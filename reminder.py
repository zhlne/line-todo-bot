from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from models import Session, Task
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import TextMessage, PushMessageRequest
import os

# 初始化 LINE Messaging API
def get_line_api():
    access_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    config = Configuration(access_token=access_token)
    return MessagingApi(ApiClient(config))

# 每分鐘執行的提醒函式
def check_tasks():
    now = datetime.now().strftime("%H:%M")
    session = Session()
    tasks = session.query(Task).filter_by(time=now).all()
    session.close()

    if not tasks:
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
            print(f"已推送提醒給 {task.user_id}：{task.content}")
        except Exception as e:
            print(f"[提醒推送錯誤] {e}")

# 啟動排程器
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_tasks, 'interval', minutes=1)
    scheduler.start()

