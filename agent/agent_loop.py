"""
Agent主循环 - 整合规划、编码、测试、调试模块
"""
import json
from agent.planner import plan
from agent.coder import code_generate, code_save, code_aggregate, code_save_multi_file, code_save_aggregated
from agent.tester import generate_tests, save_and_run_tests
from agent.debugger import debug_code
import re
import pathlib

def solve(requirement: str, model_name: str = "qwen2.5-coder:7b", max_iterations: int = 3, enable_plan: bool = True):
    """
    完整的代码生成工作流
    
    Args:
        requirement: 用户的需求描述
        model_name: 使用的模型
        max_iterations: 最大调试迭代次数
        enable_plan: 是否启用需求规划阶段
    
    Returns:
        生成的代码和结果
    """
    print("=" * 50)
    print("[AGENT] 启动代码生成工作流")
    print("=" * 50)
    
    all_results = {
        "requirement": requirement,
        "plan": None,
        "generated_code": None,
        "tests": None,
        "debug_history": [],
        "file_tests": {}  # 存储各文件的测试结果
    }
    
    # 步骤1: 需求规划
    tasks = []
    if enable_plan:
        plan_result = plan(requirement, model_name)
        all_results["plan"] = plan_result
        
        if plan_result.get("status") == "error":
            return all_results
        
        tasks = plan_result.get("tasks", [])
        project_name = plan_result.get("project_name", "project")
        
        # 确保项目名称符合 Python 文件命名规范
        project_name = re.sub(r'[^\w\s-]', '', project_name)  # 移除特殊字符
        project_name = re.sub(r'[-\s]+', '_', project_name)   # 空格和横线替换为下划线
        project_name = project_name.lower()                    # 转小写
        if not project_name:
            project_name = "project"
    else:
        # 如果不规划，则创建一个默认任务
        project_name = "project"
        tasks = [{"name": "Main", "description": requirement}]
    
    if not tasks:
        print("[ERROR] 没有任务可执行")
        return all_results

    print(f"\n[INFO] 共有 {len(tasks)} 个任务需要处理")
    

    # 步骤2: 遍历所有任务，生成代码
    task_modules = [] # 存储每个任务生成的代码模块
    all_code_results = {}   # 存储每个任务的代码生成结果
    accumulated_code = ""  # 累积已生成的代码作为上下文，供后续任务参考
    
    for idx, task in enumerate(tasks):
        print(f"\n[TASK {idx+1}/{len(tasks)}] 处理任务: {task.get('name', 'Unknown')}")
        print("-" * 50)
        
        task_name = task.get("name", f"Task{idx}")
        # 合并全局需求与当前任务描述，提供完整上下文
        task_desc = (
            f"【项目总需求】\n{requirement}\n\n"
            f"【当前任务】{task_name}\n说明: {task.get('description', '')}"
        )
        
        # 如果有多个任务且不是第一个，传入已生成的代码作为上下文
        if len(tasks) > 1 and accumulated_code:
            task_desc += (
                f"\n\n【已生成的代码】\n{accumulated_code}\n"
                f"\n【注意】请生成与上述代码不同的、互补的模块，不要重复实现相同的函数或类。"
            )
        
        # 为每个任务生成代码
        code_result = code_generate(requirement, task_desc, model_name)
        all_code_results[task_name] = code_result
        
        try:
            code_data = json.loads(code_result)
            if code_data.get("status") != "success":
                print(f"[WARNING] 任务 {task_name} 代码生成失败，跳过")
                continue
            
            # 提取代码
            code = code_data.get("code", "")
            task_modules.append({
                "task_name": task_name,
                "code": code,
                "filename": code_data.get("filename", f"{task_name}.py")
            })
            
            # 累积代码供下一个任务参考
            accumulated_code += f"\n# {task_name}\n{code}\n"
            
        except json.JSONDecodeError:
            print(f"[WARNING] 无法解析任务 {task_name} 的代码生成结果")
            continue
    
    if not task_modules:
        print("[ERROR] 所有任务代码生成都失败")
        return all_results
    
    # 步骤2.5: 汇总所有代码（多文件结构）
    file_dict = code_aggregate(task_modules, project_name)
    saved_files = code_save_multi_file(file_dict, project_name)
    
    print(f"\n[SUCCESS] 项目已保存 {len(saved_files)} 个文件")
    all_results["generated_code"] = file_dict
    all_results["generated_files"] = saved_files
    
    project_dir = f"results/generated_code/{project_name}"
    
    # 步骤3: 为所有文件生成并运行测试
    print("\n[INFO] 开始为所有文件生成测试...")
    
    # 不包含 __init__.py 和已有的测试文件
    test_files = [f for f in file_dict.keys() 
                  if f.endswith(".py") and not f.startswith("test_") and f != "__init__.py"]
    
    for file_name in test_files:
        print(f"\n[TEST] 为 {file_name} 生成测试...")
        file_code = file_dict[file_name]
        current_code = file_code
        
        # 生成测试
        test_result = generate_tests(file_code, file_name, model_name, source_dir=project_dir)
        
        try:
            test_data = json.loads(test_result)
            
            if test_data.get("status") != "success":
                print(f"[WARNING] {file_name} 测试生成失败")
                all_results["file_tests"][file_name] = {"status": "test_gen_failed", "reason": test_data.get("message")}
                continue
            
            # 执行测试
            test_exec_result = save_and_run_tests(test_result, source_dir=project_dir)
            all_results["file_tests"][file_name] = test_exec_result
            
            # 如果测试失败，进入调试循环
            if test_exec_result.get("status") == "failed":
                print(f"\n[DEBUG] {file_name} 测试失败，开始调试...")
                
                for iteration in range(max_iterations):
                    error_msg = (
                        test_exec_result.get("stdout_tail", "") + "\n" +
                        test_exec_result.get("stderr", "")
                    ).strip()
                    
                    if not error_msg:
                        print(f"[INFO] {file_name} 未找到错误信息，停止调试")
                        break
                    
                    # 检查不可调试错误
                    fatal_patterns = ["ModuleNotFoundError", "SyntaxError", "IndentationError"]
                    if any(p in error_msg for p in fatal_patterns):
                        print(f"[WARNING] {file_name} 检测到致命错误，终止调试")
                        break
                    
                    # 调用debugger，传入完整上下文
                    debug_result = debug_code(current_code, error_msg, model_name)
                    
                    try:
                        debug_data = json.loads(debug_result)
                    except json.JSONDecodeError:
                        print(f"[WARNING] 无法解析 {file_name} 的调试结果")
                        break
                    
                    all_results["debug_history"].append({
                        "file": file_name,
                        "iteration": iteration + 1,
                        "error_message": error_msg,
                        "debug_result": debug_data,
                        "test_summary": test_exec_result.get("summary"),
                    })
                    
                    if debug_data.get("status") != "success":
                        print(f"[WARNING] {file_name} Debugger 无法修复，终止调试")
                        break
                    
                    fixed_code = debug_data.get("fixed_code", "")
                    if not fixed_code:
                        print(f"[WARNING] {file_name} 无法获取修复后的代码")
                        break
                    
                    # 更新文件
                    file_path = pathlib.Path(saved_files.get(file_name, ""))
                    if file_path.exists():
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(fixed_code)
                        current_code = fixed_code
                        print(f"[INFO] {file_name} 第 {iteration+1} 次修复完成")
                        
                        # 重新测试
                        test_result = generate_tests(fixed_code, file_name, model_name, source_dir=project_dir)
                        test_data = json.loads(test_result)
                        test_exec_result = save_and_run_tests(test_result, source_dir=project_dir)
                        all_results["file_tests"][file_name] = test_exec_result
                        
                        if test_exec_result.get("status") == "success":
                            print(f"[SUCCESS] {file_name} 所有测试通过！")
                            break
                    
                    if iteration == max_iterations - 1:
                        print(f"[WARNING] {file_name} 达到最大调试次数，停止调试")
            else:
                print(f"[SUCCESS] {file_name} 测试通过")
        
        except json.JSONDecodeError:
            print(f"[WARNING] 无法解析 {file_name} 的测试生成结果")
            all_results["file_tests"][file_name] = {"status": "error", "reason": "JSON parse error"}
    
    # 步骤4: 汇总测试结果
    print("\n" + "=" * 50)
    print("[SUMMARY] 测试结果汇总")
    print("=" * 50)
    
    passed_files = [f for f, result in all_results["file_tests"].items() 
                    if result.get("status") == "success"]
    failed_files = [f for f, result in all_results["file_tests"].items() 
                    if result.get("status") == "failed"]
    
    print(f"✓ 通过: {len(passed_files)}/{len(test_files)} 个文件")
    if passed_files:
        for f in passed_files:
            print(f"  - {f}")
    
    if failed_files:
        print(f"✗ 失败: {len(failed_files)}/{len(test_files)} 个文件")
        for f in failed_files:
            print(f"  - {f}")
    
    print("=" * 50)
    print("[AGENT] 工作流完成")
    print("=" * 50)
    
    return all_results
