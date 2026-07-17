# NPOSystem — 系統設計文件

**版本**: 0.1.0 
**更新日期**: 2026-07-17  
**Git**: https://github.com/CCLSeiko/NPOSystem

---

## 目錄

1. [系統概述](#1-系統概述)
2. [技術架構](#2-技術架構)
3. [系統模組](#3-系統模組)
4. [資料庫設計](#4-資料庫設計)
5. [後端架構](#5-後端架構)
6. [前端架構](#6-前端架構)
7. [部署架構](#7-部署架構)
8. [目錄結構](#8-目錄結構)

---

## 1. 系統概述

### 1.1 專案背景

非營利組織管理系統 NPOSystem，以 **Web-Based + PostgreSQL + Python** 架構為主，
同步規劃手機網頁 APP 架構應用，需要包含可以整合 Google 帳號認證與 LINE APP 使用方式，
透過 QR Code 建立分享帳號機制。

### 1.2 子系統

| 模組 | 代號 | 說明 | 核心功能 |
|------|------|------|----------|
| 捐款系統 | DonationSys | 捐款相關管理 | 捐款人管理、捐款紀錄、自動扣款、會計報表、銀行類別 |
| 組織系統 | OrganizeSys | 組織與黨員管理 | 黨員管理、個人資料、公職人員、黨費、活動、推薦人、推薦人點數管理、推薦新成員、點數獎勵 |

### 1.3 使用者角色

| 角色 | 權限範圍 |
|------|----------|
| 系統管理員 | 所有功能 + 代碼表維護 + 員工管理 |
| 捐款管理員 | 捐款系統全部功能 |
| 組織管理員 | 組織系統全部功能 |
| 一般使用者 | 檢視權限 |

---

## 2. 技術架構

```
┌─────────────────────────────────────────────────────────┐
│                    使用者瀏覽器                           │
│              Chrome / Firefox / Edge                    │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS
┌───────────────────────┴─────────────────────────────────┐
│                    Frontend (Next.js 14)                │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ App Router  │  │ Server       │  │ shadcn/ui      │  │
│  │ 16 Pages    │  │ Components   │  │ + Tailwind CSS │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Client      │  │ API Client   │  │ TypeScript     │  │
│  │ Components  │  │ (apiFetch)   │  │ Types          │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
└───────────────────────┬─────────────────────────────────┘
                        │ REST API (JSON)
┌───────────────────────┴─────────────────────────────────┐
│                    Backend (FastAPI)                    │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ API Routes  │  │ Services     │  │ Pydantic       │  │
│  │ 70+         │  │ (Business    │  │ Schemas        │  │
│  │ Endpoints   │  │  Logic)      │  │ (Validation)   │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
│  ┌─────────────┐  ┌──────────────┐                      │
│  │ SQLAlchemy  │  │ AsyncPG      │                      │
│  │ ORM Model   │  │ (Async)      │                      │
│  └─────────────┘  └──────────────┘                      │
└───────────────────────┬─────────────────────────────────┘
                        │ AsyncPG
┌───────────────────────┴─────────────────────────────────┐
│                Database (PostgreSQL 16)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                 │
│  │ common   │ │ donation │ │ organize │                 │
│  │ (22 tbl) │ │ (15 tbl) │ │ (10 tbl) │                 │
│  └──────────┘ └──────────┘ └──────────┘                 │
└─────────────────────────────────────────────────────────┘
```

### 2.1 技術棧

| 層級 | 技術 | 版本 | 說明 |
|------|------|------|------|
| **前端** | Next.js | 14.2 | React 框架 (App Router) |
| | TypeScript | 5.x | 型別安全 |
| | shadcn/ui | latest | 元件庫（基於 Radix UI） |
| | Tailwind CSS | 3.x | Utility-first CSS |
| | Lucide React | latest | 圖示庫 |
| **後端** | Python | 3.11+ | 語言 |
| | FastAPI | 0.115+ | Web 框架 |
| | SQLAlchemy | 2.0+ | ORM（非同步） |
| | AsyncPG | latest | PostgreSQL 非同步驅動 |
| | Pydantic | 2.x | 資料驗證 |
| **資料庫** | PostgreSQL | 16 | 關聯式資料庫 |
| | Redis | 7 | 快取 (Session) |
| **容器化** | Docker | latest | 容器 |
| | Docker Compose | latest | 容器編排 |
| **其他** | Alembic | latest | DB Migration |
| | OpenPyXL | latest | Excel 匯出 |

---

## 3. 系統模組

### 3.1 捐款系統 (DonationSys)

```
捐款人管理 (Donation-Donors)
  ├── 基本資料（姓名、電話、地址、身分證號）
  └── 備註

捐款管理 (Single-Donation)        ← 單次捐款紀錄(透過銀行郵局帳號轉帳及現金捐款)
  ├── 捐款人
  ├── 捐款紀錄（金額、日期、類別）
  └── 備註
  
自動扣款管理 (Auto-Donation)       ← 自動扣款紀錄(透過信用卡或銀行郵局帳號轉帳)
  ├── 捐款人 (Donation-Donors)
  └── 扣款紀錄

會計報表 (Donation ACC Reports)

銀行類別 (Donation Bank Types)
```

#### 資料流

```
捐款人新增/匯入 → 捐款紀錄登錄 → 自動扣款排程
                                      ↓
                              會計報表產生 (月/年)
```

### 3.2 組織系統 (OrganizeSys)

```
黨員管理 (Party Members)
  ├── 基本資料
  ├── 活動紀錄
  └── 列印紀錄

個人資料 (Personal Info)
  ├── 基本資料 + 黨籍狀態
  ├── 公職人員
  ├── 黨費紀錄
  └── 介紹人
```

#### 黨籍狀態代碼

| 代碼 | 狀態 |
|:---:|:-----|
| 1 | 現任黨員 |
| 2 | 新入黨 |
| A | 準備中 |
| B | 待審核 |
| X | 停權 |
| 3 | 退黨 |
| 9 | 死亡 |

---

## 4. 資料庫設計

### 4.1 Schema 劃分

| Schema | 用途 | 表格數 |
|--------|------|--------|
| `common` | 共用資料（員工、部門、代碼表、地址） | 22 |
| `donation` | 捐款系統 | 15 |
| `organize` | 組織系統 | 10 |

---

## 5. 後端架構

### 5.1 分層架構

```
API Routes (api/v1/)
    │
    ▼
Services (services/) — 業務邏輯層
    │
    ▼
ORM Models (models/) — 資料存取層
    │
    ▼
Database (PostgreSQL)
```

### 5.2 API 路由總計

| 路由檔案 | 端點數 | Prefix |
|----------|--------|--------|
| `common.py` | 12 | `/common` |
| `donation.py` | 19 | `/donation` |
| `organize.py` | 22 | `/organize` |
| `export.py` | 4 | `/export` |
| **合計** | **71** | |

### 5.3 資料驗證 (Pydantic Schemas)

每個 Module 分為三層：

- **Read** — 輸出（from_attributes=True）
- **Create** — 新增輸入
- **Update** — 更新輸入（所有欄位 Optional）

---

## 6. 前端架構

### 6.1 頁面結構

```
/ (登入頁)
└── /dashboard
    ├── /donation
    │   ├── /dona-donors-info          ← 捐款人資料
    │   ├── /dona-single-donation      ← 單次捐款紀錄
    │   ├── /dona-auto-donation        ← 自動扣款紀錄
    │   ├── /dona-bank-types           ← 銀行類別
    │   └── /dona-acc-reports          ← 會計報表
    ├── /organize
    │   ├── /org-party-info             ← 黨務管理
    │   ├── /org-personal-info          ← 黨員個人資料
    │   ├── /org-referrer-info          ← 推薦人資料
    │   ├── /org-referrer-points        ← 推薦人點數管理
    │   ├── /org-party-membership-dues  ← 黨費管理
    │   └── /org-government             ← 公職人員
    └── /system
        └── /comm-lookup-class        ← 通用類代碼表管理
```

### 6.2 頁面總計

| 類型 | 數量 | 路徑模式 |
|------|------|----------|
| 靜態頁面 (Static) | 13 | `/dashboard/*/page.tsx` |
| 動態詳情頁 (Dynamic) | 3 | `/dashboard/*/[id]/page.tsx` |
| **合計** | **16** | |

---

## 7. 部署架構

### 7.1 Docker 容器

```
┌────────────────┐  ┌───────────────┐  ┌────────────────┐  ┌────────────────┐
│  NPOSystem-db  │  │ NPOSystem-    │  │ NPOSystem-api  │  │ NPOSystem-     │
│  PostgreSQL    │  │ redis         │  │ FastAPI        │  │ frontend       │
│  16-alpine     │  │ 7-alpine      │  │ Python 3.11    │  │ Next.js 14     │
│  Port: 5434    │  │ Port: 6379    │  │ Port: 8001     │  │ Port: 3001     │
└────────────────┘  └───────────────┘  └────────────────┘  └────────────────┘
```

### 7.2 環境變數

| 變數 | 說明 | 開發環境值 |
|------|------|------------|
| `DATABASE_URL` | 非同步 DB 連線 (AsyncPG) | `postgresql+asyncpg://postgres:postgres@db:5434/NPOSystem` |
| `DATABASE_URL_SYNC` | 同步 DB 連線 (Psycopg2) | `postgresql://postgres:***@db:5434/NPOSystem` |
| `REDIS_URL` | Redis 連線 | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT 密鑰 | `dev-secret-key-change-in-production` |
| `CORS_ORIGINS` | 允許的來源 | `["http://localhost:3001"]` |
| `NEXT_PUBLIC_API_URL` | 前端 API 基底 | `http://localhost:8001/api/v1` |

### 7.3 啟動方式

```bash
# 完整啟動
cd config && docker compose -p NPOSystem up -d

# 啟動特定服務
docker compose -p NPOSystem up -d db redis

# 重建指定服務
docker compose -p NPOSystem up -d --build api

# 查看日誌
docker compose -p NPOSystem logs -f api

# 停止
docker compose -p NPOSystem down
```

---

## 附錄 A: 開發規範

### A.1 API 命名規範

- 路徑使用 kebab-case（`/acc-reports`）
- 路徑參數使用 snake_case（`{donor_no}`）
- Query 參數使用 snake_case（`page_size`）
- JSON body 欄位使用 snake_case（`order_type`）

### A.2 資料庫命名規範

- Schema: 英文字母小寫（`donation`, `organize`）
- Table: 複數蛇形命名（`donation_records`, `party_members`）
- 欄位: 蛇形命名（`donor_no`, `order_date`）
- PK 欄位: 單欄位優先（`donor_no`, `sn`）

### A.3 Python 規範

- Python 3.11+ Type Hints
- Async/Await 所有 I/O 操作
- Service 層注入 `AsyncSession`
- 所有 CRUD 方法命名：`list`, `get`, `create`, `update`, `delete`

### A.4 TypeScript 規範

- `'use client'` 用於互動性頁面
- 型別定義統一在 `types/index.ts`
- API 回傳統一經由 `apiFetch<T>()`
- 分頁資料使用 `{items, total, page, page_size, total_pages}`
