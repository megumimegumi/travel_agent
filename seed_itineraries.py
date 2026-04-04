from backend.database import SessionLocal, DbItinerary, engine, Base
from datetime import datetime

# 确保表已经创建
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # 插入10条模拟数据
    mock_data = [
        DbItinerary(user_id="user_1", destination="东京", start_date="2026-05-01", days=5, total_cost=5000, is_saved=True, is_favorite=True),
        DbItinerary(user_id="user_1", destination="京都", start_date="2026-06-15", days=3, total_cost=3000, is_saved=True, is_favorite=False),
        DbItinerary(user_id="user_2", destination="巴黎", start_date="2026-07-20", days=7, total_cost=15000, is_saved=True, is_favorite=True),
        DbItinerary(user_id="user_2", destination="伦敦", start_date="2026-08-10", days=5, total_cost=12000, is_saved=False, is_favorite=False),
        DbItinerary(user_id="user_1", destination="纽约", start_date="2026-09-05", days=4, total_cost=8000, is_saved=True, is_favorite=False),
        DbItinerary(user_id="user_3", destination="悉尼", start_date="2026-10-01", days=6, total_cost=10000, is_saved=True, is_favorite=True),
        DbItinerary(user_id="user_1", destination="罗马", start_date="2026-11-12", days=5, total_cost=9000, is_saved=False, is_favorite=True),
        DbItinerary(user_id="user_2", destination="巴塞罗那", start_date="2026-12-20", days=4, total_cost=7500, is_saved=True, is_favorite=False),
        DbItinerary(user_id="user_3", destination="迪拜", start_date="2027-01-10", days=5, total_cost=15000, is_saved=True, is_favorite=True),
        DbItinerary(user_id="user_1", destination="新加坡", start_date="2027-02-14", days=3, total_cost=4500, is_saved=True, is_favorite=False),
    ]
    
    try:
        db.add_all(mock_data)
        db.commit()
        print("10条行程数据已成功插入到数据库！")
    except Exception as e:
        db.rollback()
        print(f"插入数据时发生错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
