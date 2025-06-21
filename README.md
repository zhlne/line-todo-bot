# 📌 LINE Bot 智慧提醒系統

一個使用 Flask + LINE Messaging API 製作的任務提醒系統，支援使用者透過 LINE 指令新增、查詢與刪除提醒事項，並在指定時間由系統自動推播提醒。

---

## 🧱 專案架構

```
📦 line-todo-bot/
├── app.py               # 主應用程式，處理 LINE Webhook 與指令邏輯
├── models.py            # SQLAlchemy 任務模型
├── reminder.py          # 定時任務檢查並推播提醒
├── requirements.txt     # 所需套件清單
```

---

## 🚀 功能說明

### ✅ 使用者指令（透過 LINE Bot 發送文字訊息）

- `新增 HH:MM 提醒內容`：新增一筆提醒  
  例如：`新增 08:30 上課不要遲到`

- `查詢`：查詢所有提醒事項  
  回應格式：
    📋 你的提醒：
    1. 08:30 上課不要遲到
    2. 21:00 寫作業

- `刪除 提醒內容`：刪除指定內容的提醒  
  例如：`刪除 上課不要遲到`

---

## 🕰️ 定時提醒機制

- 使用 Flask-APScheduler
- 每分鐘自動執行 `check_reminders` 函式
- 比對當前台灣時間（UTC+8）與任務時間
- 若符合，透過 LINE `push_message` 傳送提醒訊息給對應用戶

---

## ⚠️ 遇到的困難與解法

| 問題 | 解決方法 |
|------|----------|
| APScheduler 無法使用 `current_app` | 改用 `lambda: check_reminders(app)` 傳入應用實體 |
| 時間比對錯誤 | 使用 `datetime.utcnow() + timedelta(hours=8)` 對齊台灣時間 |
| Render 雲端休眠 | 免費方案會導致排程停止，可使用 ping 機制或升級方案 |
| LINE 傳送失敗 | 區分 reply / push message，確保使用正確 access token |
| 資料庫連線錯誤 | 檢查 `DATABASE_URL` 格式是否正確，特別是在 Render 上 |

---

## 📦 安裝與執行

### 1. 安裝環境與套件

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### 2. 建立 `.env` 環境變數

請建立 `.env` 檔案並填入以下資訊：

```
CHANNEL_SECRET=你的LINE_CHANNEL_SECRET
CHANNEL_ACCESS_TOKEN=你的LINE_CHANNEL_ACCESS_TOKEN
DATABASE_URL=postgresql://使用者:密碼@主機:5432/資料庫名稱
```

### 3. 執行應用

```bash
gunicorn app:app
```

---

## 📘 套件版本（requirements.txt）

```
Flask==2.3.3
flask_sqlalchemy==3.1.1
flask_apscheduler==1.13.1
line-bot-sdk==3.4.0
gunicorn
psycopg2-binary
```

---

## 💡 延伸方向

- ⏰ 支援日期（YYYY-MM-DD HH:MM）提醒
- 🔁 支援每日/每週重複提醒
- 📊 加入提醒統計視覺化
- 🌐 網頁後台管理介面（使用 Flask-Admin）
- 🗃️ 導出提醒歷史紀錄

---

## 🙋‍♂️ 作者

開發者：@zhlne  
GitHub: https://github.com/zhlne
