"""Read-only, bounded GPU validation preflight. Does not read credential values."""

import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


def command(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=10)
        return {"exit_code": result.returncode, "stdout": result.stdout[:16000],
                "stderr": result.stderr[:2000]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"error_type": type(exc).__name__}


def main():
    packages = {}
    for name in ("torch", "transformers", "peft", "accelerate", "vllm",
                 "huggingface-hub", "fastapi", "koevd-eval"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    roots = [Path.home(), Path("/mnt/nfs5/nlp/workspace"), Path("/tmp")]
    disks = {}
    for root in roots:
        if root.is_dir():
            usage = shutil.disk_usage(root)
            disks[str(root)] = {"total_bytes": usage.total, "free_bytes": usage.free}
    homes = [Path("/mnt/nfs5/nlp/workspace/test_ethics_deploy"), Path("/opt"),
             Path("/opt/venv"), Path("/opt/conda"), Path.home()]
    children = {}
    for root in homes:
        if not root.is_dir():
            continue
        # Bounded directory inventory; never follow a recursive cache/weight tree.
        with os.scandir(root) as entries:
            names = sorted(entry.name for entry in entries)[:80]
        children[str(root)] = names
    hf_home = Path(os.getenv("HF_HOME") or
                   Path(os.getenv("XDG_CACHE_HOME") or Path.home() / ".cache") / "huggingface")
    token_file = Path(os.getenv("HF_TOKEN_PATH") or hf_home / "token")
    cache = Path(os.getenv("HF_HUB_CACHE") or
                 os.getenv("HUGGINGFACE_HUB_CACHE") or hf_home / "hub")
    cached_repos = []
    if cache.is_dir():
        with os.scandir(cache) as entries:
            cached_repos = sorted(entry.name for entry in entries
                                  if entry.name.startswith(("models--Qwen--", "models--KETI-NLP--",
                                                            "datasets--KETI-NLP--")))[:40]
    result = {
        "scope": "read_only_resource_observation_not_inference",
        "host": platform.node(), "platform": platform.platform(),
        "python": sys.version, "python_executable": sys.executable,
        "packages": packages, "disk": disks, "directory_inventory": children,
        "commands": {name: shutil.which(name) for name in
                     ("python3", "uv", "conda", "vllm", "docker", "nvidia-smi")},
        "hf_token_env_present": bool(os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")),
        "hf_token_file_present": token_file.is_file(),
        "selected_hf_cache_repositories": cached_repos,
        "gpu": command(["nvidia-smi", "--query-gpu=index,uuid,name,driver_version,memory.total,memory.used,utilization.gpu",
                        "--format=csv,noheader"]),
        "gpu_processes": command(["nvidia-smi", "--query-compute-apps=gpu_uuid,pid,process_name,used_memory",
                                  "--format=csv,noheader"]),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
