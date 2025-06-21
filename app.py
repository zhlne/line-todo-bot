import os
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from models import db, Task
from reminder import scheduler, check_reminders
from datetime import datetime
from linebot.v3.webhook import WebhookHandler, MessageEvent
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import TextMessageContent

# 環境變數
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    raise ValueError("❌ 必須設定 CHANNEL_SECRET 和 CHANNEL_ACCESS_TOKEN")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# 初始化 APScheduler
scheduler.init_app(app)
scheduler.start()

# 加入提醒任務（避免使用 current_app）
scheduler.add_job(
    id="check_reminders",
    func=lambda: check_reminders(app),
    trigger="cron",
    minute="*"
)

with app.app_context():
    db.create_all()

handler = WebhookHandler(CHANNEL_SECRET)
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

@app.route("/")
def home():
    return "Line TODO Bot 正常運作中"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"[錯誤] {str(e)}")
        abort(500)
    return "OK"

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
        tasks = Task.query.filter_by(user_id=user_id).order_by(Task.time).all()
        if tasks:
            reply = "📋 你的提醒：\n" + "\n".join(
                [f"{i+1}. {t.time} {t.content}" for i, t in enumerate(tasks)]
            )
        else:
            reply = "🔍 查無提醒事項"

    elif text.startswith("刪除 "):
        keyword = text[3:]
        task = Task.query.filter_by(user_id=user_id, content=keyword).first()
        if task:
            db.session.delete(task)
            db.session.commit()
            reply = f"🗑️ 已刪除提醒：{keyword}"
        else:
            reply = f"❌ 查無提醒：{keyword}"

    elif text == "刪除全部":
        tasks = Task.query.filter_by(user_id=user_id).all()
        if tasks:
            for t in tasks:
                db.session.delete(t)
            db.session.commit()
            reply = "🗑️ 已刪除你所有的提醒資料"
        else:
            reply = "❌ 沒有可刪除的提醒資料"

    else:
        reply = (
            "請輸入以下指令：\n"
            "1️⃣ 新增 HH:MM 提醒內容\n"
            "2️⃣ 查詢\n"
            "3️⃣ 刪除 提醒內容\n"
            "4️⃣ 刪除全部"
        )

    with ApiClient(configuration) as api:
        line_bot_api = MessagingApi(api)
        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=reply)])
        )