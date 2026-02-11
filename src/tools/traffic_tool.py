import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from utils.config import Config

class TrafficTool:
    """交通路线规划工具 (基于高德地图 API，增强版)"""
    
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.amap_api_key
        self.base_url_v3 = "https://restapi.amap.com/v3"
        self.base_url_v4 = "https://restapi.amap.com/v4"
    
    def check_is_peak_hour(self, current_time: datetime = None) -> bool:
        """判断是否为高峰期 (7-9am, 5-7pm)"""
        if not current_time:
            current_time = datetime.now()
        
        hour = current_time.hour
        is_morning_peak = 7 <= hour < 9
        is_evening_peak = 17 <= hour < 19
        
        return is_morning_peak or is_evening_peak

    def estimate_travel_time(self, expected_duration_sec: int, current_time_str: str = None) -> int:
        """
        估算实际通行时间 (考虑拥堵系数)
        Args:
            expected_duration_sec: 正常通行所需的秒数
            current_time_str: "YYYY-MM-DD HH:MM"
        """
        if not current_time_str:
            return expected_duration_sec
        
        try:
            dt = datetime.fromisoformat(current_time_str)
            if self.check_is_peak_hour(dt):
                # 高峰期拥堵系数 1.5 - 2.0
                return int(expected_duration_sec * 1.8)
        except:
            pass
            
        return expected_duration_sec

    def get_coordinates(self, address: str, city: str = None) -> Optional[Tuple[str, str]]:
        """获取地址经纬度"""
        try:
            url = f"{self.base_url_v3}/geocode/geo"
            params = {
                "address": address,
                "key": self.api_key,
                "output": "json"
            }
            if city:
                params["city"] = city
                
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "1" and data.get("geocodes"):
                location = data["geocodes"][0]["location"]
                lon, lat = location.split(",")
                return lon, lat
            return None
        except Exception as e:
            print(f"获取坐标失败: {e}")
            return None

    def get_route_planning(self, origin: str, destination: str, mode: str = "driving", city: str = None) -> Dict[str, Any]:
        """
        获取路径规划
        
        Args:
            origin: 出发地名称
            destination: 目的地名称
            mode: 交通方式 (driving, transit, walking, bicycling)
            city: 城市名称 (用于限定坐标搜索范围，以及公交规划必填)
        """
        # 1. 获取起终点坐标 (使用city参数限定范围，提高准确度)
        origin_coords = self.get_coordinates(origin, city)
        dest_coords = self.get_coordinates(destination, city)
        
        if not origin_coords or not dest_coords:
            return {"error": f"无法获取起终点坐标: {origin} -> {destination} (城市: {city})"}
            
        origin_str = f"{origin_coords[0]},{origin_coords[1]}"
        dest_str = f"{dest_coords[0]},{dest_coords[1]}"
        
        try:
            if mode == "driving":
                url = f"{self.base_url_v3}/direction/driving"
                params = {
                    "origin": origin_str,
                    "destination": dest_str,
                    "key": self.api_key,
                    "extensions": "base"
                }
            elif mode == "walking":
                url = f"{self.base_url_v3}/direction/walking"
                params = {
                    "origin": origin_str,
                    "destination": dest_str,
                    "key": self.api_key
                }
            elif mode == "bicycling":
                url = f"{self.base_url_v4}/direction/bicycling"
                params = {
                    "origin": origin_str,
                    "destination": dest_str,
                    "key": self.api_key
                }
            elif mode == "transit":
                if not city:
                    city = origin # 默认起点城市
                url = f"{self.base_url_v3}/direction/transit/integrated"
                params = {
                    "origin": origin_str,
                    "destination": dest_str,
                    "city": city,
                    "key": self.api_key
                }
            else:
                return {"error": f"不支持的交通方式: {mode}"}

            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "1" or (mode == "bicycling" and data.get("errcode") == 0):
                return self._parse_route_result(data, mode)
            else:
                return {"error": f"路径规划失败: {data.get('info') or data.get('errmsg')}"}
                
        except Exception as e:
            return {"error": f"API请求异常: {str(e)}"}

    def _parse_route_result(self, data: Dict, mode: str) -> Dict[str, Any]:
        """解析路径规划结果"""
        result = {"mode": mode}
        
        # 不同的API返回结构略有不同
        if mode == "bicycling":
            paths = data.get("data", {}).get("paths", [])
        else:
            route = data.get("route", {})
            if mode == "transit":
                paths = route.get("transits", [])
            else:
                paths = route.get("paths", [])
                
        if not paths:
            return {"error": "未找到可行路线"}
            
        # 取第一条方案
        path = paths[0]
        
        # 距离和时间
        distance_m = int(path.get("distance", 0))
        duration_s = int(path.get("duration", 0))
        
        result["distance_km"] = round(distance_m / 1000, 1)
        result["duration_minutes"] = round(duration_s / 60)
        
        # 格式化时间显示
        hours = result["duration_minutes"] // 60
        mins = result["duration_minutes"] % 60
        time_str = ""
        if hours > 0:
            time_str += f"{hours}小时"
        if mins > 0:
            time_str += f"{mins}分钟"
        result["duration_text"] = time_str if time_str else "少于1分钟"
        
        # 费用 (部分模式有)
        if "taxi_cost" in data.get("route", {}):
            result["taxi_cost"] = data["route"]["taxi_cost"]
        if "cost" in path:
            result["transit_cost"] = path["cost"]
            
        return result    
    def calculate_distance(self, origin_city: str, destination_city: str) -> float:
        """
        计算两地直线距离 (km)
        简单估算，用于判断长途出行方式
        """
        coord1 = self.get_coordinates(origin_city)
        coord2 = self.get_coordinates(destination_city)
        
        if not coord1 or not coord2:
            return -1
        
        # 使用高德距离测量 API
        try:
            url = f"{self.base_url_v3}/distance"
            params = {
                "origins": f"{coord1[0]},{coord1[1]}",
                "destination": f"{coord2[0]},{coord2[1]}",
                "type": 0, # 直线距离
                "key": self.api_key
            }
            res = requests.get(url, params=params, timeout=5)
            data = res.json()
            if data.get("status") == "1":
                return int(data["results"][0]["distance"]) / 1000
            return -1
        except:
            return -1