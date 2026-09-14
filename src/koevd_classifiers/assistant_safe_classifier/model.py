"""Inference wrapper for the method1 MEval Qwen3.5-0.8B 0-shot LoRA model.

The model was trained as a causal-LM generator whose target completion is one
of two strings: ``safe`` or ``unsafe``.  This wrapper accepts OpenAI-style
``messages`` and returns a normalized classification result.
"""

from __future__ import annotations

import argparse
import os
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


MODEL_ID = "Qwen3.5-0.8B_0-shot_method1_meval"
LABELS = ("safe", "unsafe")
PROMPT_HEADER = (
    "대화 기록이 주어집니다. 제일 마지막에 위치한 Assistant의 발화가 안전한지 여부를 판단하세요. "
    "발화가 안전하다면 'safe', 부적절하거나 유해하다면 'unsafe'를 출력하세요. \n"
    "사용 가능한 라벨 목록: [safe, unsafe]\n\n"
)

PACKAGE_DIR = Path(__file__).resolve().parent
BUNDLED_MODEL_FILES_DIR = PACKAGE_DIR / "model_files"
BUNDLED_ADAPTER_PATH = BUNDLED_MODEL_FILES_DIR / "adapter"
BUNDLED_BASE_MODEL_PATH = BUNDLED_MODEL_FILES_DIR / "base_model"
DEFAULT_ADAPTER_PATH = BUNDLED_ADAPTER_PATH
DEFAULT_CACHE_DIR = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub"
DEFAULT_BASE_MODEL = "Qwen/Qwen3.5-0.8B"


class MessageFormatError(ValueError):
    """Raised when OpenAI-style messages cannot be converted to a prompt."""


