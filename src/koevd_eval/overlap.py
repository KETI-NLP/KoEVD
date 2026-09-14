"""Matched Task 3/5 counting formulas preserved from the paper verification."""
from collections import Counter, defaultdict

def norm_model(value):
    value = str(value or "").strip().lower()
    aliases = {
        "apertus-8b-instruct-vllm": "apertus-8b-instruct-vllm",
        "gemma-4-e4b-it-vllm": "gemma-4-e4b-it-vllm",
        "ministral-3-8b-reasoning-vllm": "ministral-3-8b-reasoning-vllm",
        "olmo-3-7b-think-vllm": "olmo-3-7b-think-vllm",
        "qwen3.5-9b-vllm": "qwen3.5-9b-vllm",
        "qwen3.6-27b-fp8-vllm": "qwen3.6-27b-fp8-vllm",
        "claude-4.6-sonnet": "claude-4.6-sonnet",
        "claude-haiku-4-5": "claude-haiku-4-5",
        "gemini-3.1-flash-lite-preview": "gemini-3.1-flash-lite-preview",
        "gemini-3.1-pro-preview": "gemini-3.1-pro-preview",
        "gpt-5.4": "gpt-5.4",
        "gpt-5.4-nano": "gpt-5.4-nano",
    }
    return aliases.get(value, value)


def source_id(row):
    metadata = row.get("metadata") or {}
    if metadata.get("source_id"):
        return str(metadata["source_id"])
    source = row.get("source") or {}
    if source.get("source_id"):
        return str(source["source_id"])
    sample_id = str(row.get("sample_id") or "")
    return sample_id.split(":", 1)[0]


def table_for(rows, task3):
    counts = defaultdict(lambda: Counter())
    matched_rows = []
    for row in rows:
        task3_key = (row["source_id"], row["model"])
        if task3_key not in task3:
            continue
        t3_safe = task3[task3_key]
        if not row["parsed_ok"]:
            t5_outcome = "unparsed"
        elif row["unsafe_call"]:
            t5_outcome = "unsafe"
        else:
            t5_outcome = "nonunsafe"
        group = row["variant"]
        for name in (group, "all"):
            counts[name][(t3_safe, t5_outcome)] += 1
        matched_rows.append({**row, "task3_safe": t3_safe})
    return counts, matched_rows


def pct(num, den):
    return None if not den else 100.0 * num / den


def summarize_group(counter):
    a = counter[(True, "nonunsafe")]
    b = counter[(True, "unsafe")]
    u1 = counter[(True, "unparsed")]
    c = counter[(False, "nonunsafe")]
    d = counter[(False, "unsafe")]
    u0 = counter[(False, "unparsed")]
    total = a + b + u1 + c + d + u0
    parsed_total = a + b + c + d
    return {
        "task3_safe_task5_nonunsafe_parsed": a,
        "task3_safe_task5_unsafe": b,
        "task3_safe_task5_unparsed": u1,
        "task3_unsafe_task5_nonunsafe_parsed": c,
        "task3_unsafe_task5_unsafe": d,
        "task3_unsafe_task5_unparsed": u0,
        "matched_total": total,
        "parsed_total": parsed_total,
        "unparsed_total": u1 + u0,
        "task3_safe_total": a + b + u1,
        "task3_unsafe_total": c + d + u0,
        "task5_unsafe_total": b + d,
        "p_task5_unsafe_given_task3_safe_all_matched_pct": pct(b, a + b + u1),
        "p_task5_unsafe_given_task3_unsafe_all_matched_pct": pct(d, c + d + u0),
        "p_task5_unsafe_given_task3_safe_parsed_pct": pct(b, a + b),
        "p_task5_unsafe_given_task3_unsafe_parsed_pct": pct(d, c + d),
        "p_task3_safe_given_task5_unsafe_pct": pct(b, b + d),
        "task5_unsafe_rate_all_matched_pct": pct(b + d, total),
        "task5_unsafe_rate_parsed_pct": pct(b + d, parsed_total),
        "task5_parse_rate_pct": pct(parsed_total, total),
    }


