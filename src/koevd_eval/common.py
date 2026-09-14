"""Shared JSONL and parsing utilities."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping


def read_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"Expected an object at {path}:{line_number}")
            yield value


def write_jsonl(path: str | Path, rows: Iterable[Mapping[str, Any]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row), ensure_ascii=False) + "\n")


def row_id(row: Mapping[str, Any]) -> str:
    metadata = row.get("metadata")
    metadata_id = metadata.get("source_id") if isinstance(metadata, Mapping) else None
    return str(row.get("sample_id") or row.get("source_id") or metadata_id or "")


def strip_code_fence(text: str) -> str:
    value = text.strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", value, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else value


def parse_json_object(text: str) -> dict[str, Any] | None:
    value = strip_code_fence(text)
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    for index, char in enumerate(value):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(value[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def prediction_text(row: Mapping[str, Any]) -> str:
    value = row.get("prediction")
    return value if isinstance(value, str) else ""
