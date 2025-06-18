from flask import Flask, request, abort
from models import db, Task
from reminder import scheduler
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging import Configuration, MessagingApi, TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import TextMessageContent
import os

# 環境變數
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    raise ValueError("❌ 必須設定 CHANNEL_SECRET 和 CHANNEL_ACCESS_TOKEN")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# LINE 初始化
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 啟動排程器
scheduler.start()
print("✅ APScheduler 啟動中")

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
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
            reply = "📋 你的提醒：\n" + "\n".join([f"{t.id}. {t.time} {t.content}" for t in tasks])
        else:
            reply = "🔍 查無提醒事項"

    elif text.startswith("刪除 "):
        keyword = text[3:]
        if keyword.isdigit():
            task = Task.query.filter_by(id=int(keyword), user_id=user_id).first()
        else:
            task = Task.query.filter_by(content=keyword, user_id=user_id).first()
        if task:
            db.session.delete(task)
            db.session.commit()
            reply = f"🗑️ 已刪除提醒：{task.content}"
        else:
            reply = f"❌ 查無提醒：{keyword}"

    else:
        reply = "請輸入以下指令：\n1️⃣ 新增 HH:MM 提醒內容\n2️⃣ 查詢\n3️⃣ 刪除 提醒編號 或 提醒內容"

    with MessagingApi(configuration) as api:
        api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=reply)]))

@app.route("/")
def index():
    return "LINE Reminder Bot 正在執行中！"

if __name__ == "__main__":
    app.run()
