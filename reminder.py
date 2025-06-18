from flask import current_app
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from models import db, Task
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, PushMessageRequest, TextMessage
import os

scheduler = BackgroundScheduler()

def check_reminders():
    with current_app.app_context():
        now = datetime.now().strftime("%H:%M")
        tasks = Task.query.filter_by(time=now).all()

        if tasks:
            configuration = Configuration(access_token=os.environ.get("CHANNEL_ACCESS_TOKEN"))
            with ApiClient(configuration) as api:
                line_bot_api = MessagingApi(api)
                for task in tasks:
                    message = TextMessage(text=f"⏰ 提醒：{task.time} {task.content}")
                    line_bot_api.push_message(PushMessageRequest(to=task.user_id, messages=[message]))

scheduler.add_job(check_reminders, "cron", minute="*")
scheduler.start()
print("✅ APScheduler 已啟動")




