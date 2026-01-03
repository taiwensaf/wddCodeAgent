"""Testing utilities for generating pytest cases via LLM and executing them."""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
from typing import Optional

import os

from agent.llm_client import LLMClient
from agent.prompt_manager import PromptManager


def _build_import_setup(source_dir: pathlib.Path, module_name: str) -> str:
    """Return a stable import bootstrap inserted at top of generated tests."""
    source_dir = source_dir.resolve()
    return (
        "import sys\n"
        "import pathlib\n"
        "THIS_DIR = pathlib.Path(__file__).resolve().parent\n"
        f"SRC_DIR = pathlib.Path(r'{source_dir}').resolve()\n"
        "if str(SRC_DIR) not in sys.path:\n"
        "    sys.path.insert(0, str(SRC_DIR))\n"
        f"from {module_name} import *\n"
    )


def _parse_summary(out: str) -> dict:
    summary = {
        "collected": None,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
        "deselected": 0,
        "warnings": 0,
        "duration": None,
    }

    collected = re.search(r"collected\s+(\d+)\s+items?(?:\s*/\s*(\d+)\s+deselected)?", out)
    if collected:
        summary["collected"] = int(collected.group(1))
        if collected.group(2):
            summary["deselected"] = int(collected.group(2))

    blocks = re.findall(r"=+\s+(.+?)\s+=+", out)
    if blocks:
        last = blocks[-1]
        parts = [p.strip() for p in last.split(",")]
        for part in parts:
            matched = re.match(r"(\d+)\s+(passed|failed|error|errors|skipped|xfailed|xpassed|warnings?|deselected)", part)
            if matched:
                n = int(matched.group(1))
                key = matched.group(2)
                key = "errors" if key in ("error", "errors") else key
                key = "warnings" if key.startswith("warning") else key
                summary[key] = n
                continue
            duration = re.search(r"in\s+([0-9\.]+)s", part)
            if duration:
                summary["duration"] = float(duration.group(1))

    return summary


def generate_tests(
    source_code: str,
    filename: str,
    model_name: str = "qwen2.5-coder:7b",
    source_dir: Optional[str] = "results/generated_code",
) -> str:
    """Generate pytest code using the LLM tester prompt.

    Returns raw JSON string from the LLM (caller parses).
    """
    print("[TESTER] 生成测试用例...")
    pm = PromptManager()
    module_name = pathlib.Path(filename).stem
    source_dir_path = pathlib.Path(source_dir) if source_dir else pathlib.Path(".")
    prompt = pm.get(
        "tester",
        filename=filename,
        source_code=source_code,
        source_dir=str(source_dir_path.resolve()),
        module_name=module_name,
        import_setup=_build_import_setup(source_dir_path, module_name),
    )

    client = LLMClient(model_name=model_name, temperature=0.2, max_tokens=2048)
    return client.generate(prompt, response_format="json")


def save_and_run_tests(
    test_json: str,
    test_dir: str = "results/tests",
    source_dir: Optional[str] = None,
    default_test_filename: Optional[str] = None,
) -> dict:
    """Save LLM-produced tests and run them with pytest.

    Args:
        test_json: JSON string from the tester LLM.
        test_dir: directory to write generated tests into.
        source_dir: directory containing the source modules (added to PYTHONPATH).
    Returns:
        Dict with status, stdout/stderr, and summary.
    """
    try:
        data = json.loads(test_json)
    except json.JSONDecodeError:
        return {"status": "error", "reason": "invalid test JSON"}

    if data.get("status") != "success":
        return {"status": "error", "reason": data.get("message", "LLM returned non-success")}

    # 优先使用 LLM 返回的文件名，否则使用调用方传入的默认名，再否则按模块名约定
    test_filename = data.get("test_filename") or default_test_filename or "test_generated.py"
    test_code = data.get("test_code", "")
    if not test_code:
        return {"status": "error", "reason": "empty test code"}

    # 清理可能的 markdown 代码块标记
    test_code = test_code.strip()
    if test_code.startswith("```python"):
        test_code = test_code[len("```python"):].lstrip()
    elif test_code.startswith("```"):
        test_code = test_code[3:].lstrip()
    if test_code.endswith("```"):
        test_code = test_code[:-3].rstrip()

    tests_root = pathlib.Path(test_dir)
    tests_root.mkdir(parents=True, exist_ok=True)
    test_path = tests_root / test_filename
    test_path.write_text(test_code, encoding="utf-8")

    env = None
    if source_dir:
        env = dict(os.environ)
        src_dir = str(pathlib.Path(source_dir).resolve())
        env["PYTHONPATH"] = src_dir + os.pathsep + env.get("PYTHONPATH", "")

    try:
        result = subprocess.run(
            ["python", "-m", "pytest", test_filename, "-v"],
            cwd=tests_root,
            capture_output=True,
            text=True,
            timeout=300,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "failed",
            "reason": "timeout",
            "stdout_tail": exc.stdout or "",
            "stderr": exc.stderr or "",
        }

    stdout_tail = "\n".join((result.stdout or "").splitlines()[-40:])
    stderr_tail = "\n".join((result.stderr or "").splitlines()[-40:])
    summary = _parse_summary((result.stdout or "") + "\n" + (result.stderr or ""))

    if result.returncode == 0:
        return {
            "status": "success",
            "returncode": result.returncode,
            "stdout_tail": stdout_tail,
            "stderr": stderr_tail,
            "summary": summary,
            "test_file": str(test_path),
        }

    return {
        "status": "failed",
        "returncode": result.returncode,
        "stdout_tail": stdout_tail,
        "stderr": stderr_tail,
        "summary": summary,
        "test_file": str(test_path),
    }
