import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from reminder import scheduler
from models import db, Task
from reminder import create_scheduler

# LINE credentials
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    raise ValueError("❌ 必須設定 CHANNEL_SECRET 和 CHANNEL_ACCESS_TOKEN")

# Flask app
app = Flask(__name__)
create_scheduler(app)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# LINE API 設定
handler = WebhookHandler(CHANNEL_SECRET)
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

# 觸發首頁確認
@app.route("/")
def home():
    return "Line Reminder Bot is running!"

# LINE Webhook Callback
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"❌ Webhook error: {e}")
    return "OK"

# 處理文字訊息事件
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text.strip()
    user_id = event.source.user_id

    if text.startswith("新增 "):
        try:
            parts = text[3:].split(" ")
            time_part = parts[0]
            content = " ".join(parts[1:])
            task = Task(user_id=user_id, time=time_part, content=content)
            db.session.add(task)
            db.session.commit()
            reply = f"✅ 已新增提醒：{time_part} {content}"
        except Exception as e:
            reply = f"❌ 新增失敗：{str(e)}"

    elif text == "查詢":
        tasks = Task.query.filter_by(user_id=user_id).order_by(Task.time.asc()).all()
        if tasks:
            reply = "📋 你的提醒：\n" + "\n".join(
                [f"{i+1}. {t.time} {t.content}" for i, t in enumerate(tasks)]
            )
        else:
            reply = "🔍 查無提醒事項"

    elif text.startswith("刪除 "):
        try:
            index = int(text[3:]) - 1
            tasks = Task.query.filter_by(user_id=user_id).order_by(Task.time.asc()).all()
            if 0 <= index < len(tasks):
                db.session.delete(tasks[index])
                db.session.commit()
                reply = f"🗑️ 已刪除提醒：{index+1}. {tasks[index].time} {tasks[index].content}"
            else:
                reply = "❌ 無效編號，請重新確認。"
        except Exception as e:
            reply = f"❌ 刪除失敗：{str(e)}"

    else:
        reply = "請輸入以下指令：\n" \
                "🆕 新增 HH:MM 提醒內容\n" \
                "📋 查詢\n" \
                "🗑️ 刪除 編號（查詢後的編號）"

    with ApiClient(configuration) as api:
        line_bot_api = MessagingApi(api)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply)]
            )
        )

