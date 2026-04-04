import json
from src.agents.planning_agent import PlanningAgent
from src.models import TravelRequest

req = TravelRequest(user_id='llll', destination='南昌', origin='上海', days=5, budget=3000, pace='适中')
agent = PlanningAgent()
hist = '用户过去5次的旅行记录如下，这能精准反映TA真实的消费水平、同行人员结构以及核心游玩节奏：\n1. 曾在 2026-04-03 前往: 南京, 时长: 3天, 预算: 4000元, 出行人物: 情侣, 游玩节奏: 适中, 偏好标签: 无\n2. 曾在 2026-04-02 前往: 巴黎, 时长: 7天, 预算: 50000元, 出行人物: 独自一人, 游玩节奏: 适中, 偏好标签: 奢华'
res = agent.run(req, weather_info='第二天下午阵雨', route_info='', user_history=hist)
print(json.dumps(res.dict().get('special_tips'), ensure_ascii=False))
