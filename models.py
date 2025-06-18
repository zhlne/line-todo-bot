from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    content = Column(String)
    time = Column(String)

engine = create_engine("sqlite:///tasks.db", connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
