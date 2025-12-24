"""
Tester - 测试生成与执行
"""
import json
import pathlib
import subprocess
import re
from agent.llm_client import LLMClient
from agent.prompt_manager import PromptManager

def generate_tests(source_code: str, filename: str, model_name: str = "qwen2.5-coder:7b", source_dir: str = "results/generated_code") -> str:
    """
    为源代码生成单元测试
    
    Args:
        source_code: 源代码内容
        filename: 源代码文件名（例如 "project.py"）
        model_name: 使用的模型
        source_dir: 源代码所在目录
    
    Returns:
        测试代码JSON
    """
    print(f"[TESTER] 为 {filename} 生成测试代码...")
    
    # 获取模块名
    module_name = filename.replace(".py", "")
    
    # 构建导入代码片段 - 使用相对路径
    # 测试文件在 results/tests/，源代码在 results/generated_code/
    import_setup = f"""import sys
import os

# 获取测试文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录 (results/ 的父目录)
project_root = os.path.dirname(os.path.dirname(current_dir))
# 源代码路径
source_path = os.path.join(project_root, '{source_dir}')
sys.path.insert(0, source_path)

# 导入模块
from {module_name} import *"""
    
    # 加载prompt模板
    pm = PromptManager()
    prompt = pm.get("tester",
                   source_code=source_code,
                   filename=filename,
                   import_setup=import_setup,
                   module_name=module_name,
                   source_dir=source_dir)
    
    # 调用LLM
    client = LLMClient(
        model_name=model_name,
        temperature=0.2,
        max_tokens=2048
    )
    
    result = client.generate(prompt, response_format="json")
    return result


def save_and_run_tests(test_json: str, test_dir: str = "results/tests", source_dir: str = "results/generated_code") -> dict:
    """
    保存测试代码并执行
    
    Args:
        test_json: 测试代码的JSON字符串
        test_dir: 测试代码保存目录
        source_dir: 源代码所在目录（用于设置 PYTHONPATH）
    
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
        
        # 执行测试 - 添加 PYTHONPATH 确保能导入源代码
        import os
        env = os.environ.copy()
        # 将源代码目录添加到 PYTHONPATH
        source_path = str(pathlib.Path(source_dir).resolve())
        env["PYTHONPATH"] = source_path + os.pathsep + env.get("PYTHONPATH", "") # 保留已有的 PYTHONPATH 值 
        
        print(f"[INFO] 执行测试... (PYTHONPATH={source_path})")
        result = subprocess.run(
            ["pytest", str(test_file), "-v"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env  # 使用修改后的环境变量
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
            # collected 行
            m = re.search(r"collected\s+(\d+)\s+items?(?:\s*/\s*(\d+)\s+deselected)?", out)
            if m:
                summary["collected"] = int(m.group(1))
                if m.group(2):
                    summary["deselected"] = int(m.group(2))
            # 摘要行，例如 === 3 passed, 1 skipped in 0.12s ===
            matches = re.findall(r"=+\s+(.+?)\s+=+", out)
            if matches:
                last = matches[-1]
                parts = [p.strip() for p in last.split(',')]
                for p in parts:
                    tm = re.match(r"(\d+)\s+(passed|failed|error|errors|skipped|xfailed|xpassed|warnings?|deselected)", p)
                    if tm:
                        n = int(tm.group(1))
                        key = tm.group(2)
                        key = "errors" if key in ("error", "errors") else key
                        key = "warnings" if key.startswith("warning") else key
                        summary[key] = n
                    else:
                        dm = re.search(r"in\s+([0-9\.]+)s", p)
                        if dm:
                            summary["duration"] = float(dm.group(1))
            return summary
        
        summary = _parse_summary(result.stdout + "\n" + result.stderr)
        stdout_tail = "\n".join((result.stdout or "").splitlines()[-40:])
        
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "test_file": str(test_file),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "summary": summary,
            "stdout_tail": stdout_tail,
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
