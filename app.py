import os
from flask import Flask, request, abort
from models import db, Task
from reminder import create_scheduler
from dotenv import load_dotenv

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhook import MessageEvent
from linebot.v3.messaging import Configuration, MessagingApi
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import TextMessageContent

# 載入 .env 環境變數（本地測試用）
load_dotenv()

CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")

if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    raise ValueError("❌ 必須設定 CHANNEL_SECRET 和 CHANNEL_ACCESS_TOKEN")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# 建立資料表
with app.app_context():
    db.create_all()

# 啟動排程器
create_scheduler(app)

handler = WebhookHandler(CHANNEL_SECRET)
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

@app.route("/")
def index():
    return "LINE Bot 待辦提醒已啟動"

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
        tasks = Task.query.filter_by(user_id=user_id).order_by(Task.time).all()
        if tasks:
            reply = "📋 你的提醒：\n" + "\n".join([f"{t.id}. {t.time} {t.content}" for t in tasks])
        else:
            reply = "🔍 查無提醒事項"

    elif text.startswith("刪除 "):
        keyword = text[3:].strip()
        if keyword.isdigit():
            task = Task.query.filter_by(user_id=user_id, id=int(keyword)).first()
        else:
            task = Task.query.filter_by(user_id=user_id, content=keyword).first()

        if task:
            db.session.delete(task)
            db.session.commit()
            reply = f"🗑️ 已刪除提醒：{task.time} {task.content}"
        else:
            reply = f"❌ 查無提醒：{keyword}"

    else:
        reply = "請輸入以下指令：\n1️⃣ 新增 HH:MM 提醒內容\n2️⃣ 查詢\n3️⃣ 刪除 提醒內容或編號"

    with MessagingApi(configuration) as api:
        api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply)]
            )
        )
