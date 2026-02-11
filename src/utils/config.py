"""
配置管理模块
"""

import os
from typing import Optional
from dotenv import load_dotenv

class Config:
    """配置管理类"""
    
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        
        # API 配置
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.qweather_api_key = os.getenv("QWEATHER_API_KEY", "dd0189861d284c57ae1d17e3bd80cff6")
        self.amap_api_key = os.getenv("AMAP_API_KEY", "827259061d8d5e336bcda246473084b1")
        self.scenic_api_key = os.getenv("SCENIC_API_KEY", "d329705d96d7")
        
        # 应用配置
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        # 文件路径
        self.data_dir = "data"
        self.plans_dir = os.path.join(self.data_dir, "plans")
        self.recommendations_dir = os.path.join(self.data_dir, "recommendations")
    
    def validate(self) -> bool:
        """验证配置是否有效"""
        if not self.api_key:
            print("❌ 错误：未找到 DEEPSEEK_API_KEY 环境变量")
            print("请在 .env 文件中设置 API 密钥")
            return False
        
        if not self.api_key.startswith("sk-"):
            print("⚠️ 警告：API 密钥格式可能不正确")
        
        return True
    
    def print_config(self):
        """打印配置信息"""
        print("📋 当前配置：")
        print(f"   API Key: {self.api_key[:10]}...")
        print(f"   Base URL: {self.base_url}")
        print(f"   调试模式: {self.debug}")
        print(f"   日志级别: {self.log_level}")
        print(f"   最大令牌数: {self.max_tokens}")
        print(f"   温度参数: {self.temperature}")
