from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from src.LlmService.backends import MockIntentBackend, OllamaIntentBackend


def create_server(host: str = "127.0.0.1", port: int = 8011) -> ThreadingHTTPServer:
    mock_backend = MockIntentBackend()
    ollama_backend = OllamaIntentBackend()

    class Handler(BaseHTTPRequestHandler):
        def end_headers(self) -> None:  # noqa: N802
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            super().end_headers()

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(HTTPStatus.NO_CONTENT.value)
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            if parsed.path == "/health":
                self._send_json(HTTPStatus.OK, {"status": "ok"})
                return
            if parsed.path == "/":
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "service": "VibeDraw LLM service",
                        "status": "ok",
                        "endpoints": [
                            {
                                "path": "/health",
                                "method": "GET",
                                "description": "Health check.",
                            },
                            {
                                "path": "/intent/parse-initial",
                                "method": "POST",
                                "query": "mode=mock|ollama&model=<name when mode=ollama>",
                                "description": "Parse a natural-language bridge prompt into structured intent.",
                            },
                            {
                                "path": "/intent/patch-model",
                                "method": "POST",
                                "query": "mode=mock|ollama&model=<name when mode=ollama>",
                                "description": "Turn an edit request into model patches.",
                            },
                        ],
                    },
                )
                return
            if parsed.path == "/intent/parse-initial":
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "error": "This endpoint requires POST.",
                        "method": "POST",
                        "query": {
                            "mode": query.get("mode", ["mock"])[0],
                            "model": query.get("model", [""])[0],
                        },
                        "example_body": {
                            "type": "parse_initial_intent",
                            "prompt": "画一座40+70+40米跨径、桥宽7.5米的预应力连续梁桥。",
                        },
                    },
                )
                return
            if parsed.path == "/intent/patch-model":
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "error": "This endpoint requires POST.",
                        "method": "POST",
                        "query": {
                            "mode": query.get("mode", ["mock"])[0],
                            "model": query.get("model", [""])[0],
                        },
                        "example_body": {
                            "type": "patch_model",
                            "current_model": {
                                "project_id": "bridge_001",
                                "bridge": {
                                    "spans_m": [40, 70, 40],
                                    "deck_width_m": 7.5,
                                },
                            },
                            "prompt": "把中跨改成75米。",
                        },
                    },
                )
                return
            self._send_json(
                HTTPStatus.NOT_FOUND,
                {
                    "error": "Not found",
                    "hint": "Try GET / for service info or POST /intent/parse-initial.",
                },
            )

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            mode = query.get("mode", ["mock"])[0]
            model = query.get("model", [""])[0]

            try:
                payload = self._read_json_body()
                if parsed.path == "/intent/parse-initial":
                    self._handle_parse_initial(payload, mode, model)
                    return
                if parsed.path == "/intent/patch-model":
                    self._handle_patch_model(payload, mode, model)
                    return
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            except ValueError as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            except RuntimeError as exc:
                self._send_json(HTTPStatus.BAD_GATEWAY, {"error": str(exc)})

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

        def _handle_parse_initial(self, payload: dict, mode: str, model: str) -> None:
            prompt = payload.get("prompt")
            if payload.get("type") != "parse_initial_intent" or not isinstance(prompt, str) or not prompt.strip():
                raise ValueError("Invalid parse_initial_intent request.")

            if mode == "ollama":
                if not model:
                    raise ValueError("Query parameter 'model' is required when mode=ollama.")
                result = ollama_backend.parse_initial_intent(prompt, model)
            else:
                result = mock_backend.parse_initial_intent(prompt)
            self._send_json(HTTPStatus.OK, result)

        def _handle_patch_model(self, payload: dict, mode: str, model: str) -> None:
            prompt = payload.get("prompt")
            current_model = payload.get("current_model")
            if (
                payload.get("type") != "patch_model"
                or not isinstance(prompt, str)
                or not prompt.strip()
                or not isinstance(current_model, dict)
            ):
                raise ValueError("Invalid patch_model request.")

            if mode == "ollama":
                if not model:
                    raise ValueError("Query parameter 'model' is required when mode=ollama.")
                result = ollama_backend.patch_model(current_model, prompt, model)
            else:
                result = mock_backend.patch_model(current_model, prompt)
            self._send_json(HTTPStatus.OK, result)

        def _read_json_body(self) -> dict:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length) if length > 0 else b"{}"
            try:
                parsed = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError("Request body must be valid JSON.") from exc
            if not isinstance(parsed, dict):
                raise ValueError("Request body must be a JSON object.")
            return parsed

        def _send_json(self, status: HTTPStatus, payload: dict) -> None:
            encoded = json.dumps(payload, ensure_ascii=True).encode("utf-8")
            self.send_response(status.value)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

    return ThreadingHTTPServer((host, port), Handler)


def main() -> int:
    server = create_server()
    print("VibeDraw LLM service listening on http://127.0.0.1:8011")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
