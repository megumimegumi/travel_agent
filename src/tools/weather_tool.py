# travel_agent_project/src/tools/weather_tool.py
import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from utils.config import Config

class WeatherTool:
    """天气查询工具 (基于和风天气 QWeather API)"""
    
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.qweather_api_key
        # 用户提供的这套凭证信息经测试仍然是走专属代理通道
        self.base_host = "https://mt3dn8ycec.re.qweatherapi.com"
        self.geo_host = "https://mt3dn8ycec.re.qweatherapi.com/geo"
        
    def _get_location_id(self, city_name: str) -> Optional[str]:
        """获取城市Location ID"""
        try:
            # 使用对应环境的 GeoAPI Host
            url = f"{self.geo_host}/v2/city/lookup"
            params = {
                "location": city_name,
                "key": self.api_key,
                "range": "cn" # 优先搜索中国城市
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("code") == "200" and data.get("location"):
                return data["location"][0]["id"]
                
            return None
        except Exception as e:
            print(f"获取城市ID失败: {e}")
            return None

    def get_weather(self, destination: str, date_str: Optional[str] = None) -> Dict[str, Any]:
        """获取实时天气信息"""
        location_id = self._get_location_id(destination)
        if not location_id:
            return {"error": "未找到该城市信息", "destination": destination}
            
        try:
            # 获取实时天气 /v7/weather/now
            url = f"{self.base_host}/v7/weather/now"
            params = {
                "location": location_id,
                "key": self.api_key
            }
            
            # 调试输出
            # print(f"DEBUG: Requesting {url} with params {params}")
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("code") != "200":
                return {"error": f"API返回错误: {data.get('code')}", "destination": destination}
                
            now = data["now"]
            temp = float(now["temp"])
            season = self._get_season_by_month(datetime.now().month)
            
            result = {
                "destination": destination,
                "date": date_str if date_str else datetime.now().strftime("%Y-%m-%d"),
                "temperature": f"{now['temp']}°C",
                "description": now["text"],
                "humidity": f"{now['humidity']}%",
                "wind_speed": f"{now['windDir']} {now['windScale']}级",
                "season": season,
                "recommendation": self._get_clothing_recommendation(temp),
                "feels_like": f"{now['feelsLike']}°C",
                "vis": f"{now['vis']}km"
            }
            
            # 尝试获取今日更多信息 /v7/weather/3d
            try:
                daily_url = f"{self.base_host}/v7/weather/3d"
                daily_res = requests.get(daily_url, params=params, timeout=5)
                daily_data = daily_res.json()
                if daily_data.get("code") == "200":
                    today = daily_data["daily"][0]
                    result["temp_max"] = f"{today['tempMax']}°C"
                    result["temp_min"] = f"{today['tempMin']}°C"
                    result["sunrise"] = today["sunrise"]
                    result["sunset"] = today["sunset"]
                    result["uv_index"] = today.get("uvIndex", "N/A")
            except:
                pass

            return result
            
        except Exception as e:
            return {"error": f"API请求失败: {str(e)}", "destination": destination}

    def get_forecast(self, destination: str) -> Dict[str, Any]:
        """获取天气预报"""
        location_id = self._get_location_id(destination)
        if not location_id:
            return {"error": "未找到该城市信息"}
            
        try:
            # 优先尝试7天 /v7/weather/7d
            url = f"{self.base_host}/v7/weather/7d"
            params = {"location": location_id, "key": self.api_key}
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            # 降级尝试3天
            if data.get("code") != "200":
                url = f"{self.base_host}/v7/weather/3d"
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
            
            if data.get("code") != "200":
                return {"error": f"无法获取预报: {data.get('code')}"}
                
            daily_list = data.get("daily", [])
            forecast_list = []
            
            for day in daily_list:
                desc = day["textDay"]
                if day["textDay"] != day["textNight"]:
                    desc += f"转{day['textNight']}"
                    
                forecast_list.append({
                    "date": day["fxDate"],
                    "temperature": f"{day['tempMin']}~{day['tempMax']}°C",
                    "description": desc,
                    "uv_index": day.get("uvIndex", "-"),
                    "humidity": day.get("humidity", "-")
                })
            
            return {"destination": destination, "forecast": forecast_list}
            
        except Exception as e:
            return {"error": str(e)}

    def get_hourly_forecast(self, destination: str) -> Dict[str, Any]:
        """获取24小时预报"""
        location_id = self._get_location_id(destination)
        if not location_id:
            return {"error": "未找到该城市信息"}
        try:
            # /v7/weather/24h
            url = f"{self.base_host}/v7/weather/24h"
            params = {"location": location_id, "key": self.api_key}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("code") != "200":
                return {"error": f"无法获取逐小时预报: {data.get('code')}"}
                
            hourly_list = []
            for item in data.get("hourly", []):
                # fxTime: 2023-01-01T12:00+08:00
                time_str = item["fxTime"].split("T")[1][:5]
                hourly_list.append({
                    "time": time_str,
                    "temperature": f"{item['temp']}°C",
                    "description": item["text"],
                    "precip_prob": f"{item.get('pop', '0')}%"
                })
            return {"destination": destination, "hourly": hourly_list}
        except Exception as e:
            return {"error": str(e)}

    def get_season(self, date_str: Optional[str] = None) -> str:
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                month = date_obj.month
            except:
                month = datetime.now().month
        else:
            month = datetime.now().month
        return self._get_season_by_month(month)

    def _get_season_by_month(self, month: int) -> str:
        if 3 <= month <= 5: return "春季"
        elif 6 <= month <= 8: return "夏季"
        elif 9 <= month <= 11: return "秋季"
        else: return "冬季"

    def _get_clothing_recommendation(self, temp: float) -> str:
        if temp >= 30: return "天气炎热，建议穿着轻薄透气的夏装，注意防晒。"
        elif temp >= 20: return "舒适温暖，建议穿着短袖或薄长袖，早晚可加薄外套。"
        elif temp >= 10: return "天气较凉，建议穿着毛衣、风衣或夹克。"
        elif temp >= 0: return "天气寒冷，建议穿着棉服、羽绒服等保暖衣物。"
        else: return "严寒天气，请穿着厚羽绒服，注意保暖防冻。"
