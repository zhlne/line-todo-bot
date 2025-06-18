from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from models import db, Task
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient, TextMessage, PushMessageRequest
import os

# 初始化 LINE Bot
channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN")
if not channel_access_token:
    raise ValueError("❌ 請設定 CHANNEL_ACCESS_TOKEN 環境變數")

configuration = Configuration(access_token=channel_access_token)
line_bot_api = MessagingApi(ApiClient(configuration))

def send_reminders():
    now = datetime.now().strftime("%H:%M")
    print(f"[Scheduler] 現在時間是 {now}，正在檢查提醒...")

    tasks = Task.query.filter_by(time=now).all()
    for task in tasks:
        line_bot_api.push_message(
            PushMessageRequest(
                to=task.user_id,
                messages=[TextMessage(text=f"⏰ 提醒事項：{task.content}")]
            )
        )
        print(f"[🔔 已發送] {task.user_id}：{task.content}")

scheduler = BackgroundScheduler(timezone="Asia/Taipei")
scheduler.add_job(send_reminders, "cron", minute="*")


