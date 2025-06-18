from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import Configuration, MessagingApi, ApiClient
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
import re
from models import Task, Session, init_db

# 環境變數
CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

app = Flask(__name__)
handler = WebhookHandler(CHANNEL_SECRET)

config = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
line_bot_api = MessagingApi(ApiClient(config))

# 初始化資料庫
init_db()

@app.route('/')
def home():
    return "✅ LINE 代辦事項 Bot 運作中！"

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Webhook error: {e}")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()

    if msg.startswith("新增"):
        match = re.match(r"新增\s+(.+)\s+(\d{2}:\d{2})", msg)
        if match:
            content, time_str = match.groups()
            session = Session()
            task = Task(user_id=user_id, content=content, time=time_str)
            session.add(task)
            session.commit()
            session.close()
            reply = f"✅ 已新增：{content}，時間：{time_str}"
        else:
            reply = "⚠️ 格式錯誤，請用：新增 事項 時間（例如：新增 吃飯 18:30）"
    else:
        reply = "請輸入：\n🟢 新增 事項 時間\n🔍 查詢\n🗑️ 刪除 事項"

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply)]
        )
    )

if __name__ == "__main__":
    app.run()


