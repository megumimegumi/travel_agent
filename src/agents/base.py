from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from services.deepseek_client import DeepSeekClient
from utils.config import Config

class BaseAgent(ABC):
    """
    Agent 基类
    封装了 LLM 客户端和基础配置，定义了标准的生命周期方法
    """
    
    def __init__(self, name: str):
        self.name = name
        self.config = Config()
        self.llm = DeepSeekClient() 
        self.memory: List[Dict[str, str]] = []

    def log(self, message: str):
        """标准日志输出"""
        print(f"[{self.name}] {message}")

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """Agent 执行入口"""
        pass
    
    def think(self, context: str) -> str:
        """基础思考能力"""
        # 这里可以实现通用的 CoT (Chain of Thought) 逻辑
        pass
