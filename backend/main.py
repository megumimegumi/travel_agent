from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import sys
import os
import traceback

# Add src to path to import existing modules
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from models import TravelRequest, Itinerary
from agents.planning_agent import PlanningAgent
from agents.guide_agent import GuideAgent
from agents.recommendation_agent import RecommendationAgent
from tools.weather_tool import WeatherTool
from tools.traffic_tool import TrafficTool
from tools.scenic_tool import ScenicTool
from services.deepseek_client import DeepSeekClient
from backend.database import SessionLocal, DbItinerary, User, init_db
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="Travel Agent API")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Models for API ---
class RecommendationRequest(BaseModel):
    user_profile: Dict[str, Any]
    requirements: str

class ItinerarySaveRequest(BaseModel):
    user_id: str
    itinerary_data: Dict[str, Any] # 完整的 itinerary json

class ItineraryActionRequest(BaseModel):
    itinerary_id: int
    action: str # "favorite", "unfavorite", "delete"

class SimulationRequest(BaseModel):
    itinerary: Dict[str, Any]
    event_description: str
    current_request: Dict[str, Any]

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResetPassword(BaseModel):
    username: str
    email: str
    new_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- Initialization ---
@app.on_event("startup")
def startup_event():
    init_db()

# --- Auth Endpoints ---

@app.post("/api/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check username
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    # Check email
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"status": "success", "username": new_user.username}

