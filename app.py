from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import Configuration, MessagingApi, ApiClient
from linebot.v3.messaging.models import TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
import re
from models import Task, Session, init_db
from reminder import start_scheduler

print("[🚀 app.py 啟動]")

# 讀取環境變數
CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

if CHANNEL_SECRET is None or CHANNEL_ACCESS_TOKEN is None:
    raise ValueError("❌ 請設定 LINE_CHANNEL_SECRET 和 LINE_CHANNEL_ACCESS_TOKEN")

app = Flask(__name__)
handler = WebhookHandler(CHANNEL_SECRET)
config = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
line_bot_api = MessagingApi(ApiClient(config))

# 初始化資料庫與排程器
init_db()
start_scheduler()

@app.route('/')
def home():
    return "✅ LINE 代辦事項提醒 Bot 正在運作！"

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"[Webhook Error] {e}")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()
    session = Session()
    reply = "🤖 請輸入：\n🟢 新增 事項 時間\n🔍 查詢\n🗑️ 刪除 事項"

    try:
        if msg.startswith("新增"):
            match = re.match(r"新增\s+(.+)\s+(\d{2}:\d{2})", msg)
            if match:
                content, time_str = match.groups()
                task = Task(user_id=user_id, content=content, time=time_str)
                session.add(task)
                session.commit()
                reply = f"✅ 已新增：{content}，時間：{time_str}"
            else:
                reply = "⚠️ 格式錯誤，請用：新增 任務 時間（例如：新增 洗衣服 21:30）"

        elif msg == "查詢":
            tasks = session.query(Task).filter_by(user_id=user_id).all()
            if tasks:
                reply = "🗒️ 你的代辦事項：\n"
                for t in tasks:
                    reply += f"- {t.content} @ {t.time}\n"
            else:
                reply = "📭 目前沒有代辦事項"

        elif msg.startswith("刪除"):
            to_delete = msg.replace("刪除", "").strip()
            task = session.query(Task).filter_by(user_id=user_id, content=to_delete).first()
            if task:
                session.delete(task)
                session.commit()
                reply = f"🗑️ 已刪除：{to_delete}"
            else:
                reply = f"⚠️ 沒有找到「{to_delete}」這個代辦事項"

    except Exception as e:
        reply = f"❌ 發生錯誤：{e}"
    finally:
        session.close()

    try:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply)]
            )
        )
    except Exception as e:
        print(f"[ReplyMessage Error] {e}")