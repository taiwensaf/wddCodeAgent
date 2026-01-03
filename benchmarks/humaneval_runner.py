"""Run official HumanEval tests on agent-generated code.

This script expects a JSONL file where each line contains at least
```
{"task_id": "HumanEval/0", "completion": "<python code>"}
```
`completion_id` is optional. Results are written as a JSON report.
"""
from __future__ import annotations

import json
import pathlib
from typing import Dict, List, Optional, Set

import typer
from human_eval.data import read_problems
from human_eval.evaluation import evaluate_functional_correctness

app = typer.Typer(help="Run HumanEval official functional-correctness tests.")


def _load_samples(
    samples_path: pathlib.Path,
    problems: Dict[str, dict],
    max_tasks: Optional[int],
) -> List[dict]:
    """Load and sanitize completions from a JSONL file."""
    samples: List[dict] = []
    seen_tasks: Set[str] = set()

    if not samples_path.exists():
        raise FileNotFoundError(f"Samples file not found: {samples_path}")

    with samples_path.open("r", encoding="utf-8") as handle:
        for idx, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                typer.echo(f"[WARN] Skip line {idx}: invalid JSON")
                continue

            task_id = row.get("task_id")
            completion = row.get("completion")
            if not task_id or completion is None:
                typer.echo(f"[WARN] Skip line {idx}: missing task_id or completion")
                continue
            if task_id not in problems:
                typer.echo(f"[WARN] Skip line {idx}: {task_id} not in HumanEval")
                continue

            samples.append(
                {
                    "task_id": task_id,
                    "completion_id": row.get("completion_id", f"agent-{len(samples)}"),
                    "completion": completion,
                }
            )
            seen_tasks.add(task_id)

            if max_tasks is not None and len(seen_tasks) >= max_tasks:
                break

    return samples


def _save_report(output_path: pathlib.Path, payload: dict) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _run_evaluation(
    samples: pathlib.Path,
    output: pathlib.Path,
    k: List[int],
    n_workers: int,
    timeout: float,
    max_tasks: Optional[int],
) -> None:
    problems = read_problems()
    samples_list = _load_samples(samples, problems, max_tasks)
    if not samples_list:
        typer.echo("[ERROR] No valid samples found; nothing to evaluate.")
        raise typer.Exit(code=1)

    k_values = sorted(set(k))
    typer.echo(
        f"[INFO] Evaluating {len(samples_list)} samples across {len(set(s['task_id'] for s in samples_list))} tasks..."
    )

    eval_result = evaluate_functional_correctness(
        samples=samples_list, k=k_values, n_workers=n_workers, timeout=timeout
    )

    report = {
        "summary": {
            "num_samples": len(samples_list),
            "num_tasks": len({s["task_id"] for s in samples_list}),
            "k": k_values,
            "timeout": timeout,
            "n_workers": n_workers,
        },
        "pass_at_k": eval_result.get("pass@k", {}),
        "results": eval_result.get("results", {}),
    }

    _save_report(output, report)
    typer.echo(f"[DONE] Report written to {output}")


@app.command()
def evaluate(
    samples: pathlib.Path = typer.Option(
        pathlib.Path("results/humaneval_samples.jsonl"),
        help="Path to JSONL with task_id/completion entries.",
    ),
    output: pathlib.Path = typer.Option(
        pathlib.Path("results/humaneval_report.json"),
        help="Where to save the evaluation report.",
    ),
    k: List[int] = typer.Option(
        [1],
        "--k",
        help="pass@k values to compute; repeat flag for multiple values (e.g., --k 1 --k 10).",
    ),
    n_workers: int = typer.Option(4, help="Parallel workers for executing tests."),
    timeout: float = typer.Option(3.0, help="Timeout (seconds) per test case."),
    max_tasks: Optional[int] = typer.Option(
        None, help="Optional cap on how many unique tasks to evaluate."
    ),
) -> None:
    """Evaluate completions against the official HumanEval tests."""
    _run_evaluation(samples, output, k, n_workers, timeout, max_tasks)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    samples: pathlib.Path = typer.Option(
        pathlib.Path("results/humaneval_samples.jsonl"),
        help="Path to JSONL with task_id/completion entries.",
    ),
    output: pathlib.Path = typer.Option(
        pathlib.Path("results/humaneval_report.json"),
        help="Where to save the evaluation report.",
    ),
    k: List[int] = typer.Option(
        [1],
        "--k",
        help="pass@k values to compute; repeat flag for multiple values (e.g., --k 1 --k 10).",
    ),
    n_workers: int = typer.Option(4, help="Parallel workers for executing tests."),
    timeout: float = typer.Option(3.0, help="Timeout (seconds) per test case."),
    max_tasks: Optional[int] = typer.Option(
        None, help="Optional cap on how many unique tasks to evaluate."
    ),
) -> None:
    """Allow calling without subcommand; forwards to evaluate when no command is given."""
    if ctx.invoked_subcommand is not None:
        return
    _run_evaluation(samples, output, k, n_workers, timeout, max_tasks)


if __name__ == "__main__":
    app()
