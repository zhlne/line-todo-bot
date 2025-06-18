# ✅ 將 Flask 專案從 SQLite 遷移到 PostgreSQL（Render 免費）

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    content = Column(String)
    time = Column(String)

# ✅ 改為從環境變數讀取 PostgreSQL 連線字串
POSTGRES_URL = os.environ.get("DATABASE_URL")
if POSTGRES_URL is None:
    raise ValueError("❌ 請設定 DATABASE_URL 環境變數")

# ✅ 建立 PostgreSQL 連線
engine = create_engine(POSTGRES_URL, connect_args={"sslmode": "require"})
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

