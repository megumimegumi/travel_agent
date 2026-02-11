"""
DeepSeek API 客户端
"""

import json
import requests
from typing import Dict, List, Any, Optional
from utils.config import Config

class DeepSeekClient:
    """DeepSeek API 客户端"""
    
    def __init__(self):
        self.config = Config()
        self.base_url = self.config.base_url
        self.api_key = self.config.api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    #聊天补全接口
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       model: str = "deepseek-chat",
                       temperature: float = None,
                       max_tokens: int = None) -> Dict[str, Any]:
        """
        发送聊天补全请求
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数
            
        Returns:
            API响应
        """
        try:
            url = f"{self.base_url}/chat/completions"
            
            # 使用配置中的默认值或传入的参数
            temperature = temperature if temperature is not None else self.config.temperature
            max_tokens = max_tokens if max_tokens is not None else self.config.max_tokens
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=180)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "error": f"API请求失败: {str(e)}",
                "status": "failed"
            }
        except Exception as e:
            return {
                "error": f"处理请求时出错: {str(e)}",
                "status": "failed"
            }
    
    def get_weather_advice(self, destination: str, weather_data: Dict[str, Any]) -> str:
        """根据天气生成出行建议"""
        prompt = f"""请根据以下天气信息，为前往{destination}的旅客提供一段简短、个性化的出行建议（100字以内），包括穿衣、携带物品和适合的活动类型。不要使用Markdown格式。
        
        天气数据:
        {json.dumps(weather_data, ensure_ascii=False)}
        """
        messages = [{"role": "user", "content": prompt}]
        try:
            response = self.chat_completion(messages, max_tokens=200)
            if "error" in response: return "无法获取建议"
            return response["choices"][0]["message"]["content"].strip()
        except:
            return "建议携带雨伞，注意保暖。"

    def generate_travel_plan(self, 
                           destination: str, 
                           days: int,
                           interests: str = None,
                           budget: int = 2000,
                           additional_requirements: str = "",
                           weather_info: str = "",
                           travelers: str = "Solo",
                           pace: str = "Moderate",
                           fitness_level: str = "Average",
                           start_date: str = "",
                           transport_mode: str = "Driving",
                           origin: str = "",
                           route_info: str = "") -> Dict[str, Any]:
        """
        生成旅行计划
        
        Args:
            destination: 目的地
            days: 天数
            interests: 兴趣描述
            budget: 预算金额(CNY)
            additional_requirements: 额外要求
            weather_info: 天气信息
            travelers: 旅行同伴
            pace: 旅行节奏
            fitness_level: 体力状况
            start_date: 出发日期
            transport_mode: 交通偏好
            origin: 出发地 (新增)
            route_info: 路线规划简报
            
        Returns:
            旅行计划
        """
        # 构建系统提示词
        system_prompt = f"""你是一个专业的旅行规划师。请根据用户的需求，创建一个详细、实用、个性化的旅行计划。

        用户概况:
        - 目的地: {destination}
        - 出发地: {origin} (如果为空则忽略)
        - 出发日期: {start_date}
        - 天数: {days}天
        - 预算: {budget}人民币
        - 兴趣偏好: {interests}
        - 同行人员: {travelers}
        - 旅行节奏: {pace}
        - 体力状况: {fitness_level}
        - 交通偏好: {transport_mode} (AI将优先基于此偏好规划市内交通，大交通请参考下方的[外部路线规划信息])
        - 外部路线规划信息: {route_info} (如果包含"从某地到某地"的信息，请务必在[交通建议]部分引用，说明大交通方案。如果route_info为空，但用户提供了出发地，请根据常识简要建议大交通)
        - 额外要求: {additional_requirements}
        - 天气预报参考: {weather_info}

        计划应包括：
        1. 每日行程安排（生成每一天的规划前，必须先在当日开头简要概括该日天气，并根据天气合理安排行程。例如下雨安排室内活动）。
        2. 餐饮建议（推荐具体餐厅或特色菜）
        3. 住宿推荐（具体酒店或区域，符合预算）
        4. 交通建议（如何到达及市内交通，需结合用户的交通偏好 {transport_mode} 及 上述路线规划信息）。
        5. 详细预算估算（各项费用明细，确保总额在 {budget} CNY 左右）
        6. 实用贴士（包含天气应对、穿衣建议等）
        
        重要要求:
        - 输出内容不要使用 Markdown 的加粗符号（即不要出现 **符号）。
        - 严格按照 JSON 格式返回。

        请以JSON格式返回，包含以下字段：
        - destination: 目的地
        - days: 天数
        - total_budget: 总预算估算
        - daily_itinerary: 每日行程列表，列表中每一项为字典，包含:
            - day: 第几天 (数字)
            - date: 日期 (YYYY-MM-DD，从出发日期推算)
            - weather_summary: 当日天气简要概括（例如：晴转多云，20-25度，适合户外）
            - theme: 当日主题 (可选)
            - activities: 活动列表，列表中每一项为字典，包含:
                - time: 时间 (如 "09:00")
                - activity: 活动描述
                - reason_for_selection: 选择该景点的理由 (结合用户兴趣、体力、天气等因素)
                - location: 地点 (可选)
                - scenic_spot: 核心搜索词 (必填)。请从中提取出最核心、不包含动词的【标准景点名称】或【标准地名】，直接用于高德地图搜索。例如 "游览故宫博物院" -> "故宫博物院"; "前往南昌之星摩天轮" -> "南昌之星"; "在万达广场吃饭" -> "万达广场"。如果是自由活动，填 ""。不要包含"周边"、"附近"等模糊词。
        - accommodation: 住宿建议
        - transportation: 交通建议
        - tips: 实用贴士列表"""

        
        # 构建用户消息
        user_message = "请为我规划旅行"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # 调用API
        # 增加 max_tokens 以防止长行程被截断
        response = self.chat_completion(messages, temperature=0.7, max_tokens=8192)
        
        if "error" in response:
            return response
        
        try:
            # 尝试解析返回的JSON
            content = response["choices"][0]["message"]["content"]
            
            # 使用更稳健的方式提取JSON部分：寻找最外层的 {}
            content = content.strip()
            # 找到第一个 {
            start_idx = content.find('{')
            # 找到最后一个 }
            end_idx = content.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                content = content[start_idx : end_idx + 1]
            else:
                 # 如果找不到完整的 {}, 可能是被截断或者格式完全错误
                 # 尝试一种补救措施：如果找到了 start_idx 没找到 end_idx，可能是截断了
                 if start_idx != -1 and end_idx == -1:
                      # 简单的补全尝试（并不一定有效，但比直接崩溃好）
                      content = content[start_idx:] + '}'
                      # 或者在logs里记录警告
            
            #以此为基础尝试解析
            try:
                 travel_plan = json.loads(content)
            except json.JSONDecodeError as e:
                # 再次尝试清理 Markdown 代码块标记 (应对 some cases where find might capture garbage)
                # 清洗控制字符
                 import re
                 content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
                 # 尝试修复常见的尾部截断导致的问题（极简版）
                 # 真正的修复比较复杂，这里先依赖增加 max_tokens
                 try:
                    travel_plan = json.loads(content)
                 except:
                    # 获取详细的解析错误，用于调试
                    raise e

            travel_plan["status"] = "success"
            travel_plan["generated_by"] = "deepseek"
            
            return travel_plan
            
        except (json.JSONDecodeError, KeyError) as e:
            # 如果JSON解析失败，返回原始内容
            return {
                "status": "partial",
                "raw_content": response.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "error": f"JSON解析失败: {str(e)}"
            }
    
    def get_travel_recommendations(self, 
                                 preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取旅行推荐
        
        Args:
            preferences: 用户偏好
            
        Returns:
            旅行推荐
        """
        system_prompt = """你是一个旅行推荐专家。根据用户的偏好，推荐合适的旅行目的地和方案。
        考虑因素包括：预算、时间、兴趣、季节、旅行节奏、体力水平、交通偏好等。
        重要要求:
        - 输出内容不要使用 Markdown 的加粗符号（即不要出现 **符号）。
        - 请务必推荐 10 个不同的目的地。
        - 推荐时请考虑用户的交通工具偏好，例如用户喜欢自驾，推荐适合自驾的地方；喜欢高铁，推荐高铁直达的地方。
        
        请以JSON格式返回，包含以下字段：
        - recommendations: 推荐列表（共10个，每个推荐包含 destination (目的地)、reason (理由)、suitability_score (适合度评分)）
        - best_match: 最佳匹配目的地名称
        - seasonal_advice: 季节性建议"""
        
        user_message = f"请根据以下偏好推荐旅行目的地：{json.dumps(preferences, ensure_ascii=False)}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = self.chat_completion(messages, temperature=0.8, max_tokens=4000)
        
        if "error" in response:
            return response
        
        try:
            content = response["choices"][0]["message"]["content"]
            content = content.strip()
            
            # 使用更稳健的方式提取JSON部分
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                content = content[start_idx : end_idx + 1]
            
            recommendations = json.loads(content)
            recommendations["status"] = "success"
            
            return recommendations
            
        except (json.JSONDecodeError, KeyError) as e:
            return {
                "status": "partial",
                "raw_content": response.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "error": f"JSON解析失败: {str(e)}"
            }

    def decide_intercity_transport(self, 
                                 origin: str,
                                 destination: str,
                                 distance_km: float,
                                 user_pref: str) -> Dict[str, Any]:
        """
        AI思考并决定跨城交通方式
        """
        prompt = f"""作为一个专业的旅行顾问，请为用户分析从 {origin} 到 {destination} 的最佳交通方式。
        
        上下文信息:
        - 距离: {distance_km} 公里
        - 用户偏好: {user_pref} (注意：这是用户在目的地游玩时的偏好，跨城交通请综合考虑距离、时长、可行性与性价比，从专业角度决策)

        请从以下选项中选择一个最合适的模式 (recommended_mode):
        - driving (自驾)
        - transit (高铁/火车/长途客运)
        - flight (飞机)
        
        并给出简短的推荐理由 (reason)。

        请以JSON格式返回:
        {{
            "recommended_mode": "driving" 或 "transit" 或 "flight",
            "reason": "推荐理由..."
        }}
        """
        messages = [{"role": "user", "content": prompt}]
        try:
            response = self.chat_completion(messages, temperature=0.5, max_tokens=500)
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            # 清理
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            if start_idx != -1 and end_idx != -1:
                content = content[start_idx : end_idx + 1]
            
            result = json.loads(content)
            return result
        except:
            # 默认回退逻辑
            if distance_km > 800: mode = "flight"
            elif distance_km > 300: mode = "transit"
            else: mode = "driving"
            return {"recommended_mode": mode, "reason": "AI解析失败，使用距离规则推荐"}
    #判断需要什么工具
    def analyze_tool_needs(self, user_requirements: Dict[str, Any]) -> List[str]:
        """
        分析用户需求，决定需要调用哪些外部工具
        """
        prompt = f"""作为一个智能旅行Agent，请分析以下用户需求，判断需要获取哪些外部信息来辅助规划。
        
        用户需求:
        {json.dumps(user_requirements, ensure_ascii=False)}
        
        可用工具:
        - weather: 查询天气预报 (如果行程涉及未来日期或户外活动)
        - traffic: 查询交通路线 (如果涉及跨城交通或路线规划)
        
        请列出需要调用的工具名称列表。
        仅通过JSON列表返回，例如: ["weather", "traffic"] 或 ["weather"]。
        不要包含其他文本。
        """
        messages = [{"role": "user", "content": prompt}]
        try:
            response = self.chat_completion(messages, max_tokens=100)
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            # 简单清理
            if content.startswith("```"): content = content.split("```")[1]
            if content.startswith("json"): content = content[4:]
            
            tools = json.loads(content.strip())
            return tools if isinstance(tools, list) else ["weather", "traffic"] # 默认全选
        except:
            return ["weather", "traffic"] # 出错时保守起见全选

    def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        try:
            messages = [
                {"role": "system", "content": "你是一个测试助手，只需回复'连接成功'。"},
                {"role": "user", "content": "测试连接"}
            ]
            
            response = self.chat_completion(messages, max_tokens=10)
            
            if "error" in response:
                return {
                    "status": "failed",
                    "error": response["error"]
                }
            
            return {
                "status": "success",
                "message": "API连接正常",
                "response": response
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
