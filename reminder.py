from flask_apscheduler import APScheduler
from models import Task
from datetime import datetime
from flask import current_app
import os

from linebot.v3.messaging import MessagingApi, Configuration
from linebot.v3.messaging.models import TextMessage, PushMessageRequest

scheduler = APScheduler()

def check_reminders():
    with current_app.app_context():
        now = datetime.now().strftime("%H:%M")
        tasks = Task.query.filter_by(time=now).all()
        if tasks:
            print(f"[提醒] 時間 {now} 有 {len(tasks)} 則提醒")
            config = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))
            with MessagingApi(config) as api:
                for task in tasks:
                    msg = f"⏰ 提醒你：{task.content}（{task.time}）"
                    api.push_message(PushMessageRequest(to=task.user_id, messages=[TextMessage(text=msg)]))
        else:
            print(f"[提醒] {now} 沒有提醒")

def create_scheduler(app):
    scheduler.init_app(app)
    scheduler.start()
    scheduler.add_job(id="check_reminders", func=check_reminders, trigger="cron", minute="*")
    print("✅ APScheduler 已啟動")