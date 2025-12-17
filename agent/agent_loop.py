"""
Agent主循环 - 整合规划、编码、测试、调试模块
"""
import json
from agent.planner import plan
from agent.coder import code_generate, code_save, code_aggregate, code_save_aggregated
from agent.tester import generate_tests, save_and_run_tests
from agent.debugger import debug_code

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
        "debug_history": []
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
    else:
        # 如果不规划，则创建一个默认任务
        project_name = "project"
        tasks = [{"name": "Main", "description": requirement}]
    
    if not tasks:
        print("[ERROR] 没有任务可执行")
        return all_results
    
    print(f"\n[INFO] 共有 {len(tasks)} 个任务需要处理")
    
    # 步骤2: 遍历所有任务，生成代码
    task_modules = []
    all_code_results = {}
    
    for idx, task in enumerate(tasks):
        print(f"\n[TASK {idx+1}/{len(tasks)}] 处理任务: {task.get('name', 'Unknown')}")
        print("-" * 50)
        
        task_name = task.get("name", f"Task{idx}")
        task_desc = f"任务: {task_name}\n说明: {task.get('description', '')}"
        
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
            
        except json.JSONDecodeError:
            print(f"[WARNING] 无法解析任务 {task_name} 的代码生成结果")
            continue
    
    if not task_modules:
        print("[ERROR] 所有任务代码生成都失败")
        return all_results
    
    # 步骤2.5: 汇总所有代码
    aggregated_code = code_aggregate(task_modules, project_name)
    file_path = code_save_aggregated(aggregated_code, project_name)
    print(f"\n[SUCCESS] 汇总代码已保存到: {file_path}")
    all_results["generated_code"] = aggregated_code
    all_results["generated_file"] = file_path
    
    # 步骤3: 为汇总项目生成测试
    try:
        filename = f"{project_name}.py"
        
        print("\n[INFO] 为汇总项目生成测试...")
        test_result = generate_tests(aggregated_code, filename, model_name)
        test_data = json.loads(test_result)
        
        if test_data.get("status") == "success":
            test_exec_result = save_and_run_tests(test_result)
            all_results["tests"] = test_exec_result
            
            # 如果测试失败，尝试调试
            if test_exec_result.get("status") == "failed":
                print("\n[INFO] 测试失败，开始调试...")
                current_code = aggregated_code
                
                for iteration in range(max_iterations):
                    error_msg = test_exec_result.get("stderr", "")
                    debug_result = debug_code(current_code, error_msg, model_name)
                    
                    debug_data = json.loads(debug_result)
                    all_results["debug_history"].append(debug_data)
                    
                    if debug_data.get("status") == "success":
                        fixed_code = debug_data.get("fixed_code", "")
                        # 重新保存修复后的代码
                        file_path = code_save_aggregated(fixed_code, project_name)
                        current_code = fixed_code
                        print(f"[INFO] 第 {iteration+1} 次修复完成")
                        
                        # 重新运行测试
                        test_result = generate_tests(fixed_code, filename, model_name)
                        test_data = json.loads(test_result)
                        test_exec_result = save_and_run_tests(test_result)
                        all_results["tests"] = test_exec_result
                        
                        if test_exec_result.get("status") == "success":
                            print("[SUCCESS] 所有测试通过！")
                            break
                    
                    if iteration == max_iterations - 1:
                        print(f"[WARNING] 达到最大调试次数 ({max_iterations})，停止调试")
        else:
            print("[WARNING] 测试生成失败")
    
    except Exception as e:
        print(f"[WARNING] 测试阶段出错: {e}")
    
    print("=" * 50)
    print("[AGENT] 工作流完成")
    print("=" * 50)
    
    return all_results
