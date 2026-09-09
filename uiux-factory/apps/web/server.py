"""apps/web/server.py — Lightweight static server cho UIUX Factory Workbench Console.

- Phục vụ apps/web/ ở cổng UIUX_CONSOLE_PORT (mặc định 5173)
- Forward /run, /intelligence, /jobs/<id>, /jobs/<id>/artifacts/<file>,
  /health, /latest, /preview/<project>/ tới bridge (mặc định 127.0.0.1:8788)
- Vì cầu nối reverse nên tránh phải bật CORS cho frontend; đơn giản, đáng tin cậy.

Cách dùng:

    .venv\\Scripts\\python.exe -u apps\\web\\server.py

Sau đó mở http://127.0.0.1:5173/
"""
from __future__ import annotations

import io
import json
import os
import sys
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HOST = os.environ.get("UIUX_CONSOLE_HOST", "127.0.0.1")
PORT = int(os.environ.get("UIUX_CONSOLE_PORT", "5173"))
BRIDGE = os.environ.get("UIUX_BRIDGE_URL", "http://127.0.0.1:8788")


# Endpoints mà console gửi tới bridge (mọi path bắt đầu bằng /api/)
API_PREFIX = "/api/"

# MIME đơn giản — an toàn cho static-only
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


class Handler(BaseHTTPRequestHandler):
    server_version = "UIUXFactoryConsole/1.0"

    def log_message(self, fmt, *args):  # noqa: A003
        sys.stdout.write("[console] " + (fmt % args) + "\n")

    # -----------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------
    def _send(self, status: int, body: bytes, content_type: str = "text/plain; charset=utf-8",
              extra_headers: dict | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        # Quan trọng: cho phép iframe preview ở origin khác được load
        self.send_header("X-Frame-Options", "ALLOWALL")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, rel_path: str) -> None:
        # Từ chối path traversal
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
            self._send(HTTPStatus.INTERNAL_SERVER_ERROR, str(error).encode("utf-8"))
            return
        self._send(HTTPStatus.OK, body, content_type)

    def _proxy_to_bridge(self, path: str) -> None:
        url = BRIDGE.rstrip("/") + "/" + path[len(API_PREFIX):]
        method = self.command
        # Đọc body cho POST/PUT
        data: bytes | None = None
        if method in {"POST", "PUT", "PATCH"}:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length > 0:
                data = self.rfile.read(length) if length <= 12_000_000 else b""
                if length > 12_000_000:
                    self._send(HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                               b'{"error":"Request too large"}',
                               "application/json; charset=utf-8")
                    return

        # Build request tới bridge
        req = urllib.request.Request(url, data=data, method=method)
        # Forward một số header cần thiết
        if data is not None and self.headers.get("Content-Type"):
            req.add_header("Content-Type", self.headers.get("Content-Type"))
        req.add_header("Accept", "application/json")
        req.add_header("X-Forwarded-For", self.client_address[0])

        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                body = resp.read()
                ct = resp.headers.get("Content-Type", "application/octet-stream")
                # Trả về đúng status code + content
                self.send_response(resp.status)
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Frame-Options", "ALLOWALL")
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as e:
            body = e.read()
            ct = e.headers.get("Content-Type", "application/json")
            self.send_response(e.code)
            self.send_header("Content-Type", ct)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        except urllib.error.URLError as e:
            payload = json.dumps({"error": f"Bridge unreachable: {e.reason}"}).encode("utf-8")
            self._send(HTTPStatus.BAD_GATEWAY, payload, "application/json; charset=utf-8")

    # -----------------------------------------------------------
    # HTTP methods
    # -----------------------------------------------------------
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
        self._send(HTTPStatus.NOT_FOUND, b'{"error":"Not Found"}', "application/json; charset=utf-8")

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
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
