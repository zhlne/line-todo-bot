from flask import Flask, request
from linebot.v3 import WebhookHandler
from linebot.v3.webhook import MessageEvent
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import TextMessageContent
from models import db, Task, init_db
from reminder import start_scheduler
import os

# 驗證環境變數
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    raise ValueError("❌ 必須設定 CHANNEL_SECRET 和 CHANNEL_ACCESS_TOKEN")

# 初始化 Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    init_db()

# 初始化 LINE Bot
handler = WebhookHandler(CHANNEL_SECRET)
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)

# 啟動排程器
start_scheduler()

@app.route("/")
def index():
    return "✅ LINE To-do Bot 運作中"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"[❌ Webhook 錯誤] {e}")

    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text.strip()
    user_id = event.source.user_id

    if text.startswith("新增 "):
        try:
            time_part, content = text[3:].split(" ", 1)
            task = Task(user_id=user_id, time=time_part, content=content)
            db.session.add(task)
            db.session.commit()
            reply = f"✅ 已新增提醒：{time_part} {content}"
        except Exception as e:
            reply = f"❌ 新增失敗：{str(e)}"

    elif text == "查詢":
        tasks = Task.query.filter_by(user_id=user_id).all()
        if tasks:
            reply = "📋 你的提醒：\n" + "\n".join([f"{i+1}. {t.time} {t.content}" for i, t in enumerate(tasks)])
        else:
            reply = "🔍 查無提醒事項"

    elif text.startswith("刪除 "):
        keyword = text[3:].strip()
        if keyword.isdigit():
            index = int(keyword) - 1
            tasks = Task.query.filter_by(user_id=user_id).all()
            if 0 <= index < len(tasks):
                deleted = tasks[index]
                db.session.delete(deleted)
                db.session.commit()
                reply = f"🗑️ 已刪除提醒：{deleted.time} {deleted.content}"
            else:
                reply = "❌ 查無對應編號"
        else:
            task = Task.query.filter_by(user_id=user_id, content=keyword).first()
            if task:
                db.session.delete(task)
                db.session.commit()
                reply = f"🗑️ 已刪除提醒：{task.content}"
            else:
                reply = f"❌ 查無提醒：{keyword}"

    else:
        reply = "請輸入以下指令：\n1️⃣ 新增 HH:MM 提醒內容\n2️⃣ 查詢\n3️⃣ 刪除 提醒內容或編號"

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply)]
        )
    )

if __name__ == "__main__":
    app.run()