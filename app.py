from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return "LINE Bot 已部署成功！"

@app.route('/callback', methods=['POST'])
def callback():
    return '收到 LINE 傳來的訊息！'

if __name__ == '__main__':
    app.run()