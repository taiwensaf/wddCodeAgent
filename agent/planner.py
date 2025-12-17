"""
Planner - 需求分析和任务拆解
"""
import json
from agent.llm_client import LLMClient
from agent.prompt_manager import PromptManager

def plan(requirement: str, model_name: str = "qwen2.5-coder:7b") -> dict:
    """
    分析需求，拆解为多个子任务
    
    Args:
        requirement: 用户需求描述
        model_name: 使用的模型
    
    Returns:
        包含项目信息和任务列表的字典
    """
    print("*" * 20)
    print("[PLANNER] 分析需求并拆解任务...")
    print("*" * 20)
    
    # 加载prompt模板
    pm = PromptManager()
    prompt = pm.get("planner", requirement=requirement)
    
    # 调用LLM
    client = LLMClient(
        model_name=model_name,
        temperature=0.2,
        max_tokens=2048
    )
    
    result = client.generate(prompt, response_format="json")
    
    try:
        plan_data = json.loads(result)
        print(f"[INFO] 项目: {plan_data.get('project_name', 'N/A')}")
        print(f"[INFO] 复杂度: {plan_data.get('complexity', 'N/A')}")
        print(f"[INFO] 任务数: {len(plan_data.get('tasks', []))}")
        return plan_data
    except json.JSONDecodeError as e:
        print(f"[ERROR] 无法解析规划结果: {e}")
        return {"status": "error", "message": str(e)}
