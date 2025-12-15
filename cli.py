import sys
import argparse
from agent.agent_loop import solve

def main():
    parser = argparse.ArgumentParser(description="Code Agent with LLM")
    parser.add_argument("requirement", help="用户的需求描述")
    parser.add_argument("--model", default="llama2", help="模型名称 (默认: llama2)")
    parser.add_argument("--temperature", type=float, default=0.2, help="生成文本的随机性 (默认: 0.2)")
    parser.add_argument("--max-tokens", type=int, default=2048, help="最大生成长度 (默认: 2048)")
    parser.add_argument("--api-base", default="http://localhost:11434", help="API地址 (默认: http://localhost:11434)")
    parser.add_argument("--format", choices=["text", "json"], default="json", help="输出格式: text 或 json (默认: json)")
    
    args = parser.parse_args()
    
    # 调用solve函数
    result = solve(
        requirement=args.requirement,
        model_name=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        api_base=args.api_base,
        response_format=args.format
    )
    
    print("\n[RESULT]")
    print(result)

if __name__ == "__main__":
    main()