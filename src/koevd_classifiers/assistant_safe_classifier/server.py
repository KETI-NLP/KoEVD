"""OpenAI-compatible HTTP server for the bundled safety classifier."""

from __future__ import annotations

import argparse
import threading
import time
from typing import Any, Dict, Mapping, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

try:
    from .model import AssistantSafeClassifier, MODEL_ID, MessageFormatError
except ImportError:  # Allows `python server.py` from this directory.
    from model import AssistantSafeClassifier, MODEL_ID, MessageFormatError


def _error_response(message: str, status_code: int = 400, code: Optional[str] = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": message,
                "type": "invalid_request_error",
                "param": None,
                "code": code,
            }
        },
    )


def _usage(prompt_tokens: int = 0, completion_tokens: int = 1) -> Dict[str, int]:
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
    }


def _chat_completion_response(
    *,
    request_model: str,
    safety_result: Mapping[str, Any],
) -> Dict[str, Any]:
    label = safety_result["result"]["label"]
    created = int(time.time())
    return {
        "id": safety_result["id"].replace("safecls-", "chatcmpl-safecls-"),
        "object": "chat.completion",
        "created": created,
        "model": request_model or MODEL_ID,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": label,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": _usage(),
        "safety_result": safety_result["result"],
    }


def build_app(classifier: Optional[AssistantSafeClassifier] = None) -> FastAPI:
    app = FastAPI(title="Assistant Safety Classifier", version="1.0.0")
    app.state.classifier = classifier or AssistantSafeClassifier(local_files_only=True)
    app.state.classifier_lock = threading.Lock()

    @app.get("/health")
    def health() -> Dict[str, Any]:
        loaded = app.state.classifier.model is not None
        return {"status": "ok", "model": MODEL_ID, "loaded": loaded}

    @app.get("/v1/models")
    def list_models() -> Dict[str, Any]:
        return {
            "object": "list",
            "data": [
                {
                    "id": MODEL_ID,
                    "object": "model",
                    "created": 0,
                    "owned_by": "assistant_safe_classification",
                }
            ],
        }

    @app.post("/v1/chat/completions")
    async def chat_completions(request: Request) -> JSONResponse:
        try:
            payload = await request.json()
        except Exception:
            return _error_response("Request body must be valid JSON")

        if not isinstance(payload, Mapping):
            return _error_response("Request body must be a JSON object")
        if payload.get("stream"):
            return _error_response("stream=true is not supported by this classifier", code="stream_not_supported")

        messages = payload.get("messages")
        if messages is None:
            return _error_response("Missing required field: messages")

        generation_kwargs: Dict[str, Any] = {}
        if "max_tokens" in payload:
            generation_kwargs["max_new_tokens"] = payload["max_tokens"]
        if "temperature" in payload:
            generation_kwargs["do_sample"] = bool(payload["temperature"])
            generation_kwargs["temperature"] = payload["temperature"]

        try:
            with app.state.classifier_lock:
                result = app.state.classifier.predict(messages, generation_kwargs=generation_kwargs)
        except MessageFormatError as exc:
            return _error_response(str(exc))
        except ValueError as exc:
            return _error_response(str(exc), status_code=422)
        except Exception as exc:
            return _error_response(f"Inference failed: {exc}", status_code=500, code="inference_failed")

        response = _chat_completion_response(
            request_model=str(payload.get("model") or MODEL_ID),
            safety_result=result,
        )
        return JSONResponse(response)

    @app.post("/v1/assistant-safety/classifications")
    async def classifications(request: Request) -> JSONResponse:
        try:
            payload = await request.json()
        except Exception:
            return _error_response("Request body must be valid JSON")

        if not isinstance(payload, Mapping):
            return _error_response("Request body must be a JSON object")
        messages = payload.get("messages")
        if messages is None:
            return _error_response("Missing required field: messages")

        try:
            with app.state.classifier_lock:
                result = app.state.classifier.predict(messages)
        except MessageFormatError as exc:
            return _error_response(str(exc))
        except ValueError as exc:
            return _error_response(str(exc), status_code=422)
        except Exception as exc:
            return _error_response(f"Inference failed: {exc}", status_code=500, code="inference_failed")

        return JSONResponse(result)

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the safety classifier with OpenAI-compatible REST APIs.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--adapter-path", default=None)
    parser.add_argument("--base-model-name-or-path", default=None)
    parser.add_argument("--cache-dir", default=None)
    parser.add_argument("--device-map", default="auto")
    parser.add_argument("--torch-dtype", default="auto")
    parser.add_argument("--load-in-4bit", action="store_true")
    parser.add_argument("--local-files-only", action="store_true", default=True)
    parser.add_argument("--allow-remote-files", action="store_false", dest="local_files_only")
    parser.add_argument("--preload", action="store_true", help="Load model before accepting requests")
    args = parser.parse_args()

    classifier = AssistantSafeClassifier(
        adapter_path=args.adapter_path,
        base_model_name_or_path=args.base_model_name_or_path,
        cache_dir=args.cache_dir,
        device_map=args.device_map,
        torch_dtype=args.torch_dtype,
        load_in_4bit=args.load_in_4bit,
        local_files_only=args.local_files_only,
    )
    if args.preload:
        classifier.load()

    app = build_app(classifier)

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
