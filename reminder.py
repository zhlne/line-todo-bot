# reminder.py
from apscheduler.schedulers.background import BackgroundScheduler
from linebot.v3.messaging import MessagingApi, Configuration, PushMessageRequest, TextMessage
from datetime import datetime, timedelta
from models import db, Task
import os

# 初始化 LINE Bot API
configuration = Configuration(access_token=os.environ.get("CHANNEL_ACCESS_TOKEN"))
line_bot_api = MessagingApi(configuration)

def check_reminders():
    now = datetime.utcnow() + timedelta(hours=8)  # ➜ 台灣時間
    now_str = now.strftime("%H:%M")

    print(f"[Scheduler] 現在時間是 {now_str}，正在檢查提醒...")

    with db.session.begin():
        tasks = db.session.query(Task).filter(Task.time == now_str).all()

    if tasks:
        for task in tasks:
            try:
                message = f"⏰ 提醒你：{task.time} {task.content}"
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=task.user_id,
                        messages=[TextMessage(text=message)]
                    )
                )
                print(f"[Scheduler] 已推播提醒給 {task.user_id}：{message}")
            except Exception as e:
                print(f"[Scheduler] ❌ 推播失敗：{str(e)}")
    else:
        print("[Scheduler] 沒有符合時間的提醒")

# 啟動排程器
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_reminders, 'interval', minutes=1)
    scheduler.start()
    print("[✅ APScheduler 啟動中]")


