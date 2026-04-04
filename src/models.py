from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import date

class FitnessLevel(str, Enum):
    """体力水平枚举"""
    IRONMAN = "铁人三项"
    ENERGETIC = "精力充沛"
    NORMAL = "普通人"
    TIRED_EASILY = "容易累"
    NO_WALKING = "甚至不想走路"

class TravelPace(str, Enum):
    """旅行节奏枚举"""
    RELAXED = "悠闲放松"
    MODERATE = "适中"
    COMPACT = "紧凑充实"
    DEEP = "深度慢游"
    SOLDIER = "特种兵打卡"

class UserProfile(BaseModel):
    """用户画像：定义用户的长期偏好和属性"""
    name: str = "User"
    age: Optional[int] = None
    fitness_level: FitnessLevel = FitnessLevel.NORMAL
    interests: List[str] = Field(default_factory=list)
    dietary_preferences: List[str] = Field(default_factory=list, description="饮食偏好/禁忌")

class TravelRequest(BaseModel):
    """单次旅行需求：定义本次旅行的具体约束"""
    user_id: Optional[str] = None # 用于关联用户历史数据
    destination: str
    origin: str
    start_date: Optional[str] = None # YYYY-MM-DD
    days: int = 3
    budget: float = 2000.0
    travelers_count: int = 1
    travelers_relation: str = "独自一人"
    pace: TravelPace = TravelPace.MODERATE
    transport_mode_preference: Optional[str] = None
    accommodation_preference: Optional[str] = None
    extra_requirements: str = ""
    interests: List[str] = Field(default_factory=list, description="本次旅行的兴趣偏好")
    dietary_preferences: List[str] = Field(default_factory=list, description="饮食偏好")
    fitness_level: FitnessLevel = FitnessLevel.NORMAL

class ItineraryItem(BaseModel):
    """行程单中的单个活动"""
    time: str
    activity: str
    location: Optional[str] = None
    scenic_spot: Optional[str] = None # 用于API搜索的精准景点名
    description: Optional[str] = None
    cost_estimate: Optional[float] = None
    transport_suggestion: Optional[str] = None

class DailyItinerary(BaseModel):
    """每日行程"""
    day: int
    date: Optional[str] = None
    theme: str
    activities: List[ItineraryItem]
    route_suggestions: List[str] = Field(default_factory=list)
    weather_summary: Optional[str] = None

class Itinerary(BaseModel):
    """完整行程单"""
    request: TravelRequest
    daily_plans: List[DailyItinerary]
    total_cost_estimate: float
    status: str = "draft" # draft, final, in_progress
    created_at: str
    preparation_list: Optional[Dict[str, List[str]]] = None # 准备清单 {Category: [Items]}
    special_tips: Optional[Dict[str, List[str]]] = None     # 特别提示 {Type: [Tips]}

# --- Phase 3: 动态仿真模型 ---

class EventType(str, Enum):
    WEATHER_CHANGE = "weather_change" # 天气突变 (下雨/升温)
    TRAFFIC_JAM = "traffic_jam"       # 交通拥堵
    ATTRACTION_CLOSE = "attraction_closed" # 景点关闭
    DELAY = "delay"                   # 交通/航班延误
    USER_CHANGE = "user_change"       # 用户主观变更 (累了/饿了)

class SimulationEvent(BaseModel):
    """环境模拟事件"""
    type: EventType
    description: str
    impact_level: str = "medium" # low, medium, high
    start_time: Optional[str] = None # 发生时间 
    duration_hours: Optional[float] = None

class TravelState(BaseModel):
    """当前旅行状态 (Context)"""
    current_time: str # ISO format YYYY-MM-DD HH:MM
    current_location: str
    current_weather: str = "晴朗"
    completed_activities: List[str] = [] # 已完成的 activity identifiers
    remaining_budget: float

class TravelSession(BaseModel):
    """旅行会话：维护整个动态过程"""
    session_id: str
    request: TravelRequest
    itinerary: Itinerary
    state: TravelState
    history: List[str] = [] # Action log
