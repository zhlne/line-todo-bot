# ✅ models.py：定義資料表與資料庫初始化
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    content = Column(String)
    time = Column(String)

# ✅ 從 Render 環境變數取得 DATABASE_URL
POSTGRES_URL = os.environ.get("DATABASE_URL")
if POSTGRES_URL is None:
    raise ValueError("❌ 請設定 DATABASE_URL 環境變數")

engine = create_engine(POSTGRES_URL, connect_args={"sslmode": "require"})
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)


