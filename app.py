# ✅ 將 Flask LINE Bot 專案使用 PostgreSQL（Render）完整版本

from flask import Flask, request
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.webhooks import MessageEvent
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest, PushMessageRequest
from linebot.v3.webhooks import TextMessageContent

from models import Task, Session, init_db
from reminder import start_scheduler

import os

# === 初始化 Flask ===
app = Flask(__name__)

# === 初始化 LINE Bot ===
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/")
def home():
    return "✅ LINE Bot 已部署成功"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("[❌ 處理訊息錯誤]", e)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()
    session = Session()
    reply = "❓ 請輸入 '新增 內容 時間'、'查詢' 或 '刪除 內容'"

    if msg.startswith("新增"):
        try:
            _, content, time = msg.split(" ", 2)
            new_task = Task(user_id=user_id, content=content, time=time)
            session.add(new_task)
            session.commit()
            reply = f"✅ 已新增：{content}，時間：{time}"
        except Exception as e:
            print("[新增任務錯誤]", e)
            reply = "⚠️ 格式錯誤，請用：新增 任務內容 時間 (例如：新增 喝水 18:30)"

    elif msg == "查詢":
        tasks = session.query(Task).filter_by(user_id=user_id).all()
        if tasks:
            reply = "🗒️ 你的代辦事項：\n" + "\n".join([f"- {t.content} @ {t.time}" for t in tasks])
        else:
            reply = "📭 目前沒有代辦事項"

    elif msg.startswith("刪除"):
        try:
            _, content = msg.split(" ", 1)
            task = session.query(Task).filter_by(user_id=user_id, content=content).first()
            if task:
                session.delete(task)
                session.commit()
                reply = f"🗑️ 已刪除：{content}"
            else:
                reply = "⚠️ 查無此任務"
        except Exception as e:
            print("[刪除任務錯誤]", e)
            reply = "⚠️ 請用格式：刪除 任務內容"

    session.close()
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply)]
                )
            )
    except Exception as e:
        print("[ReplyMessage Error]", e)

# === 啟動區 ===
if __name__ == '__main__':
    print("[🚀 app.py 啟動]")
    init_db()
    start_scheduler()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
