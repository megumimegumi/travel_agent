from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
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
from backend.database import SessionLocal, DbItinerary, User, UserEvaluation, init_db
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

class RevisionRequest(BaseModel):
    original_request: TravelRequest
    current_plan: Dict[str, Any]
    user_feedback: str

class ItinerarySaveRequest(BaseModel):
    user_id: str
    itinerary_data: Dict[str, Any] # 完整的 itinerary json

class ItineraryActionRequest(BaseModel):
    itinerary_id: int
    action: str # "favorite", "unfavorite", "delete"

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
    
    # 修改：返回 user_id 直接设定为 username，而不是数据库生成的数字 id
    return {"status": "success", "username": db_user.username, "user_id": db_user.username}

@app.post("/api/auth/reset-password")
def reset_password(req: UserResetPassword, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == req.username, User.email == req.email).first()
    if not db_user:
         raise HTTPException(status_code=404, detail="User not found matching these credentials")
    
    db_user.hashed_password = get_password_hash(req.new_password)
    db.commit()
    return {"status": "success", "message": "Password updated"}

# --- Endpoints ---

class ReviseRequest(BaseModel):
    original_request: TravelRequest
    current_plan: Dict[str, Any]
    user_feedback: str

@app.get("/api/tools/scenic_info")
def get_scenic_info(keyword: str, city: str = None):
    tool = ScenicTool()
    info = tool.get_scenic_info(keyword, city)
    return info if info else {"error": "Not found"}

