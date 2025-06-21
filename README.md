# LINE Bot 智慧提醒系統

## ✅ 支援指令

- `新增 HH:MM 提醒內容`：新增一筆提醒  
- `查詢`：查詢目前所有提醒事項  
- `刪除 提醒內容`：刪除指定提醒  
- `刪除全部`：刪除目前用戶的所有提醒資料

## 🕒 功能簡介

- 透過 LINE Bot 接收使用者輸入的提醒指令
- 使用 APScheduler 每分鐘自動比對目前時間（台灣時區）
- 到點自動透過 push message 傳送提醒訊息
- 使用 PostgreSQL 儲存提醒資料，並區分不同使用者
- 可部署至 Render 等平台自動執行

## 🧱 使用技術

- Flask：Web 應用與 API 接收
- Flask-SQLAlchemy：ORM 資料庫操作
- Flask-APScheduler：定時任務模組
- LINE Bot SDK v3：接收訊息與推播提醒
- PostgreSQL：儲存每位用戶的提醒紀錄

