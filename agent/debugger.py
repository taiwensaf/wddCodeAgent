"""
Debugger - Bug分析与修复
"""
import json
from agent.llm_client import LLMClient
from agent.prompt_manager import PromptManager

def debug_code(source_code: str, error_message: str, model_name: str = "qwen2.5-coder:7b") -> str:
    """
    分析并修复代码中的bug
    
    Args:
        source_code: 有问题的源代码
        error_message: 错误信息
        model_name: 使用的模型
    
    Returns:
        修复结果JSON
    """
    print("[DEBUGGER] 分析并修复代码...")
    
    # 加载prompt模板
    pm = PromptManager()
    prompt = pm.get("debugger",
                   source_code=source_code,
                   error_message=error_message)
    
    # 调用LLM
    client = LLMClient(
        model_name=model_name,
        temperature=0.1,  # 调试时温度更低
        max_tokens=2048
    )
    
    result = client.generate(prompt, response_format="json")
    
    try:
        debug_data = json.loads(result)
        bugs = debug_data.get("bugs_found", [])
        print(f"[INFO] 发现 {len(bugs)} 个bug，已修复")
        return result
    except json.JSONDecodeError:
        print("[ERROR] 无法解析调试结果")
        return result