@app.post("/api/plan/generate")
async def generate_plan(request: TravelRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        print(f"[Generate Plan] Received request for user_id: {request.user_id}")
        
        user_history_str = ""
        if request.user_id:
            # 读取历史行程
            recent_plans = db.query(DbItinerary).filter(DbItinerary.user_id == request.user_id).order_by(DbItinerary.created_at.desc()).limit(5).all()
            if recent_plans:
                history_list = []
                for idx, plan in enumerate(recent_plans):
                    pace_info = plan.pace or "未知"
                    travelers_info = plan.travelers or "未知"
                    tags_info = plan.tags or "无"
                    history_list.append(
                        f"{idx+1}. 曾在 {plan.start_date or '未知'} 前往: {plan.destination}, "
                        f"时长: {plan.days}天, 预算: {plan.total_cost}元, "
                        f"出行人物: {travelers_info}, 游玩节奏: {pace_info}, 偏好标签: {tags_info}"
                    )
                user_history_str = "【历史行程记录】\n过去5次的旅行：\n" + "\n".join(history_list) + "\n"

            # 读取用户评价画像（新增表）
            user_eval = db.query(UserEvaluation).filter(UserEvaluation.user_id == request.user_id).first()
            if user_eval:
                eval_str = ""
                if user_eval.recent_evaluation:
                    eval_str += f"[近期偏好评价]: {user_eval.recent_evaluation}\n"
                if user_eval.long_term_evaluation:
                    eval_str += f"[长期画像总结]: {user_eval.long_term_evaluation}\n"
                
                if eval_str:
                    user_history_str = "【AI用户画像】\n" + eval_str + "\n" + user_history_str
            else:
                if user_history_str:
                    user_history_str = "【AI用户画像】\n暂无明确评价，请根据以下历史记录推断。\n" + user_history_str

        # 2. Initialize Tools
        deepseek = DeepSeekClient()
        weather_tool = WeatherTool()
        traffic_tool = TrafficTool()
        planner = PlanningAgent()
        
        # 3. Analyze tool needs (simplified AIR loop for backend)
        req_dict = request.dict()
        needed_tools = deepseek.analyze_tool_needs(req_dict)
        
        weather_ctx = ""
        route_ctx = ""
        
        # 4. Gather Context
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

        # 5. Generate Plan，传入用户的历史数据记忆
        itinerary = planner.run(request, weather_info=weather_ctx, route_info=route_ctx, user_history=user_history_str)
        
        return itinerary
        
    except Exception as e:
        print(f"Error generating plan: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

import json
import os

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage")
os.makedirs(STORAGE_DIR, exist_ok=True)

def update_user_evaluation_in_bg(user_id: str):
    db: Session = SessionLocal()
    try:
        print(f"[Update Evaluation] Starting background update for user {user_id}...")
        
        # 查询近期与所有已保存的行程
        recent_plans = db.query(DbItinerary).filter(DbItinerary.user_id == user_id, DbItinerary.is_saved == True).order_by(DbItinerary.created_at.desc()).limit(5).all()
        all_plans = db.query(DbItinerary).filter(DbItinerary.user_id == user_id, DbItinerary.is_saved == True).order_by(DbItinerary.created_at.desc()).limit(20).all()
        
        if not recent_plans:
            print("[Update Evaluation] No saved plans found, clearing evaluation.")
            user_eval = db.query(UserEvaluation).filter(UserEvaluation.user_id == user_id).first()
            if user_eval:
                db.delete(user_eval)
                db.commit()
            return

        recent_list = [f"前往:{p.destination}, {p.days}天, 预算{p.total_cost}元, 人物:{p.travelers}, 节奏:{p.pace}, 标签:{p.tags}" for p in recent_plans]
        all_list = [f"于{p.start_date or '未知'}前往:{p.destination}, {p.days}天, 预算{p.total_cost}元, 人物:{p.travelers}, 节奏:{p.pace}, 标签:{p.tags}" for p in all_plans]

        deepseek = DeepSeekClient()
        recent_prompt = [{"role": "user", "content": "这是该用户最近5次的旅行记录：\n" + "\n".join(recent_list) + "\n\n请用200字以内概括该用户最近的总体游玩偏好，比如消费水平、同行人群、游玩节奏和倾向的兴趣点。请只输出纯文本，绝对不要使用任何Markdown格式符号（如加粗的**符号、标题###等）。"}]
        recent_resp = deepseek.chat_completion(recent_prompt)
        recent_eval = recent_resp.get("choices", [{}])[0].get("message", {}).get("content", "").replace("**", "").replace("###", "")

        long_prompt = [{"role": "user", "content": "这是该用户历史的多条/所有旅行记录：\n" + "\n".join(all_list) + "\n\n请用300字以内提炼该用户的个人画像，包括该用户的消费观念、整体旅行风格以及对目的地的倾向性长期评价。请只输出纯文本，绝对不要使用任何Markdown格式符号（如加粗的**符号、标题###等）。"}]
        long_resp = deepseek.chat_completion(long_prompt)
        long_eval = long_resp.get("choices", [{}])[0].get("message", {}).get("content", "").replace("**", "").replace("###", "")

        # 3. 写回数据库
        user_eval = db.query(UserEvaluation).filter(UserEvaluation.user_id == user_id).first()
        if not user_eval:
            user_eval = UserEvaluation(user_id=user_id, recent_evaluation=recent_eval, long_term_evaluation=long_eval)
            db.add(user_eval)
        else:
            user_eval.recent_evaluation = recent_eval
            user_eval.long_term_evaluation = long_eval
            
        db.commit()
        print(f"[Update Evaluation] Finished properly for user {user_id}")
    except Exception as e:
        print(f"[Update Evaluation] Error: {e}")
    finally:
        db.close()

def fill_itinerary_data(it: DbItinerary):
    item_dict = {
        "id": it.id,
        "user_id": it.user_id,
        "destination": it.destination,
        "start_date": it.start_date,
        "days": it.days,
        "total_cost": it.total_cost,
        "pace": getattr(it, 'pace', ''),
        "travelers": getattr(it, 'travelers', ''),
        "tags": getattr(it, 'tags', ''),
        "is_favorite": it.is_favorite,
        "created_at": it.created_at.isoformat() if it.created_at else None
    }
    file_path = os.path.join(STORAGE_DIR, f"{it.id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            item_dict["content_json"] = json.load(f)
    else:
        # Fallback 模拟结构防止前端报错
        item_dict["content_json"] = {"daily_plans": []}
    return item_dict

@app.post("/api/plan/revise")
async def revise_plan(req: ReviseRequest):
    try:
        planner = PlanningAgent()
        deepseek = DeepSeekClient()

        # Step 1: Detect Intent
        intent_prompt = [
            {"role": "system", "content": "You are an AI assistant helping a user with a travel itinerary. Determine if the user's message is a request to MODIFY the itinerary (e.g., add a day, change hotel, remove a spot) or just a CHAT message (e.g., hello, thank you, asking general questions without modification intent). Return ONLY the word 'MODIFY' or 'CHAT'."},
            {"role": "user", "content": f"User message: {req.user_feedback}"}
        ]
        intent_resp = deepseek.chat_completion(intent_prompt, temperature=0.1)
        intent = intent_resp.get("choices", [{}])[0].get("message", {}).get("content", "").strip().upper()
        
        # If it's just chat, return a simple response
        if "CHAT" in intent and "MODIFY" not in intent:
             chat_prompt = [
                {"role": "system", "content": "You are a helpful travel assistant. Reply to the user's message politely and helpfully. Keep it concise."},
                {"role": "user", "content": req.user_feedback}
             ]
             chat_resp = deepseek.chat_completion(chat_prompt)
             reply = chat_resp.get("choices", [{}])[0].get("message", {}).get("content", "")
             return {"chat_message": reply}

        # Step 2: Proceed with revision if intent is MODIFY
        # 提取原先计划的简要视图
        daily_plans = req.current_plan.get("daily_plans", [])
        plan_summary = json.dumps(daily_plans, ensure_ascii=False)
        
        feedback_str = f"原先的行程（部分或全部）：{plan_summary}。\n\n用户对这个行程的修改意见是：{req.user_feedback}。\n\n请根据用户的修改意见，在原行程的基础上进行调整，并返回完整的行程JSON。"
        
        itinerary = planner.run(request=req.original_request, feedback=feedback_str)
        return itinerary
        
    except Exception as e:
        print(f"Error revising plan: {e}")
        traceback.print_exc()
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
    
    return [fill_itinerary_data(it) for it in itineraries]

@app.get("/api/favorites/{user_id}")
async def get_my_favorites(user_id: str, db: Session = Depends(get_db)):
    # 获取“我的收藏” (is_favorite=True)
    favorites = db.query(DbItinerary).filter(
        DbItinerary.user_id == user_id,
        DbItinerary.is_favorite == True
    ).order_by(DbItinerary.created_at.desc()).all()
    
    return [fill_itinerary_data(it) for it in favorites]

@app.post("/api/itineraries/save")
async def save_itinerary(req: ItinerarySaveRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    data = req.itinerary_data
    # 解析关键字段用于索引
    req_info = data.get('request', {})
    
    interests = req_info.get("interests", [])
    if not interests:
        # 如果用户没有填兴趣，把 AI 规划出来的每天的主题 (theme) 抽取出来当作个性化 tags 记录下来！这样存入库里就不会是空的
        themes = [day.get("theme", "") for day in data.get("daily_plans", []) if day.get("theme")]
        interests = list(set(themes))[:3]
        
    tags_str = ",".join(interests) if isinstance(interests, list) else str(interests)

    db_item = DbItinerary(
        user_id=req.user_id,
        destination=req_info.get('destination', 'Unknown'),
        start_date=req_info.get('start_date', ''),
        days=req_info.get('days', 1),
        total_cost=data.get('total_cost_estimate', 0),
        pace=req_info.get("pace", ""),
        travelers=req_info.get("travelers_relation", ""),
        tags=tags_str,
        is_saved=True,
        is_favorite=False
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # 彻底告别数据库臃肿，将 AI 吐出的大段 JSON 写到本地文件中！
    file_path = os.path.join(STORAGE_DIR, f"{db_item.id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    # 保存后触发更新用户评价表
    background_tasks.add_task(update_user_evaluation_in_bg, req.user_id)

    return {"status": "success", "id": db_item.id}

@app.post("/api/itineraries/{itin_id}/action")
async def update_itinerary_status(itin_id: int, req: ItineraryActionRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    item = db.query(DbItinerary).filter(DbItinerary.id == itin_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Itinerary not found")
        
    user_id = item.user_id

    if req.action == "favorite":
        item.is_favorite = True
        db.commit()
    elif req.action == "unfavorite":
        item.is_favorite = False
        db.commit()
    elif req.action == "delete":
        # 真正从数据库中删除记录，并同步删除 JSON 文件
        try:
            file_path = os.path.join(STORAGE_DIR, f"{item.id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Failed to delete file for {item.id}: {e}")
        
        db.delete(item)
        db.commit()
        
        # 触发重新生成用户评价
        background_tasks.add_task(update_user_evaluation_in_bg, user_id)
        
    return {"status": "updated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