@app.post("/api/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    return {"status": "success", "username": db_user.username, "user_id": str(db_user.id)}

@app.post("/api/auth/reset-password")
def reset_password(req: UserResetPassword, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == req.username, User.email == req.email).first()
    if not db_user:
         raise HTTPException(status_code=404, detail="User not found matching these credentials")
    
    db_user.hashed_password = get_password_hash(req.new_password)
    db.commit()
    return {"status": "success", "message": "Password updated"}

# --- Endpoints ---

@app.get("/api/tools/scenic_info")
def get_scenic_info(keyword: str, city: str = None):
    tool = ScenicTool()
    info = tool.get_scenic_info(keyword, city)
    return info if info else {"error": "Not found"}

@app.post("/api/plan/generate")
async def generate_plan(request: TravelRequest):
    try:
        # 1. Initialize Tools
        deepseek = DeepSeekClient()
        weather_tool = WeatherTool()
        traffic_tool = TrafficTool()
        planner = PlanningAgent()
        
        # 2. Analyze tool needs (simplified AIR loop for backend)
        req_dict = request.dict()
        needed_tools = deepseek.analyze_tool_needs(req_dict)
        
        weather_ctx = ""
        route_ctx = ""
        
        # 3. Gather Context
        if "weather" in needed_tools:
            w_data = weather_tool.get_forecast(request.destination)
            if "error" not in w_data:
                forecast = w_data.get('forecast', [])
                # Take first N days roughly
                weather_ctx = f"未来天气预测: " + "; ".join([f"{d['date']}: {d['description']}, {d['temperature']}" for d in forecast[:request.days]])
        
        if "traffic" in needed_tools:
             dist_km = traffic_tool.calculate_distance(request.origin, request.destination)
             decision = deepseek.decide_intercity_transport(request.origin, request.destination, dist_km, "ai_decide")
             mode = decision.get("recommended_mode", "driving")
             route_ctx = f"建议跨城交通: {mode}。距离 {dist_km}km。"

        # 4. Generate Plan
        itinerary = planner.run(request, weather_info=weather_ctx, route_info=route_ctx)
        return itinerary
        
    except Exception as e:
        print(f"Error generating plan: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plan/simulate")
async def simulate_event(req: SimulationRequest):
    try:
        # 重构必要对象以调用 GuideAgent
        # 这里简化处理：直接使用 PlanningAgent 重新规划，模拟 Guide 的决策结果为 REPLAN
        # 在完整版中，应该先调用 GuideAgent.reflect_and_act 判断是否需要重规划
        
        # 1. 简易 Reflection
        guide = GuideAgent()
        # Mock Context (在真实场景中应从前端传入完整 TravelState)
        # 这里我们直接构造一个假定需要重规划的场景
        
        # 2. Action: 触发重规划
        planner = PlanningAgent()
        
        # 重构 TravelRequest 对象
        req_data = req.current_request
        # 如果是 Pydantic model dump 出来的，可能是 dict
        if isinstance(req_data, dict):
            # 确保枚举值正确
            from models import FitnessLevel, TravelPace
            # 简单的枚举转换尝试，失败则用默认值
            try:
                if 'fitness_level' in req_data: req_data['fitness_level'] = FitnessLevel(req_data['fitness_level'])
                if 'pace' in req_data: req_data['pace'] = TravelPace(req_data['pace'])
            except:
                pass
            travel_req = TravelRequest(**req_data)
        else:
            travel_req = req_data
            
        # 3. Re-run Planner
        # 直接将突发事件描述传递给 Agent，让其作为修正指令处理
        # 使用 weather_info 传递天气相关的突发状况
        
        weather_context = "正常"
        # 简单的关键字检测，辅助 Agent 判断 (但主要依靠 Feedback)
        if any(keyword in req.event_description for keyword in ["雨", "雪", "台风", "雾", "热", "冷", "温"]):
             weather_context = f"【突发天气变化】{req.event_description}"

        feedback = f"""
        发生突发状况: "{req.event_description}"。
        请重新规划行程以适应这一变化。
        如果突发状况涉及特定日期的天气变化（如"第二天有雨"），请务必更新该日 `daily_plans` 中的 `weather_summary` 字段为新的天气状况（例如 "有雨" 或 "大雨转阴"）。
        如果某个活动因突发状况无法进行，请替换为合适的替代活动。
        """
        
        new_itinerary = planner.run(
            travel_req, 
            weather_info=weather_context, 
            feedback=feedback
        )
        
        return {
            "status": "replanned",
            "message": "AI 已根据突发事件调整了行程",
            "new_itinerary": new_itinerary
        }
        
    except Exception as e:
        print(f"Simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend/destinations")
async def recommend_destinations(req: RecommendationRequest):
    try:
        agent = RecommendationAgent()
        result = agent.recommend(req.user_profile, req.requirements)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/itineraries/{user_id}")
async def get_my_itineraries(user_id: str, db: Session = Depends(get_db)):
    # 获取“我的行程” (is_saved=True)
    itineraries = db.query(DbItinerary).filter(
        DbItinerary.user_id == user_id,
        DbItinerary.is_saved == True
    ).order_by(DbItinerary.created_at.desc()).all()
    return itineraries

@app.get("/api/favorites/{user_id}")
async def get_my_favorites(user_id: str, db: Session = Depends(get_db)):
    # 获取“我的收藏” (is_favorite=True)
    favorites = db.query(DbItinerary).filter(
        DbItinerary.user_id == user_id,
        DbItinerary.is_favorite == True
    ).order_by(DbItinerary.created_at.desc()).all()
    return favorites

@app.post("/api/itineraries/save")
async def save_itinerary(req: ItinerarySaveRequest, db: Session = Depends(get_db)):
    data = req.itinerary_data
    # 解析关键字段用于索引
    req_info = data.get('request', {})
    
    db_item = DbItinerary(
        user_id=req.user_id,
        destination=req_info.get('destination', 'Unknown'),
        start_date=req_info.get('start_date', ''),
        days=req_info.get('days', 1),
        total_cost=data.get('total_cost_estimate', 0),
        content_json=data,
        is_saved=True,
        is_favorite=False
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"status": "success", "id": db_item.id}

@app.post("/api/itineraries/{itin_id}/action")
async def update_itinerary_status(itin_id: int, req: ItineraryActionRequest, db: Session = Depends(get_db)):
    item = db.query(DbItinerary).filter(DbItinerary.id == itin_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Itinerary not found")
        
    if req.action == "favorite":
        item.is_favorite = True
    elif req.action == "unfavorite":
        item.is_favorite = False
    elif req.action == "delete":
        item.is_saved = False
        item.is_favorite = False # 彻底移除
        
    db.commit()
    return {"status": "updated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
