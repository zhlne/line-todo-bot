from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from models import Task, db
from linebot.v3.messaging import MessagingApi, Configuration, TextMessage
import pytz
import os

# 建立 LINE Messaging API 實例
line_bot_api = MessagingApi(
    Configuration(access_token=os.environ.get("CHANNEL_ACCESS_TOKEN"))
)

# 建立排程器
scheduler = BackgroundScheduler()

def check_reminders():
    now = datetime.now(pytz.timezone('Asia/Taipei'))
    now_str = now.strftime("%H:%M")
    print(f"[Scheduler] 現在時間是 {now_str}，正在檢查提醒...")

    tasks = Task.query.filter_by(time=now_str).all()
    for task in tasks:
        print(f"[提醒] 時間符合 {task.time} | 推播內容：{task.content} | user_id: {task.user_id}")
        try:
            line_bot_api.push_message(
                task.user_id,
                TextMessage(text=f"🔔 提醒：{task.content} 的時間到了！")
            )
        except Exception as e:
            print(f"[錯誤] 無法推播：{e}")

def start_scheduler():
    print("[✅ APScheduler 啟動中]")
    scheduler.add_job(check_reminders, 'interval', minutes=1)
    scheduler.start()
