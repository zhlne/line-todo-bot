# LINE Bot 智慧提醒系統

這是一個使用 Flask 製作的 LINE Bot 提醒系統，讓使用者可以透過 LINE 聊天輸入指令，新增、查詢或刪除提醒事項，並在指定時間自動推播提醒訊息。

## ✅ 支援指令

- `新增 HH:MM 提醒內容`：新增一筆提醒  
- `查詢`：列出所有提醒事項  
- `刪除 提醒內容`：刪除指定提醒  
- `刪除全部`：刪除目前用戶的所有提醒

## 🕒 功能簡介

- 使用 APScheduler 每分鐘比對當前時間
- 使用 LINE Messaging API 推播提醒
- 使用 PostgreSQL 儲存每位用戶的提醒資料
- 可部署至 Render 等雲端平台

## 📦 技術棧

- Flask
- Flask-SQLAlchemy
- Flask-APScheduler
- LINE Bot SDK v3
- PostgreSQL

## 📁 快速部署

1. 安裝套件：
   ```bash
   pip install -r requirements.txt
   ```

2. 設定環境變數：
   ```
   CHANNEL_SECRET=
   CHANNEL_ACCESS_TOKEN=
   DATABASE_URL=
   ```

3. 執行應用：
   ```bash
   gunicorn app:app
   ```

## 🙋‍♂️ 作者

GitHub: [@zhlne](https://github.com/zhlne)
