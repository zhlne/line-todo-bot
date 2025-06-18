from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from models import db, Task
from linebot.v3.messaging import Configuration, MessagingApi, TextMessage, ReplyMessageRequest
import os

scheduler = BackgroundScheduler()

def check_reminders():
    now = datetime.now().strftime("%H:%M")
    tasks = Task.query.filter_by(time=now).all()
    for task in tasks:
        try:
            configuration = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))
            with MessagingApi(configuration) as api:
                message = TextMessage(text=f"⏰ 提醒你：{task.content}")
                api.push_message(to=task.user_id, messages=[message])
                print(f"[提醒發送] {task.user_id}: {task.content}")
        except Exception as e:
            print(f"[提醒錯誤] 無法發送給 {task.user_id}：{str(e)}")

scheduler.add_job(check_reminders, 'cron', minute='*')

