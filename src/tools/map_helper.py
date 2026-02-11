import requests
from typing import Optional, Tuple
from utils.config import Config

class MapHelper:
    """地图辅助工具类，提供坐标查询和静态地图生成"""
    
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.amap_api_key

    def get_coordinates(self, address: str, city: str = None) -> Optional[Tuple[str, str]]:
        """获取地址坐标 (lon, lat)"""
        if not address:
            return None
        
        url = "https://restapi.amap.com/v3/geocode/geo"
        params = {
            "key": self.api_key,
            "address": address
        }
        if city:
            params["city"] = city
            
        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            if data.get("status") == "1" and data.get("geocodes"):
                # location is "lon,lat"
                location = data["geocodes"][0]["location"]
                parts = location.split(",")
                if len(parts) == 2:
                    return (parts[0], parts[1])
        except Exception:
            return None
        return None

    def get_static_map_url(self, location_name: str, city: str = None) -> str:
        """获取静态地图 URL"""
        coords = self.get_coordinates(location_name, city)
        if coords:
            return f"https://restapi.amap.com/v3/staticmap?location={coords[0]},{coords[1]}&zoom=14&size=400*300&markers=mid,,A:{coords[0]},{coords[1]}&key={self.api_key}"
        return ""

