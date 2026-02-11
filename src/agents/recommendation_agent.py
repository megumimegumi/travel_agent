from typing import List, Optional
from agents.base import BaseAgent
from services.deepseek_client import DeepSeekClient
import json

class RecommendationAgent(BaseAgent):
    """
    目的地推荐智能体
    根据用户画像和模糊需求，推荐合适的旅游目的地
    """
    
    def __init__(self):
        super().__init__(name="RecommendationAgent")
    
    def run(self, user_profile: dict, requirements: str) -> List[dict]:
        """Alias for recommend to satisfy BaseAgent abstract method"""
        return self.recommend(user_profile, requirements)
        
    def recommend(self, user_profile: dict, requirements: str) -> List[dict]:
        """
        生成推荐列表
        Returns: [{'city': 'xx', 'reason': 'xx', 'tags': ['xx']}]
        """
        self.log("开始分析用户需求并推荐目的地...")
        
        system_prompt = f"""
        你是一个资深的旅行灵感规划师。请根据用户的个人信息和详细需求，推荐12个最适合的国内旅游目的地。
        
        用户信息:
        - 出发地: {user_profile.get('origin', '未知')}
        - 偏好: {user_profile.get('interests', [])}
        
        本次具体要求:
        {requirements}
        
        请严格按照以下JSON格式返回结果，不要包含Markdown格式：
        [
            {{
                "city": "目的地名称",
                "reason": "推荐理由（结合用户出发地、预算和兴趣，50字以内）",
                "tags": ["标签1", "标签2"],
                "suitable_season": "推荐游玩月份"
            }}
        ]
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "请给我推荐12个目的地，只返回JSON数组。"}
        ]
        
        response = self.llm.chat_completion(messages, temperature=0.8) # 推荐需要一点发散性
        
        if "error" in response:
            raise Exception(f"LLM调用失败: {response['error']}")
            
        try:
            content = response["choices"][0]["message"]["content"]
            # 更强健的 JSON 提取
            import re
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                json_str = match.group()
                return json.loads(json_str)
            else:
                # 尝试直接解析
                content = content.replace("```json", "").replace("```", "").strip()
                return json.loads(content)
        except Exception as e:
            self.log(f"解析推荐结果失败: {e}\n原始内容: {content}")
            # 返回一个默认的错误提示项，而不是空列表，这样前端能看到反馈
            return [{
                "city": "解析失败",
                "reason": f"AI 返回了非标准格式的数据，请重试。错误: {str(e)}",
                "tags": ["系统错误"],
                "suitable_season": "未知"
            }]
