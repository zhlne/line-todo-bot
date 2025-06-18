from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ LINE Bot 在 Render 上成功運作！"

@app.route('/callback', methods=['POST'])
def callback():
    return '✅ 收到 LINE 傳來的訊息！'

if __name__ == '__main__':
    app.run()
