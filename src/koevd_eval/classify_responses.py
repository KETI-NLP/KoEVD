"""Apply a released KoEVD measurement classifier to Task 3 responses."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Iterable

from .common import prediction_text, read_jsonl, write_jsonl


def chunks(values: list[Any], size: int) -> Iterable[list[Any]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def build_messages(row: dict[str, Any]) -> list[dict[str, str]]:
    messages = [dict(message) for message in row.get("messages", [])]
    return messages + [{"role": "assistant", "content": prediction_text(row)}]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=int, choices=(3, 4), required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--base-model-name-or-path")
    parser.add_argument("--local-files-only", action="store_true")
    adapter = parser.add_mutually_exclusive_group(required=True)
    adapter.add_argument("--adapter-path", help="Local HF adapter directory")
    adapter.add_argument("--adapter-repo", help="HF model repo ID")
    parser.add_argument("--revision", help="Required with --adapter-repo")
    args = parser.parse_args()
    if args.adapter_repo:
        from .hub import download
        if not args.revision:
            parser.error("--revision is required with --adapter-repo")
        args.adapter_path = str(download(args.adapter_repo, args.revision, local_files_only=args.local_files_only))
    if not (Path(args.adapter_path) / "adapter_config.json").is_file():
        parser.error("--adapter-path must contain adapter_config.json")
    if args.task == 3:
        from koevd_classifiers.assistant_safe_classifier import AssistantSafeClassifier as Classifier
    else:
        from koevd_classifiers.response_strategy_classifier import StrategyClassifier as Classifier
    kwargs: dict[str, Any] = {"local_files_only": args.local_files_only, "adapter_path": args.adapter_path}
    if args.base_model_name_or_path:
        kwargs["base_model_name_or_path"] = args.base_model_name_or_path
    classifier = Classifier(**kwargs)
    rows = list(read_jsonl(args.input))
    output_rows: list[dict[str, Any]] = []
    for batch in chunks(rows, max(1, args.batch_size)):
        eligible_indexes = [index for index, row in enumerate(batch) if row.get("api_status") == "ok" and prediction_text(row).strip()]
        measured = classifier.predict_batch([build_messages(batch[index]) for index in eligible_indexes]) if eligible_indexes else []
        if len(measured) != len(eligible_indexes):
            raise RuntimeError("Classifier returned a different number of results than eligible inputs")
        measured_by_index = {index: value["result"] for index, value in zip(eligible_indexes, measured)}
        for index, row in enumerate(batch):
            result = dict(row)
            result["measurement"] = measured_by_index.get(index)
            result["measurement_error"] = None if index in measured_by_index else "missing_or_failed_generation"
            output_rows.append(result)
    write_jsonl(args.output, output_rows)


if __name__ == "__main__":
    main()
