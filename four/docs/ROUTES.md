# 路由設計：數位足跡-碳排放行為帳本

## 1. 路由總覽表格

| 功能模組 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| 註冊頁面 | GET | `/register` | `templates/auth/register.html` | 顯示註冊表單 |
| 處理註冊 | POST | `/register` | — | 接收表單，寫入資料庫，重導向至登入頁 |
| 登入頁面 | GET | `/login` | `templates/auth/login.html` | 顯示登入表單 |
| 處理登入 | POST | `/login` | — | 驗證帳密，設定 Session，重導向至首頁 |
| 登出 | GET | `/logout` | — | 清除 Session，重導向至登入頁 |
| 儀表板(首頁) | GET | `/` | `templates/index.html` | 顯示累積碳排、目標進度與近期紀錄列表 |
| 登錄行為頁面 | GET | `/records/new` | `templates/ledger/record.html` | 顯示行為分類登錄表單 |
| 建立行為紀錄 | POST | `/records` | — | 接收表單，計算碳排與建議，存入 DB，重導向 |
| 刪除行為紀錄 | POST | `/records/<id>/delete` | — | 刪除單筆紀錄，重導向至首頁 |
| 視覺化報表 | GET | `/report` | `templates/report/index.html` | 顯示圖表統計數據 |
| 目標設定頁面 | GET | `/target` | `templates/report/target.html` | 顯示每月減碳目標設定表單 |
| 更新目標 | POST | `/target` | — | 接收表單，更新 DB，重導向至首頁 |

---

## 2. 每個路由的詳細說明

### 帳號驗證 (Auth)
- **`GET /register`**
  - **輸入**：無
  - **處理**：無特殊邏輯
  - **輸出**：渲染 `register.html`
- **`POST /register`**
  - **輸入**：表單 `username`, `password`, `confirm_password`
  - **處理**：檢查帳號是否重複、密碼與確認密碼是否相符、將密碼 bcrypt 雜湊後呼叫 `User.create()`
  - **輸出**：成功後 Flash 訊息，重導向至 `/login`
- **`GET /login`**
  - **輸入**：無
  - **處理**：若已登入則重導向 `/`
  - **輸出**：渲染 `login.html`
- **`POST /login`**
  - **輸入**：表單 `username`, `password`
  - **處理**：呼叫 `User.get_by_username()` 比對密碼，正確則將 `user_id` 寫入 Session
  - **輸出**：成功後重導向 `/`；失敗則 Flash 錯誤回 `login.html`
- **`GET /logout`**
  - **輸入**：無
  - **處理**：清除 Session 內的 `user_id`
  - **輸出**：重導向至 `/login`

### 行為帳本 (Ledger)
- **`GET /`**
  - **輸入**：無（從 Session 取得 `user_id`）
  - **處理**：呼叫 `CarbonRecord.get_all_by_user()` 取回歷史紀錄，計算本月總碳排量，比對目標。
  - **輸出**：渲染 `index.html` 帶入數據
- **`GET /records/new`**
  - **輸入**：無
  - **處理**：無特殊邏輯
  - **輸出**：渲染 `record.html`
- **`POST /records`**
  - **輸入**：表單 `category`, `action_name`, `parameter_value`
  - **處理**：透過碳排係數字典計算 `carbon_amount`，並根據行為決定 `suggestion`（例如：開車建議改搭大眾運輸）。呼叫 `CarbonRecord.create()` 寫入 DB。
  - **輸出**：Flash 計算結果與建議，重導向至 `/`
- **`POST /records/<id>/delete`**
  - **輸入**：URL 參數 `id`
  - **處理**：呼叫 `CarbonRecord.delete(id)`（需確保為該使用者的紀錄）
  - **輸出**：重導向至 `/`

### 報表與目標 (Report)
- **`GET /report`**
  - **輸入**：無
  - **處理**：呼叫 `CarbonRecord.get_all_by_user()`，將數據依類別或時間分組聚合，準備給前端繪圖
  - **輸出**：渲染 `report/index.html`
- **`GET /target`**
  - **輸入**：無
  - **處理**：呼叫 `User.get_by_id()` 取得目前的目標數值
  - **輸出**：渲染 `report/target.html`
- **`POST /target`**
  - **輸入**：表單 `target_carbon_emission`
  - **處理**：呼叫 `User.update_target()`
  - **輸出**：Flash 成功訊息，重導向至 `/`

---

## 3. Jinja2 模板清單

所有的模板檔案會建立在 `app/templates/` 中。

| 檔案名稱 | 繼承自 | 說明 |
| :--- | :--- | :--- |
| `base.html` | (無) | 共用排版，包含 `<head>`、導覽列 (Navbar)、Flash 訊息與 Footer。 |
| `index.html` | `base.html` | 首頁儀表板，顯示總覽數據與行為列表。 |
| `auth/login.html` | `base.html` | 登入表單。 |
| `auth/register.html` | `base.html` | 註冊表單。 |
| `ledger/record.html` | `base.html` | 新增行為紀錄表單。 |
| `report/index.html` | `base.html` | 包含 Chart.js 圓餅圖與折線圖的視覺化報表。 |
| `report/target.html` | `base.html` | 設定每月減碳目標的表單。 |
