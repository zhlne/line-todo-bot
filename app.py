from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from datetime import datetime
from reminder import scheduler
from models import db, Task
import os

# 初始化 Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db.init_app(app)

# 環境變數：LINE 機器人憑證
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    raise ValueError("❌ 必須設定 CHANNEL_SECRET 和 CHANNEL_ACCESS_TOKEN")

# 初始化 LINE Bot
handler = WebhookHandler(CHANNEL_SECRET)
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
line_bot_api = MessagingApi(ApiClient(configuration))

@app.route("/")
def home():
    return "✅ LINE Bot To-Do Reminder 啟動中"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    if text == "查詢":
        tasks = Task.query.filter_by(user_id=user_id).all()
        if not tasks:
            reply = "🔍 查無提醒事項"
        else:
            reply = "🗒 你的提醒列表：\n" + "\n".join([f"{t.content} @ {t.time}" for t in tasks])

    elif text.startswith("刪除:"):
        target = text.replace("刪除:", "").strip()
        task = Task.query.filter_by(user_id=user_id, content=target).first()
        if task:
            db.session.delete(task)
            db.session.commit()
            reply = f"🗑 已刪除提醒：{target}"
        else:
            reply = "❌ 查無此提醒"

    elif "@" in text:
        try:
            content, time_str = map(str.strip, text.split("@"))
            datetime.strptime(time_str, "%H:%M")  # 驗證格式
            task = Task(user_id=user_id, content=content, time=time_str)
            db.session.add(task)
            db.session.commit()
            reply = f"✅ 已新增提醒：{content} @ {time_str}"
        except:
            reply = "⚠️ 格式錯誤，請用：提醒內容@HH:MM"
    else:
        reply = "請輸入提醒，例如：吃藥@08:00、查詢、刪除:吃藥"

    with ApiClient(configuration) as api_client:
        line_bot = MessagingApi(api_client)
        line_bot.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply)]
            )
        )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    scheduler.start()
    print("[✅ APScheduler 啟動中]")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))


