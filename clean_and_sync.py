import os
import json
import random
from datetime import datetime, timedelta
from backend.database import SessionLocal, User, DbItinerary, UserEvaluation, init_db
from backend.main import update_user_evaluation_in_bg, STORAGE_DIR
import logging

db = SessionLocal()

# 1. Delete test data: deleting any itineraries and evaluations where user_id is not in User table, or user_id starts with 'test'
valid_users = [u.username for u in db.query(User).all()]
print(f"Valid users: {valid_users}")

all_itineraries = db.query(DbItinerary).all()
deleted_its = 0
for it in all_itineraries:
    if it.user_id not in valid_users or 'test' in it.user_id:
        db.delete(it)
        deleted_its += 1
        # also delete file
        fp = os.path.join(STORAGE_DIR, f"{it.id}.json")
        if os.path.exists(fp):
            os.remove(fp)

all_evals = db.query(UserEvaluation).all()
for ev in all_evals:
    if ev.user_id not in valid_users or 'test' in ev.user_id:
        db.delete(ev)
db.commit()
print(f"Deleted {deleted_its} test itineraries.")

# 2. Sync database with storage JSON files
# If an itinerary is_saved=True but no JSON file exists, either set is_saved=False or delete it? Or if JSON file exists but not in DB?
# Better: delete DB row if JSON file is missing for is_saved itineraries, since it's corrupt.
sync_count = 0
db_its = db.query(DbItinerary).all()
for it in db_its:
    if it.is_saved:
        fp = os.path.join(STORAGE_DIR, f"{it.id}.json")
        if not os.path.exists(fp):
            db.delete(it)
            sync_count += 1
db.commit()
print(f"Synced {sync_count} orphaned DB itineraries.")

# 3. Generate 5-10 random historical itineraries for each valid user and trigger evaluation
destinations = ["北京", "上海", "广州", "深圳", "成都", "重庆", "西安", "南京", "苏州", "杭州", "武汉", "长沙", "青岛", "厦门", "昆明", "大理", "丽江", "三亚"]
paces = ["悠闲放松", "适中", "紧凑充实", "深度慢游", "特种兵打卡"]
travelers = ["独自", "情侣", "朋友", "家庭"]
tags_pool = ["人文", "历史", "自然", "美食", "购物", "夜生活", "摄影"]

for u in ['Megumi', '木瓜星灵', 'llll', '码头菩萨']:
    if u not in valid_users: continue
    
    # Check if they already have >= 5 itineraries
    existing_cnt = db.query(DbItinerary).filter_by(user_id=u).count()
    if existing_cnt >= 5:
        print(f"User {u} already has {existing_cnt} itineraries. Regenerating eval...")
        update_user_evaluation_in_bg(u)
        continue

    num_to_gen = random.randint(5, 10)
    print(f"Generating {num_to_gen} itineraries for {u}...")
    
    for _ in range(num_to_gen):
        dest = random.choice(destinations)
        days = random.randint(3, 7)
        cost = random.randint(1500, 5000)
        pace = random.choice(paces)
        traveler = random.choice(travelers)
        tags = ",".join(random.sample(tags_pool, 2))
        
        # Start date within last 6 months
        past_days = random.randint(10, 180)
        start_date = (datetime.now() - timedelta(days=past_days)).strftime("%Y-%m-%d")
        
        new_it = DbItinerary(
            user_id=u,
            destination=dest,
            start_date=start_date,
            days=days,
            total_cost=cost,
            pace=pace,
            travelers=traveler,
            tags=tags,
            is_saved=True,
            is_favorite=random.choice([True, False])
        )
        db.add(new_it)
        db.commit()
        db.refresh(new_it)
        
        # generate a mock JSON
        mock_data = {
            "request": {
                "destination": dest, "start_date": start_date, "days": days,
                "travelers_relation": traveler, "pace": pace, "interests": tags.split(",")
            },
            "daily_plans": [],
            "total_cost_estimate": cost,
            "special_tips": {}
        }
        with open(os.path.join(STORAGE_DIR, f"{new_it.id}.json"), "w", encoding="utf-8") as f:
            json.dump(mock_data, f, ensure_ascii=False)
            
    # Update evaluation
    try:
        update_user_evaluation_in_bg(u)
    except Exception as e:
        print(f"Failed to generated eval for {u}: {e}")

print("Done!")
