from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64))
    content = db.Column(db.String(256))
    time = db.Column(db.String(5))  # 格式為 HH:MM
