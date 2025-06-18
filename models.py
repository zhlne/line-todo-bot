from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), nullable=False)
    content = db.Column(db.String(128), nullable=False)
    time = db.Column(db.String(10), nullable=False)





