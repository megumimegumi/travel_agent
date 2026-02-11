import json
from typing import Optional, Dict, Any, List
from agents.base import BaseAgent
from models import TravelSession, TravelState, Itinerary, DailyItinerary
from services.deepseek_client import DeepSeekClient

class GuideAgent(BaseAgent):
    """
    向导智能体 (Guide)
    负责 AIR 循环中的 Reflection 与 Action。
    它监控环境变化，决定是否需要调整当前行程。
    """
    
    def __init__(self):
        super().__init__(name="GuideAgent")

    def run(self, session: TravelSession, env_snapshot: Dict[str, Any]) -> str:
        """运行 Guide Agent (别名 reflect_and_act)"""
        return self.reflect_and_act(session, env_snapshot)

    def reflect_and_act(self, session: TravelSession, env_snapshot: Dict[str, Any]) -> str:
        """
        核心 AIR 方法
        
        Args:
            session: 当前用户的旅行状态和计划
            env_snapshot: 当前环境信息 (时间、天气、突发事件)
        
        Returns:
             Action 指令 (例如 "CONTINUE", "REPLAN: reason")
        """
        self.log(f"正在进行环境感知与反思 (Reflection)... 环境: {env_snapshot}")
        
        # 1. 提取当前应该进行的活动
        current_plan_context = self._get_current_planned_activity(session, env_snapshot['time'])
        
        # 2. 构建 Prompt 进行推理
        prompt = self._build_reflection_prompt(session, env_snapshot, current_plan_context)
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "请根据当前情况做出决策。"}
        ]
        
        # 3. 调用 LLM
        response = self.llm.chat_completion(messages, temperature=0.5)
        
        if "error" in response:
            self.log(f"Reflection 失败: {response['error']}")
            return "CONTINUE" # 默认继续
            
        decision = response["choices"][0]["message"]["content"]
        self.log(f"🔍 决策结果: {decision}")
        return decision

    def _get_current_planned_activity(self, session: TravelSession, current_time_str: str) -> str:
        """简单查找当前时间段的计划"""
        # 简化逻辑：返回下一项未完成的活动即可
        # 实际逻辑应解析时间对比
        current_dt = current_time_str # Simplified comparison
        
        # 遍历行程，找到第一个"未完成"且时间匹配的
        # 为了Demo，我们直接返回 "当前时段计划内容" 的摘要
        for day in session.itinerary.daily_plans:
            # 简化：假设是第一天
            if day.day == 1:
                return f"Day 1 计划: {[act.activity for act in day.activities]}"
        return "无计划"

    def _build_reflection_prompt(self, session: TravelSession, env: Dict, plan_ctx: str) -> str:
        return f"""你是一个智能旅行管家。你需要实施 Action-Information-Reflection 循环。

        [Information - 环境信息]
        - 当前时间: {env['time']}
        - 当前天气: {env['weather']}
        - 突发事件: {env['events']}

        [Process - 用户状态]
        - 当前位置: {session.state.current_location}
        - 原始计划概览: {plan_ctx}
        - 用户体力概况: {session.request.fitness_level.value}

        [Reflection - 任务]
        请分析当前环境（尤其是突发事件和天气）是否影响接下来的行程？
        
        判断逻辑：
        1. 如果一切正常，或者影响很小（例如"小雨"但原本就是在室内吃火锅），则输出 "CONTINUE"。
        2. 如果影响严重（例如"暴雨"我们要去爬山，或者"交通瘫痪"导致赶不上车），则输出 "REPLAN: [原因]"。
        
        [Constraints]
        - 只根据逻辑判断，不要过于敏感。
        - 你的输出必须是以下两种格式之一，不要包含其他废话:
          Format 1: CONTINUE
          Format 2: REPLAN: <详细原因描述>
        """
