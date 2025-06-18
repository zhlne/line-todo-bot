from apscheduler.schedulers.background import BackgroundScheduler
from models import db, Task
from datetime import datetime, timedelta
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import TextMessage, PushMessageRequest
import os

# === 初始化 LINE Messaging API ===
channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN")
configuration = Configuration(access_token=channel_access_token)
line_bot_api = MessagingApi(ApiClient(configuration))

# === 初始化排程器 ===
scheduler = BackgroundScheduler()

# === 檢查提醒任務 ===
def check_reminders():
    now = datetime.utcnow() + timedelta(hours=8)  # 台灣時區
    now_str = now.strftime("%H:%M")
    print(f"[Scheduler] 現在時間是 {now_str}，正在檢查提醒...")

    print("【資料庫中全部提醒】")
    tasks = Task.query.all()
    for t in tasks:
        print(f"📝 {t.time} | {t.content} | {t.user_id}")

    due_tasks = Task.query.filter_by(time=now_str).all()
    for task in due_tasks:
        try:
            message = TextMessage(text=f"⏰ 提醒你：{task.time} {task.content}")
            line_bot_api.push_message(PushMessageRequest(to=task.user_id, messages=[message]))
            print(f"[Scheduler] 已推播提醒給 {task.user_id}：{task.time} {task.content}")
        except Exception as e:
            print(f"[Scheduler] ❌ 推播失敗：{str(e)}")

# === 啟動排程器 ===
def start_scheduler():
    scheduler.add_job(check_reminders, 'interval', minutes=1)
    scheduler.start()
    print("[✅ APScheduler 啟動中]")



