from fflask_apscheduler import APScheduler
from flask import current_app
from models import db, Task
from datetime import datetime

scheduler = APScheduler()

@scheduler.task("cron", id="check_reminders", minute="*")
def check_reminders():
    app = current_app._get_current_object()
    with app.app_context():
        now = datetime.now().strftime("%H:%M")
        tasks = Task.query.filter_by(time=now).all()
        for task in tasks:
            print(f"[提醒] {task.time} - {task.content}（用戶：{task.user_id}）")