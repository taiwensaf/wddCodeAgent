"""
Tester - 测试生成与执行
"""
import json
import pathlib
import subprocess
from agent.llm_client import LLMClient
from agent.prompt_manager import PromptManager

def generate_tests(source_code: str, filename: str, model_name: str = "qwen2.5-coder:7b") -> str:
    """
    为源代码生成单元测试
    
    Args:
        source_code: 源代码内容
        filename: 源代码文件名
        model_name: 使用的模型
    
    Returns:
        测试代码JSON
    """
    print("[TESTER] 生成测试代码...")
    
    # 加载prompt模板
    pm = PromptManager()
    prompt = pm.get("tester",
                   source_code=source_code,
                   filename=filename)
    
    # 调用LLM
    client = LLMClient(
        model_name=model_name,
        temperature=0.2,
        max_tokens=2048
    )
    
    result = client.generate(prompt, response_format="json")
    return result


def save_and_run_tests(test_json: str, test_dir: str = "results/tests") -> dict:
    """
    保存测试代码并执行
    
    Args:
        test_json: 测试代码的JSON字符串
        test_dir: 测试代码保存目录
    
    Returns:
        测试结果
    """
    try:
        test_data = json.loads(test_json)
        
        # 保存测试文件
        test_path = pathlib.Path(test_dir)
        test_path.mkdir(parents=True, exist_ok=True)
        
        test_filename = test_data.get("test_filename", "test_code.py")
        test_file = test_path / test_filename
        
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_data.get("test_code", ""))
        
        print(f"[INFO] 测试文件已保存到: {test_file}")
        
        # 执行测试
        print("[INFO] 执行测试...")
        result = subprocess.run(
            ["pytest", str(test_file), "-v"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "test_file": str(test_file),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
