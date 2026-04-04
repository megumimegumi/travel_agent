import random
from datetime import datetime, timedelta
from backend.database import SessionLocal, DbItinerary, User

def generate_records():
    db = SessionLocal()
    
    try:
        # 首先尝试从 users 表查询所有用户 (前端注册的真实用户)
        db_users = db.query(User).all()
        user_ids = [str(u.id) for u in db_users]
        
        # 如果 users 表是空的，尝试从现有的 itineraries 表中获取已经存在的模拟用户 ID
        if not user_ids:
            itineraries = db.query(DbItinerary).all()
            user_ids = list(set([it.user_id for it in itineraries if it.user_id]))
            
        if not user_ids:
            print("没有在数据库中找到任何用户。使用默认的三个测试用户。")
            user_ids = ["user_1", "user_2", "user_3"]
            
        print(f"在数据库中找到了以下用户: {user_ids}")
        
        destinations = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "重庆", "西安", "武汉", "三亚", "拉萨", "青岛", "厦门", "昆明"]
        
        new_records = []
        for uid in user_ids:
            print(f"正在为用户 {uid} 生成 7 条随机真实感的旅行记录...")
            for i in range(7):
                dest = random.choice(destinations)
                days = random.randint(2, 7)
                cost = days * random.randint(500, 2000) # 每天开销 500-2000 不等
                
                # 随机生成过去的日期
                days_ago = random.randint(10, 365)
                start_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                
                record = DbItinerary(
                    user_id=uid,
                    destination=dest,
                    start_date=start_date,
                    days=days,
                    total_cost=cost,
                    is_saved=random.choice([True, False]),
                    is_favorite=random.choice([True, False])
                )
                new_records.append(record)
                
        db.add_all(new_records)
        db.commit()
        print(f"\n成功！共为 {len(user_ids)} 个用户生成了 {len(new_records)} 条记录，并已存入数据库。")
        
    except Exception as e:
        db.rollback()
        print(f"发生错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_records()
