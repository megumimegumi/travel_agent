from typing import List, Optional, Dict
from datetime import datetime, timedelta
from models import SimulationEvent, EventType, TravelState
import json

class EnvironmentSimulator:
    """
    环境模拟器
    用于维护"虚拟世界"的时间、天气和突发事件状态
    """
    def __init__(self, start_time: str, initial_weather: str = "晴朗"):
        self.current_time = datetime.fromisoformat(start_time)
        self.weather = initial_weather
        self.active_events: List[SimulationEvent] = []
        self.logs: List[str] = []

    def get_time_str(self) -> str:
        return self.current_time.strftime("%Y-%m-%d %H:%M")

    def time_pass(self, minutes: int):
        """让时间流逝"""
        self.current_time += timedelta(minutes=minutes)
        self.logs.append(f"⏰ 时间流逝: {minutes}分钟 (当前: {self.get_time_str()})")
        
        # 简单模拟：如果还有事件，检查是否过期（此处暂略，假设事件持续直到手动清除或覆盖）

    def inject_event(self, event: SimulationEvent):
        """注入突发事件"""
        self.active_events.append(event)
        self.logs.append(f"⚠️ 突发事件注入: [{event.type.value}] {event.description}")
        
        # 如果是天气事件，直接更新环境天气
        if event.type == EventType.WEATHER_CHANGE:
            # 简单的提取逻辑，实际可能更复杂
            if "雨" in event.description:
                self.weather = "中雨"
            elif "晴" in event.description:
                self.weather = "晴朗"
            else:
                self.weather = event.description

    def create_snapshot(self) -> dict:
        """获取当前环境快照 (Information)"""
        return {
            "time": self.get_time_str(),
            "weather": self.weather,
            "events": [e.description for e in self.active_events]
        }
