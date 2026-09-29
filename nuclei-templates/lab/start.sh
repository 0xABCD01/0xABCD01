#!/usr/bin/env bash
# Start the lab components and wait until they answer.
#
#   ./start.sh                       vulnerable :3000, patched :3001, OOB :4444
#   ./start.sh vulnerable            just the vulnerable build
#   ./start.sh --restart vulnerable  stop then start one component
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NODE_BIN="$LAB_DIR/.runtime/node/bin/node"
LOGS="$LAB_DIR/logs"
PIDS="$LAB_DIR/pids"
OOB_PORT="${OOB_PORT:-4444}"
VULN_PORT="${VULN_PORT:-3000}"
PATCHED_PORT="${PATCHED_PORT:-3001}"

log() { printf '\033[1;34m[start]\033[0m %s\n' "$*"; }
err() { printf '\033[1;31m[start] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

[ -x "$NODE_BIN" ] || err "node runtime missing - run ./setup.sh first"
mkdir -p "$LOGS" "$PIDS"

is_running() {
  local name="$1"
  [ -f "$PIDS/$name.pid" ] || return 1
  kill -0 "$(cat "$PIDS/$name.pid")" 2>/dev/null
}

stop_one() {
  local name="$1"
  if is_running "$name"; then
    kill "$(cat "$PIDS/$name.pid")" 2>/dev/null || true
    for _ in 1 2 3 4 5 6 7 8 9 10; do
      is_running "$name" || break
      sleep 0.3
    done
  fi
  rm -f "$PIDS/$name.pid"
}

wait_http() { # url, label, seconds
  local url="$1" label="$2" deadline=$(( $(date +%s) + ${3:-40} ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    if curl -fsS -m 3 -o /dev/null "$url" 2>/dev/null; then
      log "$label ready"
      return 0
    fi
    sleep 0.5
  done
  err "$label did not answer on $url (see $LOGS/${label% *}.log)"
}

start_app() { # variant, port
  local variant="$1" port="$2"
  local dir="$LAB_DIR/run/$variant"
  [ -d "$dir/node_modules" ] || err "run/$variant missing - run ./setup.sh first"

  if is_running "$variant"; then
    log "$variant already running (pid $(cat "$PIDS/$variant.pid"))"
    return 0
  fi

  # the pid file is written by the child itself (bash execs into node, so the
  # recorded pid is the server process, not a wrapper subshell)
  # setsid --fork gives the server its own session so start.sh can exit without
  # waiting for it; the child records its own pid (bash execs into node).
  ( cd "$dir" \
    && NEXT_TELEMETRY_DISABLED=1 PATH="$LAB_DIR/.runtime/node/bin:$PATH" \
       nohup setsid --fork bash -c 'echo $$ > "$1"; shift; exec "$@"' _ "$PIDS/$variant.pid" \
         "$NODE_BIN" ./node_modules/next/dist/bin/next start -H 0.0.0.0 -p "$port" \
       >"$LOGS/$variant.log" 2>&1 </dev/null & )
  disown -a 2>/dev/null || true

  wait_http "http://127.0.0.1:$port/api/lab-info" "$variant (:$port)"
}

start_oob() {
  if is_running oob; then
    log "OOB listener already running (pid $(cat "$PIDS/oob.pid"))"
    return 0
  fi
  : >"$LAB_DIR/oob-hits.log"
  ( cd "$LAB_DIR" \
    && nohup setsid --fork python3 ./oob-listener.py --host 0.0.0.0 --port "$OOB_PORT" \
         --log "$LAB_DIR/oob-hits.log" --pidfile "$PIDS/oob.pid" \
       >"$LOGS/oob.log" 2>&1 </dev/null & )
  disown -a 2>/dev/null || true
  # the listener writes its own pid file; give it a moment
  for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
    [ -s "$PIDS/oob.pid" ] && break
    sleep 0.25
  done
  kill -0 "$(cat "$PIDS/oob.pid")" 2>/dev/null || err "OOB listener failed to start (see $LOGS/oob.log)"
  log "OOB listener ready on 0.0.0.0:$OOB_PORT"
}

restart_one() {
  local name="$1"
  stop_one "$name"
  rm -f "$PIDS/$name.pid"
  case "$name" in
    vulnerable) start_app vulnerable "$VULN_PORT" ;;
    patched)    start_app patched "$PATCHED_PORT" ;;
    oob)        start_oob ;;
    *)          err "unknown component '$name'" ;;
  esac
}

main() {
  if [ "${1:-}" = "--restart" ]; then
    restart_one "${2:?usage: --restart <vulnerable|patched|oob>}"
    return 0
  fi
  case "${1:-all}" in
    vulnerable) start_app vulnerable "$VULN_PORT" ;;
    patched)    start_app patched "$PATCHED_PORT" ;;
    oob)        start_oob ;;
    all)
      start_oob
      start_app vulnerable "$VULN_PORT"
      start_app patched "$PATCHED_PORT"
      ;;
    *) err "unknown component '${1}'" ;;
  esac
}

main "$@"
