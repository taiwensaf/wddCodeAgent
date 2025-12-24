import sys
import argparse
import json
from agent.agent_loop import solve

def main():
    parser = argparse.ArgumentParser(description="Code Agent with LLM - 完整工作流")
    parser.add_argument("requirement", help="用户的需求描述")
    parser.add_argument("--model", default="qwen2.5-coder:7b", help="模型名称 (默认: qwen2.5-coder:7b)")
    parser.add_argument("--plan", action="store_true", default=True, help="是否启用需求规划阶段 (默认: 启用)")
    parser.add_argument("--no-plan", dest="plan", action="store_false", help="跳过需求规划阶段")
    parser.add_argument("--max-iterations", type=int, default=3, help="最大调试迭代次数 (默认: 3)")
    
    args = parser.parse_args()
    
    # 调用solve函数
    result = solve(
        requirement=args.requirement,
        model_name=args.model,
        max_iterations=args.max_iterations,
        enable_plan=args.plan
    )
    
    print("\n" + "=" * 50)
    print("[RESULT] 工作流结果")
    print("=" * 50)
    
    # 打印规划结果
    if result.get("plan"):
        plan_data = result["plan"]
        print("\n【规划阶段】")
        print(f"项目: {plan_data.get('project_name', 'N/A')}")
        print(f"复杂度: {plan_data.get('complexity', 'N/A')}")
        tasks = plan_data.get('tasks', [])
        print(f"任务数: {len(tasks)}")
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task.get('name', 'N/A')}: {task.get('description', 'N/A')}")
    
    # 打印生成的代码
    if result.get("generated_file"):
        print("\n【代码生成】")
        print(f"汇总文件: {result.get('generated_file', 'N/A')}")
        if result.get("generated_code"):
            code_lines = result["generated_code"].split("\n")
            print(f"代码行数: {len(code_lines)}")
    
    # 打印测试结果
    if result.get("tests"):
        test_result = result["tests"]
        print("\n【测试结果】")
        print(f"状态: {test_result.get('status', 'N/A')}")
        if test_result.get("test_file"):
            print(f"测试文件: {test_result.get('test_file')}")
        
        summary = test_result.get("summary", {}) or {}
        if summary:
            collected = summary.get('collected')
            duration = summary.get('duration')
            stats = []
            for key in ("passed", "failed", "errors", "skipped", "xfailed", "xpassed", "deselected", "warnings"):
                val = summary.get(key)
                if val:
                    stats.append(f"{key}: {val}")
            if collected is not None:
                print(f"用例总数: {collected}")
            if stats:
                print("统计: " + ", ".join(stats))
            if duration is not None:
                print(f"耗时: {duration:.2f}s")
        
        if test_result.get("status") == "success":
            print("✓ 所有测试通过！")
            # 成功时也展示测试输出的最后几行，便于核对
            tail = test_result.get("stdout_tail") or ""
            if tail:
                print("\n输出摘要:")
                print(tail)
        else:
            print("✗ 测试失败")
            # 失败时显示更详细的输出尾部帮助定位
            tail = test_result.get("stdout_tail") or test_result.get("stdout", "")
            if tail:
                print("\n失败输出摘要:")
                print(tail)
            if test_result.get("stderr"):
                print("\n错误信息 (stderr):")
                print(test_result.get("stderr", "")[:1000])
    
    # 打印调试历史
    if result.get("debug_history"):
        print("\n【调试历史】")
        for i, debug in enumerate(result["debug_history"], 1):
            bugs = debug.get("bugs_found", [])
            print(f"第 {i} 次修复: 发现 {len(bugs)} 个bug")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()