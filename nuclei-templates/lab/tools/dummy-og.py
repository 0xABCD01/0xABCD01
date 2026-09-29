#!/usr/bin/env python3
"""Minimal stand-in for an OG route: 200 + image/png for any GET/POST.

The templates only deliver the payload after a request shape answers 200 with an
image content type (that is what a real renderer does). compare-payload.sh needs
the delivery step to happen so it can capture the body with --dump-requests, so
it points the template at this instead of a plain directory server.

    python3 dummy-og.py --port 23000
"""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BODY = b"\x89PNG\r\n\x1a\n" + b"dummy-og"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _respond(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)  # drain the body so keep-alive stays sane
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(BODY)))
        self.end_headers()
        self.wfile.write(BODY)

    do_GET = do_POST = do_PUT = _respond

    def log_message(self, *args):  # keep the harness output clean
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.daemon_threads = True
    print(f"[dummy-og] {args.host}:{args.port} answers 200 image/png", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
