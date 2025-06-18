from flask import Flask, request, abort
from models import db, Task
from reminder import start_scheduler
from linebot.v3 import WebhookHandler
from linebot.v3.webhooks import MessageEvent
from linebot.v3.webhooks import TextMessageContent
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
        tasks = Task.query.filter_by(user_id=user_id).order_by(Task.id).all()
        if tasks:
            reply_lines = ["📋 你的提醒："]
            for i, t in enumerate(tasks, start=1):
                reply_lines.append(f"{i}. {t.time} {t.content}")
            reply = "\n".join(reply_lines)
        else:
            reply = "🔍 查無提醒事項"

    elif text.startswith("刪除 "):
        arg = text[3:].strip()
        tasks = Task.query.filter_by(user_id=user_id).order_by(Task.id).all()

        if arg.isdigit():
            index = int(arg) - 1
            if 0 <= index < len(tasks):
                task_to_delete = tasks[index]
                db.session.delete(task_to_delete)
                db.session.commit()
                reply = f"🗑️ 已刪除提醒：{task_to_delete.time} {task_to_delete.content}"
            else:
                reply = f"❌ 無此編號提醒：{arg}"
        else:
            reply = f"❌ 無效刪除指令，請輸入：刪除 編號"

    else:
        reply = "請輸入以下指令：\n1️⃣ 新增 HH:MM 提醒內容\n2️⃣ 查詢\n3️⃣ 刪除 編號"

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply)]
        )
    )


if __name__ == "__main__":
    start_scheduler()
    app.run(host="0.0.0.0", port=10000)


