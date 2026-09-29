#!/usr/bin/env python3
"""Minimal TLS terminator for the lab: accepts HTTPS and forwards to an HTTP backend.

`next start` speaks plain HTTP, so a target that "listens on 443" is really
TLS-in-front-of-HTTP. This is the smallest useful stand-in for that front end, so
the templates can be exercised against an https:// target.

    python3 tls-proxy.py --port 443 --backend 127.0.0.1:8080 --cert cert.pem --key key.pem

Ports below 1024 need root (or CAP_NET_BIND_SERVICE).
"""
import argparse
import socket
import ssl
import sys
import threading


def pump(src, dst):
    try:
        while True:
            chunk = src.recv(65536)
            if not chunk:
                break
            dst.sendall(chunk)
    except OSError:
        pass
    finally:
        for sock in (src, dst):
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


def handle(conn, ctx, backend):
    try:
        tls = ctx.wrap_socket(conn, server_side=True)
    except (ssl.SSLError, OSError):
        conn.close()
        return
    try:
        upstream = socket.create_connection(backend, timeout=10)
        upstream.settimeout(None)
    except OSError:
        tls.close()
        return
    sideways = threading.Thread(target=pump, args=(tls, upstream), daemon=True)
    sideways.start()
    pump(upstream, tls)
    sideways.join(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, required=True, help="TLS listen port")
    parser.add_argument("--backend", required=True, help="host:port to forward to")
    parser.add_argument("--cert", required=True, help="PEM certificate")
    parser.add_argument("--key", required=True, help="PEM private key")
    parser.add_argument("--host", default="0.0.0.0", help="bind address (default 0.0.0.0)")
    args = parser.parse_args()

    host, _, port = args.backend.rpartition(":")
    backend = (host or "127.0.0.1", int(port))

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(args.cert, args.key)

    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        listener.bind((args.host, args.port))
    except PermissionError:
        sys.exit(f"cannot bind {args.host}:{args.port}: permission denied (need root or CAP_NET_BIND_SERVICE)")
    listener.listen(128)
    print(f"[tls] {args.host}:{args.port} -> {backend[0]}:{backend[1]}", flush=True)

    while True:
        conn, _ = listener.accept()
        threading.Thread(target=handle, args=(conn, ctx, backend), daemon=True).start()


if __name__ == "__main__":
    main()
