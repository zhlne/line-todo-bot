from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from models import SessionLocal, Task
from linebot.v3.messaging import Configuration, MessagingApi, ApiClient
from linebot.v3.messaging.models import TextMessage, PushMessageRequest
import os
import pytz

scheduler = BackgroundScheduler(timezone="Asia/Taipei")

CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

def check_reminders():
    now = datetime.now(pytz.timezone("Asia/Taipei"))
    current_time = now.strftime("%H:%M")
    print(f"[Scheduler] 現在時間是 {current_time}，正在檢查提醒...")

    session = SessionLocal()
    tasks = session.query(Task).filter_by(time=current_time).all()

    if not tasks:
        print("[Scheduler] 沒有符合時間的提醒")
    else:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            for task in tasks:
                try:
                    line_bot_api.push_message(
                        PushMessageRequest(
                            to=task.user_id,
                            messages=[TextMessage(text=f"🔔 提醒：{task.content} 的時間到了！")]
                        )
                    )
                except Exception as e:
                    print("[❌ LINE 推播失敗]", e)
    session.close()

def start_scheduler():
    scheduler.add_job(check_reminders, 'cron', minute='*')
    scheduler.start()
    print("[✅ APScheduler 啟動中]")

