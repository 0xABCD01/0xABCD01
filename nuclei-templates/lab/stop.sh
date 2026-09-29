#!/usr/bin/env bash
# Stop everything start.sh brought up.
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIDS="$LAB_DIR/pids"

log() { printf '\033[1;34m[stop]\033[0m %s\n' "$*"; }

for name in vulnerable patched oob; do
  pid_file="$PIDS/$name.pid"
  [ -f "$pid_file" ] || continue
  pid="$(cat "$pid_file")"
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    log "stopped $name (pid $pid)"
  else
    log "$name was not running"
  fi
  rm -f "$pid_file"
done

# fallback: something still bound to a lab port (an earlier run, or a worker)
# gets cleaned up so the next start does not trip over "address already in use"
for port in "${VULN_PORT:-3000}" "${PATCHED_PORT:-3001}" "${OOB_PORT:-4444}"; do
  pids="$(ss -ltnp 2>/dev/null | awk -v p=":$port" '$4 ~ p {print $0}' | grep -o 'pid=[0-9]*' | cut -d= -f2 | sort -u)"
  for pid in $pids; do
    kill "$pid" 2>/dev/null && log "freed :$port (killed leftover pid $pid)"
  done
done

# next start leaves no children behind, but a killed worker can leave a socket
# in TIME_WAIT; report anything still bound so the next start is not a surprise.
for port in "${VULN_PORT:-3000}" "${PATCHED_PORT:-3001}" "${OOB_PORT:-4444}"; do
  if command -v ss >/dev/null 2>&1 && ss -ltn 2>/dev/null | grep -q ":$port "; then
    log "note: something is still listening on :$port"
  fi
done
