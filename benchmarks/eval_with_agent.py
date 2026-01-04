"""
使用 Agent 在 HumanEval 上进行评估
流程：HumanEval 问题 → Agent 生成代码 → 官方测试 → 统计通过率
"""
import json
import pathlib
from typing import Optional, List
import sys

import typer
from human_eval.data import read_problems, write_jsonl
from human_eval.evaluation import evaluate_functional_correctness
from human_eval.execution import check_correctness

# 添加项目路径
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from agent.agent_loop import solve
from agent.llm_client import LLMClient
from benchmarks.humaneval_runner import _run_evaluation

app = typer.Typer(help="Evaluate Agent on HumanEval with standard tests.")


def _extract_python_code(text: str) -> str:
    """Extract the Python code block from LLM output, stripping prose/markdown."""
    text = text.strip()

    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 2:
            code = parts[1]
            if code.startswith("python"):
                code = code[len("python"):].lstrip()
            return code.strip()

    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith(("def ", "class ", "import ", "from ")):
            return "\n".join(lines[i:]).strip()

    return text


def _generate_solutions(
    num_problems: Optional[int] = None,
    num_samples_per_task: int = 1,
    model_name: str = "qwen2.5-coder:7b",
    output_file: pathlib.Path = pathlib.Path("results/humaneval_samples.jsonl"),
) -> None:
    """
    使用 Agent 为 HumanEval 问题生成代码
    
    Args:
        num_problems: 评估的问题数（None 表示全部 164 个）
        num_samples_per_task: 每个问题生成的代码版本数（用于 pass@k）
        model_name: 使用的模型
        output_file: 输出的 JSONL 文件
    """
    problems = read_problems()
    problem_ids = sorted(problems.keys())
    
    if num_problems:
        problem_ids = problem_ids[:num_problems]
    
    typer.echo(f"🎯 开始为 {len(problem_ids)} 个 HumanEval 问题生成代码...")
    typer.echo(f"   • 每个问题生成 {num_samples_per_task} 个版本（用于 pass@{num_samples_per_task}）")
    typer.echo(f"   • 模型: {model_name}")
    typer.echo(f"   • 输出: {output_file}\n")
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    completed = 0
    skipped = 0
    
    with output_file.open("w", encoding="utf-8") as f:
        for idx, task_id in enumerate(problem_ids, 1):
            problem = problems[task_id]
            
            typer.echo(f"[{idx}/{len(problem_ids)}] {task_id}: {problem.get('entry_point', 'unknown')}")
            
            # 构建 prompt：问题描述 + 函数签名
            prompt = f"""{problem['prompt']}"""
            
            try:
                # 为每个问题生成多个版本
                for sample_idx in range(num_samples_per_task):
                    # 提高温度以获得多样化的代码
                    client = LLMClient(
                        model_name=model_name,
                        temperature=0.5 + (sample_idx * 0.2),  # 逐渐增加温度
                        max_tokens=2048
                    )
                    
                    completion_raw = client.generate(prompt, response_format="text")
                    completion = _extract_python_code(completion_raw)
                    
                    # 写入 JSONL
                    record = {
                        "task_id": task_id,
                        "completion": completion,
                        "completion_id": f"agent-{sample_idx}",
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                
                completed += 1
                typer.echo(f"   ✓ 成功生成 {num_samples_per_task} 个版本\n")
                
            except Exception as e:
                skipped += 1
                typer.echo(f"   ✗ 生成失败: {str(e)}\n")
    
    typer.echo(f"\n{'='*60}")
    typer.echo(f"📝 生成完成:")
    typer.echo(f"   • 成功: {completed}/{len(problem_ids)} 个问题")
    typer.echo(f"   • 失败: {skipped} 个问题")
    typer.echo(f"   • 总样本数: {completed * num_samples_per_task}")
    typer.echo(f"   • 输出文件: {output_file}")
    typer.echo(f"{'='*60}\n")


def _evaluate_solutions(
    samples_file: pathlib.Path = pathlib.Path("results/humaneval_samples.jsonl"),
    output_file: pathlib.Path = pathlib.Path("results/humaneval_report.json"),
    k_values: Optional[List[int]] = None,
    n_workers: int = 4,
    timeout: float = 3.0,
) -> None:
    """
    使用官方 HumanEval 测试评估生成的代码
    
    Args:
        samples_file: 包含生成代码的 JSONL 文件
        output_file: 输出的评估报告
        k_values: pass@k 的 k 值列表
        n_workers: 并行工作进程数
        timeout: 单个测试超时时间（秒）
    """
    if k_values is None:
        k_values = [1]
    
    typer.echo(f"\n{'='*60}")
    typer.echo(f"🧪 开始 HumanEval 评估...")
    typer.echo(f"   • 样本文件: {samples_file}")
    typer.echo(f"   • 评估指标: pass@{', pass@'.join(map(str, k_values))}")
    typer.echo(f"   • 并行进程: {n_workers}")
    typer.echo(f"   • 超时时间: {timeout}s")
    typer.echo(f"{'='*60}\n")
    
    if not samples_file.exists():
        typer.echo(f"❌ 样本文件不存在: {samples_file}")
        raise typer.Exit(code=1)
    
    try:
        _run_evaluation(samples_file, output_file, k_values, n_workers, timeout, None)
        
        # 读取并显示结果摘要
        if output_file.exists():
            with output_file.open("r", encoding="utf-8") as f:
                report = json.load(f)
            
            typer.echo(f"\n{'='*60}")
            typer.echo(f"📊 评估结果摘要")
            typer.echo(f"{'='*60}")
            
            summary = report.get("summary", {})
            typer.echo(f"\n✓ 评估任务数: {summary.get('num_tasks', 'N/A')}")
            typer.echo(f"✓ 评估样本数: {summary.get('num_samples', 'N/A')}")
            
            typer.echo(f"\n📈 通过率:")
            pass_at_k = report.get("pass_at_k", {})
            for k_val in sorted(k_values):
                key = f"pass@{k_val}"
                rate = pass_at_k.get(key, "N/A")
                if isinstance(rate, float):
                    typer.echo(f"   • {key}: {rate*100:.2f}%")
                else:
                    typer.echo(f"   • {key}: {rate}")
            
            typer.echo(f"\n📁 完整报告: {output_file}")
            typer.echo(f"{'='*60}\n")
    
    except Exception as e:
        typer.echo(f"❌ 评估失败: {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def generate(
    num_problems: Optional[int] = typer.Option(
        None,
        help="评估的问题数（默认全部 164 个）。输入 10 可只评估前 10 个。"
    ),
    num_samples: int = typer.Option(
        1,
        "--samples",
        help="每个问题生成的代码版本数（用于 pass@k 评估）"
    ),
    model_name: str = typer.Option(
        "qwen2.5-coder:7b",
        "--model",
        help="使用的 LLM 模型"
    ),
    output: pathlib.Path = typer.Option(
        pathlib.Path("results/humaneval_samples.jsonl"),
        help="输出的样本文件"
    ),
) -> None:
    """为 HumanEval 问题生成代码"""
    _generate_solutions(num_problems, num_samples, model_name, output)


@app.command()
def evaluate(
    samples: pathlib.Path = typer.Option(
        pathlib.Path("results/humaneval_samples.jsonl"),
        help="包含生成代码的 JSONL 文件"
    ),
    output: pathlib.Path = typer.Option(
        pathlib.Path("results/humaneval_report.json"),
        help="输出的评估报告"
    ),
    k: List[int] = typer.Option(
        [1],
        "--k",
        help="pass@k 的 k 值（可重复，如 --k 1 --k 10）"
    ),
    n_workers: int = typer.Option(4, help="并行工作进程数"),
    timeout: float = typer.Option(3.0, help="单个测试超时时间（秒）"),
) -> None:
    """使用官方 HumanEval 测试评估代码"""
    _evaluate_solutions(samples, output, k, n_workers, timeout)


@app.command()
def run_all(
    num_problems: Optional[int] = typer.Option(
        None,
        help="评估的问题数。输入 5 可只评估前 5 个。"
    ),
    num_samples: int = typer.Option(
        1,
        "--samples",
        help="每个问题生成的代码版本数"
    ),
    model_name: str = typer.Option(
        "qwen2.5-coder:7b",
        "--model",
        help="使用的 LLM 模型"
    ),
    k: List[int] = typer.Option(
        [1],
        "--k",
        help="pass@k 的 k 值"
    ),
    max_iterations: int = typer.Option(
        3,
        "--max-iterations",
        help="最大调试迭代次数"
    ),
    enable_plan: bool = typer.Option(
        False,
        "--enable-plan",
        help="是否启用规划阶段（多任务拆解）"
    ),
) -> None:
    """使用完整 Agent 工作流评估（planner → coder → tester → debugger）"""
    problems = read_problems()
    problem_ids = sorted(problems.keys())
    
    if num_problems:
        problem_ids = problem_ids[:num_problems]
    
    typer.echo(f"\n🎯 开始用完整 Agent 工作流评估 {len(problem_ids)} 个 HumanEval 问题...")
    typer.echo(f"   • 每个问题生成 {num_samples} 个版本")
    typer.echo(f"   • 模型: {model_name}")
    typer.echo(f"   • 最大调试次数: {max_iterations}")
    typer.echo(f"   • 规划阶段: {'启用' if enable_plan else '禁用'}\n")
    
    samples_file = pathlib.Path("results/humaneval_samples.jsonl")
    samples_file.parent.mkdir(parents=True, exist_ok=True)
    
    completed = 0
    passed_count = 0
    all_samples = []
    
    with samples_file.open("w", encoding="utf-8") as f:
        for idx, task_id in enumerate(problem_ids, 1):
            problem = problems[task_id]
            entry_point = problem.get('entry_point', 'unknown')
            
            typer.echo(f"\n{'='*70}")
            typer.echo(f"[{idx}/{len(problem_ids)}] {task_id}: {entry_point}")
            typer.echo(f"{'='*70}")
            
            # 构建需求：HumanEval 的 prompt 就是需求描述
            requirement = problem['prompt']
            
            try:
                # 为这个问题生成多个版本
                task_passed = False
                last_error = "未评估"
                last_completion = ""
                
                for sample_idx in range(num_samples):
                    typer.echo(f"\n🤖 版本 {sample_idx+1}/{num_samples} - 启动 Agent 工作流...")
                    
                    # 对 HumanEval 题目，修改需求说明来指导 Coder
                    humaneval_requirement = (
                        requirement + "\n\n"
                        "【重要说明】这是 HumanEval 编程题，请只生成要求的函数实现。\n"
                        "- 不需要 main() 函数\n"
                        "- 不需要测试代码\n"
                        "- 只生成函数定义和必要的辅助函数\n"
                        "- 确保函数名称与题目要求完全一致"
                    )
                    
                    # 调用完整的 agent 工作流
                    agent_result = solve(
                        requirement=humaneval_requirement,
                        model_name=model_name,
                        max_iterations=max_iterations,
                        enable_plan=False,  # HumanEval 单函数，不需要规划
                        project_name=task_id.replace('/', '_'),
                    )
                    
                    # 提取生成的代码
                    generated_files = agent_result.get("generated_code", {})
                    if not generated_files:
                        typer.echo(f"   ⚠️  Agent 未生成任何代码")
                        continue
                    
                    # 找到主函数所在的文件（优先级：包含 entry_point → main.py → 第一个 py 文件）
                    completion = ""
                    
                    # 第一优先级：找包含目标函数的文件
                    for filename, code_content in generated_files.items():
                        if filename.endswith(".py") and filename != "__init__.py":
                            if f"def {entry_point}" in code_content:
                                completion = code_content
                                break
                    
                    # 第二优先级：找 main.py
                    if not completion:
                        if "main.py" in generated_files:
                            main_content = generated_files["main.py"]
                            # 检查 main.py 中是否有目标函数（可能在 main.py 中定义）
                            if f"def {entry_point}" in main_content:
                                completion = main_content
                    
                    # 第三优先级：使用第一个非 __init__.py 的文件
                    if not completion:
                        for filename in sorted(generated_files.keys()):
                            if filename.endswith(".py") and filename != "__init__.py":
                                completion = generated_files[filename]
                                break
                    
                    if not completion:
                        typer.echo(f"   ⚠️  无法从生成的文件中提取代码")
                        continue
                    
                    # 提取纯函数定义（去掉测试代码等）
                    completion = _extract_python_code(completion)
                    last_completion = completion
                    
                    # 用 HumanEval 官方测试验证
                    test_code = problem["prompt"] + "\n" + completion + "\n" + problem["test"] + "\n" + f"check({entry_point})"
                    
                    passed = False
                    error_msg = "未知错误"
                    try:
                        exec_globals = {}
                        exec(test_code, exec_globals)
                        passed = True
                        error_msg = "通过"
                    except AssertionError as e:
                        error_msg = f"AssertionError: {str(e)}"
                    except SyntaxError as e:
                        error_msg = f"SyntaxError: {str(e)}"
                        debug_file = pathlib.Path(f"results/.debug_{task_id.replace('/', '_')}.py")
                        debug_file.write_text(test_code, encoding="utf-8")
                        error_msg += f" (调试文件: {debug_file})"
                    except Exception as e:
                        error_msg = f"{type(e).__name__}: {str(e)}"
                    
                    result = {"passed": passed, "result": error_msg}
                    
                    # 保存样本
                    record = {
                        "task_id": task_id,
                        "completion": completion,
                        "completion_id": f"agent-{sample_idx}",
                        "agent_tests_passed": agent_result.get("file_tests", {}),
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    all_samples.append(record)
                    
                    # 检查是否通过
                    if result.get("passed", False):
                        task_passed = True
                        if num_samples == 1:
                            typer.echo(f"\n   ✅ HumanEval 官方测试通过")
                        else:
                            typer.echo(f"\n   ✅ 版本 {sample_idx+1} HumanEval 官方测试通过")
                        break
                    else:
                        error_msg = result.get("result", "未知错误")
                        if num_samples > 1:
                            typer.echo(f"\n   ⏳ 版本 {sample_idx+1} HumanEval 官方测试失败: {error_msg[:100]}")
                        last_error = error_msg
                
                if task_passed:
                    passed_count += 1
                elif not task_passed and num_samples == 1:
                    typer.echo(f"\n   ❌ HumanEval 官方测试失败")
                    typer.echo(f"      原因: {last_error[:300]}")
                    typer.echo(f"      生成代码预览:")
                    code_lines = last_completion.split('\n')[:10]
                    for line in code_lines:
                        typer.echo(f"        {line}")
                    total_lines = len(last_completion.split('\n'))
                    if total_lines > 10:
                        typer.echo(f"        ... (共 {total_lines} 行)")
                elif not task_passed:
                    typer.echo(f"\n   ❌ 所有 {num_samples} 个版本都未通过 HumanEval 官方测试")
                    typer.echo(f"      最后错误: {last_error[:300]}")
                
                completed += 1
                
            except Exception as e:
                typer.echo(f"\n   ❌ Agent 执行失败: {str(e)}")
                import traceback
                typer.echo(f"      详细错误:\n{traceback.format_exc()}")
    
    # 显示最终统计
    typer.echo(f"\n{'='*70}")
    typer.echo(f"📊 评估完成")
    typer.echo(f"{'='*70}")
    typer.echo(f"   • 评估问题数: {completed}")
    typer.echo(f"   • 通过问题数: {passed_count}")
    typer.echo(f"   • 通过率: {passed_count/completed*100:.1f}%")
    typer.echo(f"   • 样本文件: {samples_file}")
    typer.echo(f"{'='*70}\n")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """HumanEval 评估工具"""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


if __name__ == "__main__":
    app()
