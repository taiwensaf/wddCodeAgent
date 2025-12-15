# 作为调用大语言模型的客户端接口
import openai
from typing import Optional
from dataclasses import dataclass
import ollama

@dataclass  # 声明为数据类 用来传递模型参数
class LLMClient:
    model_name: str
    temperature: float = 0.2  # 控制生成文本的随机性，值越低越确定
    max_tokens: int = 2048  # 控制生成文本的长度
    api_base: str = "http://localhost:11434"  # 本地ollama的接口地址
    stream: bool = False

    def update_config(self, **kwargs):
        """更新配置参数"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown parameter: {key}")

    def generate(self, prompt: str, stop: Optional[list[str]] = None, response_format: Optional[str] = None) -> str:
        """调用LLM生成文本，可选结构化JSON输出"""

        try:
            # 如果使用OpenAI API
            if "gpt" in self.model_name.lower() or self.api_base.startswith("https"):
                kwargs = {
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "stop": stop,
                }
                if response_format == "json":
                    kwargs["response_format"] = {"type": "json_object"}

                response = openai.ChatCompletion.create(**kwargs)
                return response["choices"][0]["message"]["content"]

            # 如果使用本地Ollama
            else:
                messages = [{"role": "user", "content": prompt}]
                format_arg = "json" if response_format == "json" else None
                options = {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                }

                if self.stream:
                    result_text = ""
                    for chunk in ollama.chat(
                        model=self.model_name,
                        messages=messages,
                        stream=True,
                        format=format_arg,
                        options=options,
                    ):
                        result_text += chunk["message"]["content"]
                    return result_text

                response = ollama.chat(
                    model=self.model_name,
                    messages=messages,
                    format=format_arg,
                    options=options,
                )
                return response["message"]["content"]

        except Exception as e:
            print(f"Error calling LLM: {e}")
            raise
