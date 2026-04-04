import os
import sys

from backend.database import SessionLocal, DbItinerary, User

def update_user_ids_to_username():
    db = SessionLocal()
    
    try:
        # 获取所有真实用户映射
        users = db.query(User).all()
        user_map = {str(u.id): u.username for u in users}
        
        # 加上刚才默认生成的虚假用户的映射
        user_map.update({
            "user_1": "user_1",
            "user_2": "user_2",
            "user_3": "user_3"
        })
        
        itineraries = db.query(DbItinerary).all()
        count = 0
        for it in itineraries:
            if it.user_id in user_map:
                it.user_id = user_map[it.user_id]
                count += 1
                
        db.commit()
        print(f"成功！已将 {count} 条记录的 user_id 从数字ID替换为真实的用户名。")
        
        # 验证修改
        records = db.query(DbItinerary).limit(5).all()
        print("--- 数据库里的前5条记录展示 (已更新) ---")
        for r in records:
            print(f"用户: {r.user_id}, 目的地: {r.destination}")
            
    except Exception as e:
        db.rollback()
        print(f"发生错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_user_ids_to_username()