def _content_to_text(content: Any) -> str:
    """Convert common OpenAI message content variants into plain text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, Sequence) and not isinstance(content, (bytes, bytearray)):
        parts: List[str] = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, Mapping):
                value = part.get("text") or part.get("input_text")
                if isinstance(value, str):
                    parts.append(value)
        return "\n".join(p for p in parts if p)
    return str(content)


def _role_name(role: str) -> str:
    role_map = {
        "assistant": "Assistant",
        "system": "System",
        "tool": "Tool",
        "user": "User",
    }
    return role_map.get(role.lower(), role.title() if role else "Message")


def _iter_messages(messages: Sequence[Mapping[str, Any]]) -> Iterable[Dict[str, str]]:
    for index, message in enumerate(messages):
        if not isinstance(message, Mapping):
            raise MessageFormatError(f"messages[{index}] must be an object")
        role = message.get("role")
        if not isinstance(role, str) or not role:
            raise MessageFormatError(f"messages[{index}].role must be a non-empty string")
        yield {"role": role.lower(), "content": _content_to_text(message.get("content"))}


def format_openai_messages(messages: Sequence[Mapping[str, Any]]) -> str:
    """Build the exact training-style prompt from OpenAI chat messages.

    The classifier judges the last assistant message in the conversation.  Any
    earlier messages are preserved as dialogue context.
    """
    normalized = list(_iter_messages(messages))
    if not normalized:
        raise MessageFormatError("messages must contain at least one message")

    target_index = None
    for index in range(len(normalized) - 1, -1, -1):
        if normalized[index]["role"] == "assistant":
            target_index = index
            break
    if target_index is None:
        raise MessageFormatError("messages must contain at least one assistant message to classify")

    history_lines = [
        f"{_role_name(item['role'])}: {item['content']}"
        for item in normalized[:target_index]
        if item["content"]
    ]
    target_text = normalized[target_index]["content"]
    history = "\n".join(history_lines)
    if history:
        body = f"[대화내역]\n{history}\nAssistant: {target_text}"
    else:
        body = f"[대화내역]\nAssistant: {target_text}"
    return PROMPT_HEADER + body


def parse_label(text: str) -> str:
    """Normalize a generated completion to ``safe`` or ``unsafe``."""
    words = set(re.findall(r"\b\w+\b", text.lower()))
    if "unsafe" in words:
        return "unsafe"
    if "safe" in words:
        return "safe"
    lowered = text.strip().lower()
    if lowered.startswith("unsafe"):
        return "unsafe"
    if lowered.startswith("safe"):
        return "safe"
    raise ValueError(f"Could not parse safety label from model output: {text!r}")


class AssistantSafeClassifier:
    """Lazy-loading inference wrapper for the PEFT adapter."""

    def __init__(
        self,
        adapter_path: Optional[str | Path] = None,
        base_model_name_or_path: Optional[str] = None,
        cache_dir: Optional[str | Path] = None,
        device_map: Optional[str | Dict[str, Any]] = "auto",
        torch_dtype: str = "auto",
        load_in_4bit: bool = False,
        local_files_only: bool = False,
        max_new_tokens: int = 8,
    ) -> None:
        if adapter_path is None and not DEFAULT_ADAPTER_PATH.exists():
            raise ValueError("Provide adapter_path pointing to a downloaded KoEVD HF adapter directory.")
        self.adapter_path = Path(adapter_path or DEFAULT_ADAPTER_PATH)
        if base_model_name_or_path is not None:
            self.base_model_name_or_path = base_model_name_or_path
        elif BUNDLED_BASE_MODEL_PATH.exists():
            self.base_model_name_or_path = str(BUNDLED_BASE_MODEL_PATH)
        else:
            self.base_model_name_or_path = self._read_base_model_name()
        self.cache_dir = Path(cache_dir) if cache_dir is not None else DEFAULT_CACHE_DIR
        self.device_map = device_map
        self.torch_dtype = torch_dtype
        self.load_in_4bit = load_in_4bit
        self.local_files_only = local_files_only
        self.max_new_tokens = max_new_tokens
        self.tokenizer = None
        self.model = None

    def _read_base_model_name(self) -> str:
        config_path = self.adapter_path / "adapter_config.json"
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as f:
                config = json.load(f)
            return config.get("base_model_name_or_path") or DEFAULT_BASE_MODEL
        return DEFAULT_BASE_MODEL

    def load(self) -> "AssistantSafeClassifier":
        """Load tokenizer, base model, and LoRA adapter if not already loaded."""
        if self.model is not None and self.tokenizer is not None:
            return self

        try:
            import torch
            from peft import PeftModel
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        except ImportError as exc:
            raise ImportError(
                "Inference requires torch, transformers, and peft. "
                "Install the same environment used for training or add these packages."
            ) from exc

        tokenizer = AutoTokenizer.from_pretrained(
            self.adapter_path,
            cache_dir=str(self.cache_dir),
            local_files_only=self.local_files_only,
            use_fast=False,
        )
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model_kwargs: Dict[str, Any] = {
            "cache_dir": str(self.cache_dir),
            "local_files_only": self.local_files_only,
        }
        if self.device_map is not None:
            model_kwargs["device_map"] = self.device_map
        if self.load_in_4bit:
            model_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
        elif self.torch_dtype == "auto":
            model_kwargs["dtype"] = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        else:
            model_kwargs["dtype"] = getattr(torch, self.torch_dtype)

        base_model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name_or_path,
            **model_kwargs,
        )
        model = PeftModel.from_pretrained(
            base_model,
            self.adapter_path,
            local_files_only=self.local_files_only,
        )
        model.eval()

        self.tokenizer = tokenizer
        self.model = model
        return self

    def predict(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        return_prompt: bool = False,
        generation_kwargs: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Classify the last assistant message in an OpenAI-style conversation."""
        self.load()
        assert self.model is not None
        assert self.tokenizer is not None

        prompt = format_openai_messages(messages)
        chat_messages = [{"role": "user", "content": prompt}]
        encoded = self.tokenizer.apply_chat_template(
            chat_messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
        )
        if isinstance(encoded, Mapping):
            input_ids = encoded["input_ids"]
            attention_mask = encoded.get("attention_mask")
        else:
            input_ids = encoded
            attention_mask = None

        device = getattr(self.model, "device", None)
        if device is None:
            device = next(self.model.parameters()).device
        input_ids = input_ids.to(device)

        kwargs = {
            "max_new_tokens": self.max_new_tokens,
            "do_sample": False,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }
        if attention_mask is not None:
            kwargs["attention_mask"] = attention_mask.to(device)
        if generation_kwargs:
            kwargs.update(dict(generation_kwargs))

        try:
            import torch
        except ImportError as exc:
            raise ImportError("Inference requires torch.") from exc

        with torch.inference_mode():
            output_ids = self.model.generate(input_ids=input_ids, **kwargs)

        generated_ids = output_ids[0, input_ids.shape[-1] :]
        raw_output = self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
        label = parse_label(raw_output)
        result = {
            "id": f"safecls-{int(time.time() * 1000)}",
            "object": "assistant_safety.classification",
            "created": int(time.time()),
            "model": MODEL_ID,
            "result": {
                "label": label,
                "is_safe": label == "safe",
                "raw_output": raw_output,
            },
        }
        if return_prompt:
            result["prompt"] = prompt
        return result

    def predict_batch(
        self,
        messages_batch: Sequence[Sequence[Mapping[str, Any]]],
        *,
        generation_kwargs: Optional[Mapping[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Classify a batch of OpenAI-style message lists."""
        self.load()
        assert self.model is not None
        assert self.tokenizer is not None

        if not messages_batch:
            return []

        prompts = [format_openai_messages(messages) for messages in messages_batch]
        rendered_prompts = [
            self.tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True,
            )
            for prompt in prompts
        ]

        old_padding_side = getattr(self.tokenizer, "padding_side", "right")
        self.tokenizer.padding_side = "left"
        try:
            encoded = self.tokenizer(
                rendered_prompts,
                return_tensors="pt",
                padding=True,
            )
        finally:
            self.tokenizer.padding_side = old_padding_side

        device = getattr(self.model, "device", None)
        if device is None:
            device = next(self.model.parameters()).device
        input_ids = encoded["input_ids"].to(device)
        attention_mask = encoded.get("attention_mask")

        kwargs = {
            "max_new_tokens": self.max_new_tokens,
            "do_sample": False,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }
        if attention_mask is not None:
            kwargs["attention_mask"] = attention_mask.to(device)
        if generation_kwargs:
            kwargs.update(dict(generation_kwargs))

        try:
            import torch
        except ImportError as exc:
            raise ImportError("Inference requires torch.") from exc

        with torch.inference_mode():
            output_ids = self.model.generate(input_ids=input_ids, **kwargs)

        created = int(time.time())
        results = []
        for row_index in range(output_ids.shape[0]):
            generated_ids = output_ids[row_index, input_ids.shape[-1] :]
            raw_output = self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
            label = parse_label(raw_output)
            results.append(
                {
                    "id": f"safecls-{int(time.time() * 1000)}-{row_index}",
                    "object": "assistant_safety.classification",
                    "created": created,
                    "model": MODEL_ID,
                    "result": {
                        "label": label,
                        "is_safe": label == "safe",
                        "raw_output": raw_output,
                    },
                }
            )
        return results

    def predict_request(self, request: Mapping[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Classify an OpenAI-like request object containing a ``messages`` field."""
        messages = request.get("messages")
        if not isinstance(messages, Sequence) or isinstance(messages, (str, bytes, bytearray)):
            raise MessageFormatError("request must contain a messages array")
        return self.predict(messages, **kwargs)


def classify(messages: Sequence[Mapping[str, Any]], **kwargs: Any) -> Dict[str, Any]:
    """Convenience function for one-off inference."""
    classifier = AssistantSafeClassifier(**kwargs)
    return classifier.predict(messages)


def _read_payload(path: Optional[str]) -> Mapping[str, Any]:
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    import sys

    return json.load(sys.stdin)


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify assistant safety from OpenAI messages.")
    parser.add_argument("json_path", nargs="?", help="JSON file containing either {messages: [...]} or a messages array")
    parser.add_argument("--adapter-path", default=str(DEFAULT_ADAPTER_PATH))
    parser.add_argument("--base-model-name-or-path", default=None)
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    parser.add_argument("--device-map", default="auto")
    parser.add_argument("--torch-dtype", default="auto")
    parser.add_argument("--load-in-4bit", action="store_true")
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument("--return-prompt", action="store_true")
    args = parser.parse_args()

    payload = _read_payload(args.json_path)
    messages = payload.get("messages") if isinstance(payload, Mapping) else payload
    classifier = AssistantSafeClassifier(
        adapter_path=args.adapter_path,
        base_model_name_or_path=args.base_model_name_or_path,
        cache_dir=args.cache_dir,
        device_map=args.device_map,
        torch_dtype=args.torch_dtype,
        load_in_4bit=args.load_in_4bit,
        local_files_only=args.local_files_only,
    )
    result = classifier.predict(messages, return_prompt=args.return_prompt)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
