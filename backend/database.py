from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# 使用 MySQL 数据库
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://Megumi:09231110jthJTH.@localhost/travel_agent_memory"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class DbItinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True) # 简单的用户标识
    destination = Column(String(100))
    start_date = Column(String(20))
    days = Column(Integer)
    total_cost = Column(Integer)
    
    # 存储完整的 JSON 结构
    content_json = Column(JSON) 
    
    created_at = Column(DateTime, default=datetime.now)
    is_saved = Column(Boolean, default=True)   # 是否在“我的行程”中
    is_favorite = Column(Boolean, default=False) # 是否在“我的收藏”中

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)

def init_db():
    Base.metadata.create_all(bind=engine)
