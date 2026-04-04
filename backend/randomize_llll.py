import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.database import SessionLocal, DbItinerary

def randomize_llll_data():
    db = SessionLocal()
    try:
        # 查询 llll 的所有行程记录
        llll_recs = db.query(DbItinerary).filter(DbItinerary.user_id == 'llll').all()
        
        if not llll_recs:
            print("没有找到 llll 账号的记录。")
            return

        # 准备一些不同情境的模板，让数据更像一个活生生的人
        personas = [
            {"pace": "深度慢游", "travelers": "情侣出行", "tags": "奢华尊享,米其林美食,艺术看展", "cost_multiplier": 2000}, # 奢华情侣游
            {"pace": "紧凑充实", "travelers": "独自一人", "tags": "历史人文,城市漫步,摄影", "cost_multiplier": 800},     # 独自出差/扫街
            {"pace": "悠闲放松", "travelers": "朋友结伴", "tags": "买买买,网红打卡,探店", "cost_multiplier": 1200},     # 和闺蜜/哥们逛吃
            {"pace": "适中", "travelers": "家庭出游", "tags": "自然风光,亲子漫游,度假村", "cost_multiplier": 1500},       # 带家人去玩
            {"pace": "特种兵打卡", "travelers": "独自一人", "tags": "徒步,小众探险,极限运动", "cost_multiplier": 500}       # 偶尔疯一把
        ]

        print("正在为账号 llll 重新洗牌历史数据...\n")
        
        for rec in llll_recs:
            # 随机选择一种出行情景，但可以保留一定几率是其偏向的高端游
            weights = [0.4, 0.15, 0.2, 0.15, 0.1] # 40%概率还是高端情侣游，其他拆分
            persona = random.choices(personas, weights=weights, k=1)[0]
            
            rec.pace = persona["pace"]
            rec.travelers = persona["travelers"]
            # 也可以稍微给 tags 增加点随机性突变
            rec.tags = persona["tags"]
            
            # 相关花费也根据新的人设波动一下
            rec.total_cost = rec.days * (persona["cost_multiplier"] + random.randint(-200, 500))

        db.commit()

        # 打印展示
        print("--- 账号 llll 的多样化个性记录（更新后） ---")
        for rec in llll_recs:
             print(f"目的地: {rec.destination: <4} | 节奏: {rec.pace: <6} | 出行: {rec.travelers: <5} | 花费: {rec.total_cost} | 标签: {rec.tags}")
        
    except Exception as e:
        print(f"执行出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    randomize_llll_data()
