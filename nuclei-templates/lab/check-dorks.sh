#!/usr/bin/env bash
# Check that the FOFA body markers used in the template metadata really appear in
# the HTML that a Next.js 16.3.5 app serves.
#
# The template metadata advertises these markers:
#   body="opengraph-image"                  ImageResponse file-convention users
#   body="self.__next_f.push"               App Router flight payload
#   body="/api/og"                          hand-written OG routes (only when referenced)
#
# This builds a throwaway app in /tmp with an `app/opengraph-image.jsx` route,
# serves it, and greps the response - so the dorks in the README are not folklore.
#
# Usage: ./check-dorks.sh [--port 3011] [--keep]
set -uo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NODE_BIN="$LAB_DIR/.runtime/node/bin/node"
NEXT_BIN_DIR="$LAB_DIR/run/vulnerable/node_modules/.bin"
PORT=3011
KEEP=0

while [ $# -gt 0 ]; do
  case "$1" in
    --port) PORT="${2:?}"; shift 2 ;;
    --keep) KEEP=1; shift ;;
    -h|--help) sed -n '2,17p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

PASS=0; FAIL=0
ok()  { printf '  \033[1;32mPASS\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
bad() { printf '  \033[1;31mFAIL\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

[ -x "$NODE_BIN" ] || { echo "no node in .runtime - run ./setup.sh first" >&2; exit 1; }
[ -x "$NEXT_BIN_DIR/next" ] || { echo "no built vulnerable app - run ./setup.sh first" >&2; exit 1; }

# refuse to run if something already owns the port - otherwise the checks below
# could be answered by a stale server and still "pass"
owner="$(ss -ltnpH "sport = :$PORT" 2>/dev/null | grep -E '(127\.0\.0\.1|0\.0\.0\.0|\*):'"$PORT" | grep -oE 'pid=[0-9]+' | cut -d= -f2 | sort -u | tr '\n' ' ')"
if [ -n "${owner// /}" ]; then
  echo "port $PORT is already in use (pid(s): $owner) - stop it or pass --port" >&2
  exit 1
fi

APP_DIR="/tmp/cve-2026-94545-dorkcheck"
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/app"
# Turbopack refuses node_modules that point outside the project root, so reuse the
# vulnerable build's install through a symlink and build with webpack.
ln -s "$LAB_DIR/run/vulnerable/node_modules" "$APP_DIR/node_modules"

cat > "$APP_DIR/package.json" <<'JSON'
{"name":"dorkcheck","private":true,"dependencies":{"next":"16.3.5","react":"19.3.0","react-dom":"19.3.0"}}
JSON
cat > "$APP_DIR/app/layout.jsx" <<'JSX'
export const metadata = { title: 'dorkcheck' };
export default function RootLayout({ children }) { return (<html><body>{children}</body></html>); }
JSX
cat > "$APP_DIR/app/page.jsx" <<'JSX'
export default function Page() { return <main>dorkcheck</main>; }
JSX
cat > "$APP_DIR/app/opengraph-image.jsx" <<'JSX'
import { ImageResponse } from 'next/og';
export const size = { width: 1200, height: 630 };
export default function Image() { return new ImageResponse(<div style={{ fontSize: 64 }}>dorkcheck</div>, size); }
JSX

echo "[dorks] building a scratch Next.js 16.3.5 app with the opengraph-image convention"
if ! ( cd "$APP_DIR" && NEXT_TELEMETRY_DISABLED=1 PATH="$(dirname "$NODE_BIN"):$PATH" \
        ./node_modules/.bin/next build --webpack ) >"$APP_DIR/build.log" 2>&1; then
  echo "build failed - see $APP_DIR/build.log" >&2
  exit 1
fi

( cd "$APP_DIR" && NEXT_TELEMETRY_DISABLED=1 PATH="$(dirname "$NODE_BIN"):$PATH" \
    nohup setsid --fork ./node_modules/.bin/next start -H 127.0.0.1 -p "$PORT" \
    >"$APP_DIR/server.log" 2>&1 </dev/null & )
disown -a 2>/dev/null || true

deadline=$(( $(date +%s) + 30 ))
HTML=""
while [ "$(date +%s)" -lt "$deadline" ]; do
  HTML="$(curl -fsS -m 3 "http://127.0.0.1:$PORT/" 2>/dev/null || true)"
  printf '%s' "$HTML" | grep -q 'dorkcheck' && break
  HTML=""
  sleep 0.5
done
if [ -z "$HTML" ]; then
  bad "scratch app did not serve"
else
  echo
  echo "  meta tags the app emitted:"
  printf '%s' "$HTML" | tr '>' '>\n' | grep -io '<meta [^>]*og:image[^>]*>' | sed 's/^/    /' | head -3

  printf '%s' "$HTML" | grep -q 'opengraph-image' \
    && ok 'body="opengraph-image" is present in the HTML' \
    || bad 'body="opengraph-image" missing'
  printf '%s' "$HTML" | grep -q 'self.__next_f.push' \
    && ok 'body="self.__next_f.push" is present in the HTML' \
    || bad 'body="self.__next_f.push" missing'

  # the route itself must answer with an image
  meta="$(curl -sS -m 20 -o "$APP_DIR/og.png" -w '%{http_code} %{content_type} %{size_download}' \
            "http://127.0.0.1:$PORT/opengraph-image" 2>/dev/null || true)"
  set -- $meta
  case "${2:-}" in
    image/*) ok "the /opengraph-image route serves an image  (${2}, ${3:-0} bytes)" ;;
    *)       bad "the /opengraph-image route answered: ${meta:-nothing}" ;;
  esac

  # a hand-written route is only visible through whatever references it
  printf '%s' "$HTML" | grep -q '/api/og' \
    && ok 'body="/api/og" is present (this app references it)' \
    || echo '  NOTE body="/api/og" only appears when the app links the route - expected to be absent here'
fi

# stop the scratch server: next renames itself to "next-server", so kill whatever
# is listening on the port instead of matching a command line
for pid in $(ss -ltnpH "sport = :$PORT" 2>/dev/null | grep -E '(127\.0\.0\.1|0\.0\.0\.0|\*):'"$PORT" | grep -oE 'pid=[0-9]+' | cut -d= -f2 | sort -u); do
  kill "$pid" 2>/dev/null || true
done
sleep 0.5
[ "$KEEP" = "1" ] || rm -rf "$APP_DIR"

echo
echo "  summary: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
