from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from pytz import timezone
from models import Session, Task
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import TextMessage, PushMessageRequest
import os

print("[📦 reminder.py 被匯入]")

def get_line_api():
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    config = Configuration(access_token=token)
    return MessagingApi(ApiClient(config))

def check_tasks():
    tz = timezone('Asia/Taipei')
    now = datetime.now(tz).strftime("%H:%M")
    print(f"[Scheduler] 現在台灣時間是 {now}，正在檢查提醒...")
    session = Session()
    tasks = session.query(Task).filter_by(time=now).all()
    session.close()

    if not tasks:
        print("[Scheduler] 沒有符合時間的提醒")
        return

    line_bot_api = get_line_api()
    for task in tasks:
        try:
            line_bot_api.push_message(
                PushMessageRequest(
                    to=task.user_id,
                    messages=[TextMessage(text=f"🔔 提醒：{task.content} 的時間到了！")]
                )
            )
            print(f"[Scheduler] ✅ 已推送提醒給 {task.user_id}：{task.content}")
        except Exception as e:
            print(f"[提醒推送錯誤] {e}")

def start_scheduler():
    print("[✅ APScheduler 啟動中]")
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_tasks, 'interval', minutes=1)
    scheduler.start()