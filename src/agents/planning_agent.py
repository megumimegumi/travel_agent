import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from agents.base import BaseAgent
from models import TravelRequest, Itinerary, DailyItinerary, ItineraryItem
from services.deepseek_client import DeepSeekClient

class PlanningAgent(BaseAgent):
    """
    规划智能体
    负责接收旅行需求，生成详细行程规划
    """
    
    def __init__(self):
        super().__init__(name="PlanningAgent")
        
    def run(self, request: TravelRequest, weather_info: str = "", route_info: str = "", feedback: str = "", user_history: str = "") -> Itinerary:
        """执行规划任务 (可选带反馈进行优化)"""
        if feedback:
            self.log(f"接收到反馈，正在优化前往 {request.destination} 的行程...")
        else:
            self.log(f"开始为用户规划前往 {request.destination} 的行程...")
        
        # 1. 构建 Prompt
        system_prompt = self._build_system_prompt(request, weather_info, route_info, feedback, user_history)
        user_message = "请开始规划，请直接输出JSON格式结果。"
        
        # 如果是反馈模式，可以适当提高一点温度以寻求不同解，或者降低温度以严格遵循指令
        # 这里选择保持稳定
        temperature = 0.7 if not feedback else 0.5 
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # 2. 调用 LLM
        self.log("调用 LLM 生成行程...")
        # 增加 max_tokens 防止 JSON 截断 (由 4000 提升至 8192)
        response = self.llm.chat_completion(messages, temperature=temperature, max_tokens=8192)
        
        if "error" in response:
            raise Exception(f"LLM调用失败: {response['error']}")
            
        # 3. 解析结果并转换为 Pydantic 模型
        try:
            content = response["choices"][0]["message"]["content"]
            plan_dict = self._parse_json_from_response(content)
            
            # 4. 数据清洗与模型转换
            itinerary = self._convert_to_itinerary_model(request, plan_dict)
            self.log("行程规划生成成功！")
            return itinerary
            
        except Exception as e:
            self.log(f"解析规划结果失败: {e}")
            # 这里可以有一个 fallback 机制或者重试机制
            raise e

    def _build_system_prompt(self, request: TravelRequest, weather_info: str, route_info: str, feedback: str = "", user_history: str = "") -> str:
        """构建系统提示词"""
        
        constraint_instructions = ""
        if feedback:
            constraint_instructions = f"""
            ⚠️ 【重要修正指令】
            上一版行程存在以下问题，请务必在本次生成中修正：
            {feedback}
            
            请严格遵守上述修正指令，重新调整行程。
            """

        history_section = ""
        if user_history:
            history_section = f"""
            📚 【用户历史偏好记忆】
            以下是该用户过去的旅行请求记录（仅供参考，用于推断用户潜在偏好，如喜欢的目的地类型、习惯的预算范围等，但请优先满足本次明确的请求）：
            {user_history}
            """

        return f"""你是一个专业的旅行规划师。请根据用户的需求，创建一个详细、实用、个性化的旅行计划。

        用户概况:
        - 目的地: {request.destination}
        - 出发地: {request.origin}
        - 出发日期: {request.start_date or "未定"}
        - 天数: {request.days}天
        - 预算: {request.budget}人民币 (请严格把控预算)
        - 兴趣偏好: {request.interests}
        - 饮食偏好: {request.dietary_preferences}
        - 同行人员: {request.travelers_count}人 ({request.travelers_relation})
        - 旅行节奏: {request.pace.value if hasattr(request.pace, 'value') else request.pace}
        - 体力状况: {request.fitness_level.value if hasattr(request.fitness_level, 'value') else request.fitness_level}
        - 交通偏好: {request.transport_mode_preference or "智能推荐"}
        - 住宿偏好: {request.accommodation_preference or "不限"}
        - 外部路线规划信息: {route_info}
        - 额外要求: {request.extra_requirements}
        - 天气预报参考: {weather_info}

        {history_section}

        {constraint_instructions}

        计划应包括：
        1. 每日行程安排。
        2. 餐饮与住宿推荐。
        3. 交通建议与详细预算。
        4. 行前准备清单 (Preparation List)：必须具体分类(如证件,衣物,电子设备,药品等)。
        5. 特别提示 (Special Tips)：包含交通, 门票预约, 文化风俗等注意事项。
        
        重要要求:
        - 输出内容不要使用 Markdown 的加粗符号。
        - 严格按照以下的 JSON 结构返回。

        JSON 结构示例:
        {{
            "daily_plans": [
                {{
                    "day": 1,
                    "date": "2024-01-01",
                    "theme": "城市初印象",
                    "weather_summary": "晴转多云",
                    "activities": [
                        {{
                            "time": "09:00",
                            "activity": "参观故宫博物院",
                            "scenic_spot": "故宫",
                            "location": "东城区景山前街4号",
                            "description": "深入了解明清宫廷历史，打卡太和殿。",
                            "transport_suggestion": "地铁1号线天安门东站"
                        }},
                         {{
                            "time": "12:00",
                            "activity": "午餐: 四季民福烤鸭",
                            "scenic_spot": "", 
                            "location": "故宫附近", 
                            "description": "品尝正宗北京烤鸭。",
                            "transport_suggestion": "步行"
                        }}
                    ],
                   "route_suggestions": ["故宫->景山->王府井"]
                }}
            ],
            "total_cost_estimate": 2500,
            "created_at": "YYYY-MM-DD",
            "preparation_list": {{
                "证件": ["身份证", "学生证"],
                "衣物": ["T恤", "薄外套"],
                "电子设备": ["充电宝", "自拍杆"],
                "药品": ["感冒药"],
                "App准备": ["支付宝", "高德地图"]
            }},
            "special_tips": {{
                "交通": ["建议提前购买高铁票"],
                "景点": ["博物馆周一闭馆，需通过小程序提前3天预约"],
                "餐饮": ["用餐高峰期需排队"],
                "天气": ["近期多雨，请备好雨具"],
                "防坑指南": ["不要轻信路边一日游销售"]
            }}
        }}
        """

    def _parse_json_from_response(self, content: str) -> Dict[str, Any]:
        """从 LLM 响应中提取 JSON"""
        content = content.strip()
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            json_str = content[start : end + 1]
            # 简单的清理
            import re
            json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
            return json.loads(json_str)
        raise ValueError("无法在响应中找到 JSON 内容")

    def _convert_to_itinerary_model(self, request: TravelRequest, data: Dict[str, Any]) -> Itinerary:
        """将字典转换为 Itinerary 对象"""
        # 这里需要处理数据映射，因为 LLM 返回的结构可能和 Pydantic 模型略有不同，或者字段缺失
        # 我们做一些鲁棒性处理
        
        daily_plans = []
        for d in data.get("daily_plans", []):
            try:
                items = []
                for act in d.get("activities", []):
                    items.append(ItineraryItem(
                        time=act.get("time", ""),
                        activity=act.get("activity", ""),
                        location=act.get("location"),
                        scenic_spot=act.get("scenic_spot"), # 新增字段映射
                        description=act.get("description") or act.get("reason_for_selection"),
                        transport_suggestion=act.get("transport_suggestion")
                    ))
                
                daily_plans.append(DailyItinerary(
                    day=d.get("day"),
                    date=d.get("date"),
                    theme=d.get("theme", ""),
                    weather_summary=d.get("weather_summary"),
                    activities=items,
                    route_suggestions=d.get("route_suggestions", [])
                ))
            except Exception as e:
                self.log(f"跳过格式错误的一天数据: {e}")
                continue

        return Itinerary(
            request=request,
            daily_plans=daily_plans,
            total_cost_estimate=data.get("total_cost_estimate", 0),
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            preparation_list=data.get("preparation_list"),
            special_tips=data.get("special_tips")
        )
