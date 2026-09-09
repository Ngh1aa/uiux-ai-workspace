"""Lightweight static server for the UIUX Factory Workbench Console.

- Serves ``apps/web/`` on ``UIUX_CONSOLE_PORT`` (default 5173).
- Reverse-proxies ``/api/*`` to the local bridge (default 127.0.0.1:8788).
- Keeps the Workbench same-origin while preserving security headers returned by
  generated preview responses.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
HOST = os.environ.get("UIUX_CONSOLE_HOST", "127.0.0.1")
PORT = int(os.environ.get("UIUX_CONSOLE_PORT", "5173"))
BRIDGE = os.environ.get("UIUX_BRIDGE_URL", "http://127.0.0.1:8788")
API_PREFIX = "/api/"


def _bridge_origin() -> str:
    parsed = urlsplit(BRIDGE)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}"


BRIDGE_ORIGIN = _bridge_origin()
CONSOLE_CSP = "; ".join(
    [
        "default-src 'self'",
        "base-uri 'none'",
        "object-src 'none'",
        "form-action 'self'",
        "frame-ancestors 'none'",
        "script-src 'self'",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data:",
        "font-src 'self' data:",
        "connect-src 'self'" + (f" {BRIDGE_ORIGIN}" if BRIDGE_ORIGIN else ""),
        "frame-src 'self'" + (f" {BRIDGE_ORIGIN}" if BRIDGE_ORIGIN else ""),
    ]
)

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
}

# Only forward response headers whose semantics are safe and useful through the
# local reverse proxy. In particular, AI preview CSP must not be dropped.
PROXY_RESPONSE_HEADERS = (
    "Content-Security-Policy",
    "Content-Disposition",
)


class Handler(BaseHTTPRequestHandler):
    server_version = "UIUXFactoryConsole/1.1"

    def log_message(self, fmt, *args):  # noqa: A003
        sys.stdout.write("[console] " + (fmt % args) + "\n")

    def _send_common_security_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")

    def _send_console_security_headers(self) -> None:
        self._send_common_security_headers()
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", CONSOLE_CSP)

    def _send(
        self,
        status: int,
        body: bytes,
        content_type: str = "text/plain; charset=utf-8",
        extra_headers: dict | None = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self._send_console_security_headers()
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, rel_path: str) -> None:
        rel = rel_path.lstrip("/").replace("..", "").replace("\\", "/")
        if rel.endswith("/") or rel == "":
            rel = "index.html"

        target = (ROOT / rel).resolve()
        if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
            self._send(HTTPStatus.NOT_FOUND, b"Not Found")
            return

        content_type = MIME.get(target.suffix.lower(), "application/octet-stream")
        try:
            body = target.read_bytes()
        except OSError as error:
            self._send(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                str(error).encode("utf-8"),
            )
            return

        self._send(HTTPStatus.OK, body, content_type)

    def _write_proxy_response(self, response, body: bytes) -> None:
        content_type = response.headers.get(
            "Content-Type",
            "application/octet-stream",
        )
        self.send_response(response.status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self._send_common_security_headers()

        for header in PROXY_RESPONSE_HEADERS:
            value = response.headers.get(header)
            if value:
                self.send_header(header, value)

        self.end_headers()
        self.wfile.write(body)

    def _proxy_to_bridge(self, path: str) -> None:
        url = BRIDGE.rstrip("/") + "/" + path[len(API_PREFIX) :]
        method = self.command
        data: bytes | None = None

        if method in {"POST", "PUT", "PATCH"}:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length > 12_000_000:
                self._send(
                    HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    b'{"error":"Request too large"}',
                    "application/json; charset=utf-8",
                )
                return
            if length > 0:
                data = self.rfile.read(length)

        request = urllib.request.Request(url, data=data, method=method)
        if data is not None and self.headers.get("Content-Type"):
            request.add_header("Content-Type", self.headers.get("Content-Type"))
        request.add_header("Accept", self.headers.get("Accept", "*/*"))
        request.add_header("X-Forwarded-For", self.client_address[0])

        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                body = response.read()
                self._write_proxy_response(response, body)
        except urllib.error.HTTPError as error:
            body = error.read()
            self.send_response(error.code)
            self.send_header(
                "Content-Type",
                error.headers.get("Content-Type", "application/json"),
            )
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self._send_common_security_headers()
            for header in PROXY_RESPONSE_HEADERS:
                value = error.headers.get(header)
                if value:
                    self.send_header(header, value)
            self.end_headers()
            self.wfile.write(body)
        except urllib.error.URLError as error:
            payload = json.dumps(
                {"error": f"Bridge unreachable: {error.reason}"}
            ).encode("utf-8")
            self._send(
                HTTPStatus.BAD_GATEWAY,
                payload,
                "application/json; charset=utf-8",
            )

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path.startswith(API_PREFIX):
            self._proxy_to_bridge(path)
            return
        self._serve_file(path)

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path.startswith(API_PREFIX):
            self._proxy_to_bridge(path)
            return
        self._send(
            HTTPStatus.NOT_FOUND,
            b'{"error":"Not Found"}',
            "application/json; charset=utf-8",
        )

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self._send_console_security_headers()
        self.end_headers()


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print()
    print("=" * 72)
    print("UIUX FACTORY - WORKBENCH CONSOLE")
    print("=" * 72)
    print(f"[Console] http://{HOST}:{PORT}")
    print(f"[Bridge]  {BRIDGE}")
    print(f"[Static]  {ROOT}")
    print("=" * 72)
    print("Open http://localhost:5173/ in your browser.")
    print("=" * 72)
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
