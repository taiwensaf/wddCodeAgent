import sys
from agent.llm_client import LLMClient

def solve(requirement, model_name="llama2", temperature=0.2, max_tokens=2048, api_base="http://localhost:11434", response_format="json"):
    """
    解决用户请求
    
    Args:
        requirement: 用户的需求描述
        model_name: 模型名称，
        temperature: 生成文本的随机性，0.0-1.0，越低越确定
        max_tokens: 生成文本的最大长度
        api_base: API地址，支持本地Ollama和OpenAI
        response_format: 输出格式，None为普通文本，"json" 为结构化JSON（默认json）
    
    Returns:
        LLM生成的结果
    """
    print("*" * 20)
    print("[INFO] Solving request...")
    print(f"[INFO] Using model: {model_name}")
    print(f"[INFO] Request: {requirement}")
    print("*" * 20)
    
    try:
        # 初始化LLM客户端
        client = LLMClient(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_base=api_base
        )
        
        prompt = f"""你是一个软件工程智能体，请根据用户需求生成代码。
                【严格输出要求】
                1. 你必须只返回 JSON，不得包含任何解释性文字
                2. 不得使用 Markdown（```）
                3. JSON 必须是合法的，可被 Python json.loads() 解析
                4. code 字段中只包含源代码文本

                【JSON 输出格式】
                {{
                \"status\": \"success\",
                \"language\": \"python\",
                \"filename\": \"<filename>.py\",
                \"code\": \"<python source code>\",
                \"entry_point\": \"<main function name>\",
                \"description\": \"<简要说明>\"
                }}

                【用户需求】
                {requirement}
                """
        # 调用LLM生成响应
        result = client.generate(prompt, response_format=response_format)
        return result
    
    except Exception as e:
        print(f"[ERROR] Failed to solve request: {e}")
        return f"Error: {e}"
