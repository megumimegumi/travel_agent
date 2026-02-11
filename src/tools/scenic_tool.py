import requests
import hashlib # keep import although not used locally in simplified logic
from typing import Dict, Any, Optional
from utils.config import Config

class ScenicTool:
    """景区信息查询工具 (基于高德地图 AMAP API)"""
    
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.amap_api_key  # 复用高德 Key
        self.base_url = "https://restapi.amap.com/v3/place/text"
        
        # 静态地图专用 Key (用户的主 Key)
        self.static_key = self.config.amap_api_key
        # self.static_secret = "..." # 如果需要签名需配合 secret，当前 Key 似乎不需要强制签名

    def _generate_static_map_url(self, location: str, name: str) -> str:
        """生成静态地图 URL"""
        if not location:
            return ""
            
        base_static_url = "https://restapi.amap.com/v3/staticmap"
        
        # 构造参数
        params = {
            "key": self.static_key,
            "location": location,
            "zoom": "17",      # 增加 Zoom 级别以显示更详细的街道/建筑轮廓
            "size": "1024*1024", # 使用 API 允许的最大尺寸 (1024x1024)
            "scale": "2",      # 高清模式 (Retina, 2x scale -> 2048x2048 effective)
            "markers": f"mid,,A:{location}", # 标记中心点
            "labels": f"{name},2,0,16,0xFFFFFF,0x008000:{location}" 
        }
        
        # 拼接最终 URL (移除 sig 签名逻辑)
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_static_url}?{query_string}"
    
    def get_scenic_info(self, keyword: str, city: str = None) -> Optional[Dict[str, Any]]:
        """
        查询景区信息
        Args:
            keyword: 景区关键词
            city: 城市名称 (可选)
        """
        if not keyword:
            return None
            
        # 清理关键词
        clean_word = keyword.replace("游览", "").replace("前往", "").replace("参观", "").strip()
        if not clean_word:
            clean_word = keyword
            
        params = {
            "key": self.api_key,
            "keywords": clean_word,
            "extensions": "all",  # 获取详细信息
            "offset": 1,          # 只取第一个
            "page": 1
        }
        if city:
            params["city"] = city
            
        try:
            response = requests.get(self.base_url, params=params, timeout=3)
            data = response.json()
            
            if data.get("status") == "1" and data.get("pois"):
                poi = data["pois"][0]
                
                # 提取并适配字段
                biz_ext = poi.get("biz_ext", {}) if isinstance(poi.get("biz_ext"), dict) else {}
                
                # 价格
                price = biz_ext.get("cost")
                if not price:
                    price = "免费/未知"
                else:
                    price = f"约{price}元"
                
                # 评分/等级
                rating = biz_ext.get("rating")
                type_code = poi.get("type", "")
                level_str = ""
                if rating and isinstance(rating, str) and len(rating) > 0:
                     level_str = f"评分 {rating}"
                else:
                    # 尝试从 type 中提取简短描述 (type 格式通常是 "大类;中类;小类")
                    level_str = type_code.split(";")[-1] if ";" in type_code else type_code
                
                # 简介 (高德 POI 接口没有长文本简介，构造一个基础描述)
                address = poi.get("address", "无详细地址")
                tag = poi.get("tag", "")
                name = poi.get("name", "")
                p_type = poi.get("type", "")
                
                # 尽量丰富描述
                content_parts = []
                
                # 类型描述
                if p_type:
                    # type 字段通常是 "大类;中类;小类"，取最后两个增加描述性
                    type_parts = p_type.split(";")
                    display_type = "-".join(type_parts[-2:]) if len(type_parts) >= 2 else p_type
                    content_parts.append(f"【类型】{display_type}")

                content_parts.append(f"【地址】{address}")
                
                if tag:
                    content_parts.append(f"【标签】{tag}")
                
                if poi.get("tel"):
                    content_parts.append(f"【电话】{poi.get('tel')}")
                
                # 尝试提取更多信息
                if poi.get("business_area"):
                    content_parts.append(f"【商圈】{poi.get('business_area')}")
                
                # 如果有 alias
                if poi.get("alias"):
                    content_parts.append(f"【别名】{poi.get('alias')}")
                
                # 图片提取
                photo_urls = []
                photos = poi.get("photos", [])
                if photos:
                    for p in photos:
                        if isinstance(p, dict) and p.get("url"):
                            photo_urls.append(p.get("url"))

                content = " ".join(content_parts)

                    
                # 营业时间 (高德 v3 text 接口通常不直接返回 opentime)
                open_time = "以现场为准"
                
                # 生成静态地图
                location_coords = poi.get("location", "")
                static_map_url = self._generate_static_map_url(location_coords, name)
                
                return {
                    "name": name,
                    "level": level_str[:15], # 限制长度
                    "price": price,
                    "opentime": open_time,
                    "content": content,
                    "photos": photo_urls,
                    "static_map": static_map_url
                }
                
            return None
        except Exception as e:
            # print(f"Scenic API Warning: {e}") # Debug only
            return None
