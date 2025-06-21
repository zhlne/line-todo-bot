# 📌 LINE Bot 智慧提醒系統

這是一套可部署的 LINE Bot 提醒應用系統，用戶可透過簡單文字指令，操作新增、查詢與刪除提醒事項。系統會在指定時間自動推送提醒訊息，適合日常生活任務安排與備忘需求。

---

## ✅ 支援指令

| 指令範例 | 功能說明 |
|----------|----------|
| `新增 HH:MM 提醒內容` | 新增提醒，例如：`新增 08:30 出門搭車` |
| `查詢` | 查詢目前所有提醒事項 |
| `刪除 提醒內容` | 刪除特定提醒，例如：`刪除 出門搭車` |
| `刪除全部` | 一次刪除目前用戶的所有提醒資料（⚠️ 不可復原） |

---

## 🕒 功能簡介

- 📩 透過 LINE Bot Webhook 接收指令
- ⏰ 使用 APScheduler 每分鐘自動比對目前時間（支援台灣時區 UTC+8）
- 🔔 時間到即自動透過 Push Message 傳送提醒
- 🧑‍💼 每位用戶資料獨立儲存（依 user_id 區分）
- ☁️ 可部署於 Render、Heroku 等支援 Python Web App 的雲平台

---

## 🧱 使用技術

| 分類 | 技術 |
|------|------|
| Web 應用框架 | Flask |
| 資料庫 ORM | Flask-SQLAlchemy |
| 定時排程模組 | Flask-APScheduler |
| 即時通訊串接 | LINE Bot SDK v3 |
| 資料儲存 | PostgreSQL |
| 雲端部署 | Render + Gunicorn |

---

## 📦 相依套件（requirements.txt）

```
Flask==2.3.3
flask_sqlalchemy==3.1.1
flask_apscheduler==1.13.1
line-bot-sdk==3.4.0
gunicorn
psycopg2-binary
```

---

## 📁 專案結構（簡略）

```
├── app.py              # 主應用入口，處理指令邏輯與 Webhook
├── models.py           # 任務資料模型（Task）
├── reminder.py         # 每分鐘檢查提醒並推播
├── requirements.txt    # 相依套件清單
├── render.yaml / Procfile  # 雲端部署設定
```

---
