"""
Prompt 管理器 - 统一加载和管理所有prompt模板
"""
import pathlib
from typing import Dict

class PromptManager:
    def __init__(self, prompt_dir: str = "prompt"):
        self.prompt_dir = pathlib.Path(prompt_dir)
        self._prompts: Dict[str, str] = {}
        self._load_all_prompts() # 加载所有prompt文件 
    
    def _load_all_prompts(self):
        """加载所有prompt文件"""
        if not self.prompt_dir.exists():
            print(f"[WARNING] Prompt directory not found: {self.prompt_dir}")
            return
        
        for prompt_file in self.prompt_dir.glob("*.txt"):
            name = prompt_file.stem  # 文件名不含扩展名
            with open(prompt_file, "r", encoding="utf-8") as f:
                self._prompts[name] = f.read()
            print(f"[INFO] Loaded prompt: {name}")
    
    def get(self, name: str, **kwargs) -> str:
        """
        获取prompt模板并填入变量
        Args:
            name: prompt名称 (planner, coder, tester, debugger)
            **kwargs: 要填入的变量
        Returns:
            填入变量后的prompt
        """
        if name not in self._prompts:
            raise ValueError(f"Prompt not found: {name}")
        
        template = self._prompts[name]
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing variable in prompt '{name}': {e}")
    
    def list_prompts(self) -> list:
        """列出所有可用的prompt"""
        return list(self._prompts.keys())
