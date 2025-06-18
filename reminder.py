from flask_apscheduler import APScheduler
from flask import current_app
from models import db, Task
from datetime import datetime, timedelta
import os
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.messaging.models import TextMessage, PushMessageRequest

scheduler = APScheduler()

@scheduler.task("cron", id="check_reminders", minute="*")
def check_reminders():
    app = current_app._get_current_object()
    with app.app_context():
        # 台灣時區 = UTC+8
        taiwan_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%H:%M")
        print(f"[台灣現在時間] {taiwan_time}（即將比對提醒任務）")

        tasks = Task.query.filter_by(time=taiwan_time).all()

        CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
        configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

        for task in tasks:
            print(f"[提醒] {task.time} - {task.content}（用戶：{task.user_id}）")

            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=task.user_id,
                        messages=[TextMessage(text=f"⏰ 提醒你：{task.time} {task.content}")]
                    )
                )


