from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from src.agent import WebRetrievalAgent
from src.models.schema import RetrievalRequest

ROOT = Path(__file__).resolve().parent
AGENT = WebRetrievalAgent()


class Handler(BaseHTTPRequestHandler):
    server_version = "InnerOSMatch4Demo/0.1"

    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/api/retrieve":
            self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 64_000:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "invalid_body"})
            return

        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            request = RetrievalRequest(
                query=str(payload.get("query", "")).strip(),
                seed_url=(str(payload.get("url", "")).strip() or None),
                max_hops=int(payload.get("max_hops", 5)),
            )
            response = AGENT.execute(request)
            self._json(HTTPStatus.OK, response.model_dump(mode="json"))
        except Exception as exc:
            self._json(
                HTTPStatus.BAD_REQUEST,
                {"error": type(exc).__name__, "detail": str(exc)[:240]},
            )

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self._json(HTTPStatus.OK, {"ok": True, "service": "match4-demo"})
            return

        if path == "/":
            path = "/index.html"

        target = (ROOT / path.lstrip("/")).resolve()
        if ROOT not in target.parents and target != ROOT:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        data = target.read_bytes()
        mime = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{mime}; charset=utf-8" if mime.startswith("text/") else mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt: str, *args) -> None:
        return


def main() -> None:
    host = "127.0.0.1"
    port = 8787
    print(f"InnerOS Match 4 demo: http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
