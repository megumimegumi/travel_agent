import sys
import os
import random
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.database import engine, SessionLocal, DbItinerary

def alter_and_seed():
    db = SessionLocal()
    try:
        # 直接使用原生 SQL 对 MySQL 进行 Alter 操作，增加三列（捕获异常以防列已存在）
        with engine.begin() as conn:
            for col in ['pace', 'travelers']:
                try:
                    conn.execute(text(f"ALTER TABLE itineraries ADD COLUMN {col} VARCHAR(50);"))
                except Exception as e:
                    print(f"列 {col} 可能已存在跳过: {e}")
            try:
                conn.execute(text("ALTER TABLE itineraries ADD COLUMN tags VARCHAR(200);"))
            except Exception as e:
                print(f"列 tags 可能已存在跳过: {e}")

        # 为数据库中原有的记录（包括 llll的记录）随机赋予个性化的标签
        paces = ["悠闲放松", "适中", "紧凑充实", "深度慢游", "特种兵打卡"]
        travs = ["独自一人", "情侣出行", "亲子游", "朋友结伴", "家庭出游"]
        tags_pool = ["美食猎人", "探寻历史", "拥抱自然", "买买买", "网红打卡", "小众摄影", "艺术看展", "极限探险"]

        records = db.query(DbItinerary).all()
        for r in records:
            if r.user_id == 'llll':
                 # 为你的测试账户 llll 提供符合"土豪"的专属固定设定
                 r.pace = "深度慢游"
                 r.travelers = "情侣出行"
                 r.tags = "奢华尊享,米其林美食,艺术看展"
            else:
                 r.pace = random.choice(paces)
                 r.travelers = random.choice(travs)
                 r.tags = ",".join(random.sample(tags_pool, k=random.randint(1, 3)))
        
        db.commit()
        print("表格结构已轻量化升级，个性化标签注入成功！")

        # 打印展示 llll 账户的个例数据
        llll_recs = db.query(DbItinerary).filter(DbItinerary.user_id == 'llll').all()
        print("\n--- 账号 llll 的个性化记录 ---")
        for rec in llll_recs:
             print(f"目的地: {rec.destination} | 节奏: {rec.pace} | 出行: {rec.travelers} | 标签: {rec.tags} | 预算: {rec.total_cost}元")
        
    except Exception as e:
        print(f"执行出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    alter_and_seed()
