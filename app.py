from flask import Flask, request
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhook import MessageEvent
from linebot.v3.messaging import Configuration, MessagingApi, ApiClient
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import TextMessageContent

import os
from models import Task, SessionLocal, init_db
from reminder import start_scheduler

app = Flask(__name__)

# ✅ 設定 LINE Bot 金鑰
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    raise ValueError("❌ 必須設定 CHANNEL_SECRET 和 CHANNEL_ACCESS_TOKEN")

handler = WebhookHandler(CHANNEL_SECRET)
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

# ✅ 初始化資料庫與排程器
init_db()
start_scheduler()

@app.route("/")
def index():
    return "✅ LINE To-Do Bot 已部署成功"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "❌ Invalid signature", 400

    return "OK"

# ✅ 處理使用者訊息
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()

    reply = "❓ 請用正確格式：待辦事項@時間 (例如：考試@14:30)"
    if "@" in msg:
        try:
            content, time = msg.split("@")
            content = content.strip()
            time = time.strip()

            task = Task(user_id=user_id, content=content, time=time)
            session = SessionLocal()
            session.add(task)
            session.commit()
            session.close()

            reply = f"✅ 已新增提醒：{content} @ {time}"
        except:
            reply = "⚠️ 無法解析內容，請確認格式正確"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply)]
            )
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
