"""Run model-facing KoEVD JSONL through an OpenAI-compatible endpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Mapping

from .common import read_jsonl, row_id, write_jsonl


def endpoint(base_url: str) -> str:
    value = base_url.rstrip("/")
    return value if value.endswith("/chat/completions") else value + "/chat/completions"


def call_api(url: str, api_key: str, model: str, messages: list[Mapping[str, Any]], temperature: float, max_tokens: int, timeout: float) -> str:
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    content = body["choices"][0]["message"].get("content", "")
    if isinstance(content, list):
        content = "".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
    return str(content or "")


def successful_ids(output_path: Path) -> set[str]:
    if not output_path.exists():
        return set()
    return {row_id(row) for row in read_jsonl(output_path) if row.get("api_status") == "ok"}


def unique_rows(rows):
    indexed = {}
    for row in rows:
        key = row_id(row)
        if not key or key in indexed:
            raise ValueError(f"Input/output requires unique nonempty sample IDs: {key!r}")
        indexed[key] = row
    return indexed


def input_digest(row):
    return hashlib.sha256(json.dumps(row, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def run_rows(rows, output, config, *, api_key="", timeout=120, retries=2, retry_delay=2, resume=False):
    """Checkpoint one current result per input ID; failed retries replace rows."""
    inputs = unique_rows(rows)
    previous = unique_rows(read_jsonl(output)) if resume and output.exists() else {}
    for key, result in previous.items():
        if key not in inputs or result.get("run_config") != config or result.get("input_sha256") != input_digest(inputs[key]):
            raise ValueError("Resume requires the same input rows, model, endpoint and decoding settings; use a new output file.")
    results = dict(previous)
    for key, row in inputs.items():
        if key in results and results[key].get("api_status") == "ok":
            continue
        result = dict(row)
        result.update(prediction="", api_status="error", api_error=None,
                      evaluated_model=config["model"], run_config=config, input_sha256=input_digest(row))
        for attempt in range(retries + 1):
            try:
                result["prediction"] = call_api(config["endpoint"], api_key, config["model"], row["messages"], config["temperature"], config["max_tokens"], timeout)
                result["api_status"] = "ok"
                result["api_error"] = None
                break
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as exc:
                result["api_error"] = f"{type(exc).__name__}: {exc}"
                if attempt < retries:
                    time.sleep(retry_delay * (attempt + 1))
        results[key] = result
        temporary = output.with_suffix(output.suffix + ".tmp")
        write_jsonl(temporary, (results[k] for k in inputs if k in results))
        os.replace(temporary, output)
    if not inputs:
        write_jsonl(output, [])
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--retry-delay", type=float, default=2.0)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    api_key = os.environ.get(args.api_key_env, "")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = list(read_jsonl(args.input))[args.start :]
    if args.limit is not None:
        rows = rows[: args.limit]
    if args.retries < 0 or args.start < 0 or (args.limit is not None and args.limit < 0):
        parser.error("retries, start and limit must be nonnegative")
    config = {"endpoint": endpoint(args.base_url), "model": args.model,
              "temperature": args.temperature, "max_tokens": args.max_tokens}
    run_rows(rows, output, config, api_key=api_key, timeout=args.timeout,
             retries=args.retries, retry_delay=args.retry_delay, resume=args.resume)


if __name__ == "__main__":
    main()
