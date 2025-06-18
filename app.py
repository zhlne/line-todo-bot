from flask import Flask, request, abort
from models import db, Task
from reminder import scheduler
from linebot.v3 import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, TextMessage, ReplyMessageRequest
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "").replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if not app.config["SQLALCHEMY_DATABASE_URI"]:
    raise ValueError("❌ 請設定 DATABASE_URL 環境變數")

db.init_app(app)
with app.app_context():
    db.create_all()

# LINE Bot 初始化
channel_secret = os.getenv("CHANNEL_SECRET")
channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN")
if not channel_secret or not channel_access_token:
    raise ValueError("❌ 必須設定 CHANNEL_SECRET 和 CHANNEL_ACCESS_TOKEN")

handler = WebhookHandler(channel_secret)
configuration = Configuration(access_token=channel_access_token)
line_bot_api = MessagingApi(ApiClient(configuration))

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
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
        tasks = Task.query.filter_by(user_id=user_id).all()
        if tasks:
            reply = "📋 你的提醒：\n" + "\n".join([f"{t.time} {t.content}" for t in tasks])
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

    else:
        reply = "請輸入以下指令：\n1️⃣ 新增 HH:MM 提醒內容\n2️⃣ 查詢\n3️⃣ 刪除 提醒內容"

    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=reply)])
    )

if __name__ == "__main__":
    scheduler.start()
    app.run(host="0.0.0.0", port=10000)
