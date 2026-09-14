"""Scoring CLI; old function imports remain supported."""
import argparse
import json
from pathlib import Path
from .common import read_jsonl
from .parsers import parse_task1, parse_task2, parse_task5
from .metrics import ratio, score_task1, score_task2, score_task3, score_task4, score_task5

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=int, choices=(1, 2, 3, 4, 5), required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    rows = list(read_jsonl(args.input))
    result = {1: score_task1, 2: score_task2, 3: score_task3, 4: score_task4, 5: score_task5}[args.task](rows)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
