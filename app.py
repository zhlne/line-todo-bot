# ✅ 完整版 app.py：整合新增/查詢/刪除提醒 + LINE webhook 接收

from flask import Flask, request
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhook import MessageEvent
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import TextMessageContent

from models import db, Task
from reminder import start_scheduler
import os

app = Flask(__name__)

# === 環境變數設定 ===
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    raise ValueError("❌ 必須設定 CHANNEL_SECRET 和 CHANNEL_ACCESS_TOKEN")

# === LINE Bot 設定 ===
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
messaging_api = MessagingApi(ApiClient(configuration))

# === 資料庫設定（PostgreSQL） ===
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# === 啟動排程器 ===
start_scheduler(messaging_api)

# === 根路由 ===
@app.route('/')
def home():
    return '✅ LINE Bot 已部署'

# === LINE Webhook ===
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature', 400
    return 'OK'

# === 訊息事件處理 ===
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    reply = ""

    # 查詢提醒
    if text == "查詢":
        tasks = Task.query.filter_by(user_id=user_id).all()
        if tasks:
            reply = "📋 你的提醒事項：\n" + "\n".join([f"{t.content} @ {t.time}" for t in tasks])
        else:
            reply = "目前沒有任何提醒事項。"

    # 刪除提醒：刪除:內容
    elif text.startswith("刪除:"):
        content_to_delete = text.replace("刪除:", "").strip()
        task = Task.query.filter_by(user_id=user_id, content=content_to_delete).first()
        if task:
            db.session.delete(task)
            db.session.commit()
            reply = f"✅ 已刪除提醒：{content_to_delete}"
        else:
            reply = f"❌ 查無提醒：{content_to_delete}"

    # 新增提醒：內容@時間
    elif "@" in text:
        try:
            content, time_str = text.split("@")
            content = content.strip()
            time_str = time_str.strip()
            new_task = Task(user_id=user_id, content=content, time=time_str)
            db.session.add(new_task)
            db.session.commit()
            reply = f"✅ 已新增提醒：{content} @ {time_str}"
        except:
            reply = "❌ 格式錯誤，請使用『提醒內容@時間』的格式。"
    
    else:
        reply = "請使用以下格式：\n📌 新增提醒：提醒內容@時間\n🗒 查詢提醒：查詢\n🗑 刪除提醒：刪除:提醒內容"

    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply)]
        )
    )

# === 啟動 Flask ===
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

