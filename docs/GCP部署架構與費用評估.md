# NPOSystem — Google Cloud Platform (GCP) 部署架構建議與費用評估

**版本**: 0.1.0  
**更新日期**: 2026-07-17  
**狀態**: 📝 草案 — 待確認後執行  

---

## 目錄

1. [GCP 服務概覽](#1-gcp-服務概覽)
2. [架構方案比較](#2-架構方案比較)
3. [方案 A：Cloud Run 首選方案（推薦）](#3-方案-acloud-run-首選方案推薦)
4. [方案 B：Compute Engine 傳統方案](#4-方案-bcompute-engine-傳統方案)
5. [測試環境 vs 正式環境配置](#5-測試環境-vs-正式環境配置)
6. [費用評估總表](#6-費用評估總表)
7. [CI/CD 部署流程](#7-cicd-部署流程)
8. [啟動步驟](#8-啟動步驟)
9. [附錄：GCP 免費方案](#9-附錄gcp-免費方案)

---

## 1. GCP 服務概覽

NPOSystem 技術棧對應的 GCP 託管服務：

| NPOSystem 元件 | GCP 對應服務 | 說明 |
|:---------------|:-------------|:------|
| **Next.js 前端** | Cloud Run / Compute Engine | 容器化 Node.js 應用 |
| **FastAPI 後端** | Cloud Run / Compute Engine | 容器化 Python 應用 |
| **PostgreSQL 16** | Cloud SQL for PostgreSQL | 代管資料庫，自動備份 |
| **Redis 7** | Memorystore for Redis | 代管 Redis，Session 快取 |
| **Docker 映像** | Artifact Registry | 容器映像儲存庫 |
| **靜態檔案** | Cloud Storage | 圖片、匯出檔案存放 |
| **網域名稱** | Cloud DNS | DNS 代管 |
| **SSL 憑證** | Google-managed SSL | 自動憑證管理 |
| **監控日誌** | Cloud Monitoring + Logging | 效能監控與錯誤日誌 |
| **CI/CD** | Cloud Build / Cloud Deploy | 自動化建置部署 |

---

## 2. 架構方案比較

| 項目 | 🏆 方案 A：Cloud Run | 方案 B：Compute Engine |
|:-----|:--------------------:|:----------------------:|
| **管理難度** | ⭐ 極低（Serverless） | ⭐⭐⭐ 中等（需管理 VM） |
| **擴展方式** | 自動水平擴展（0→N） | 手動/自動調整機器規模 |
| **閒置費用** | ❌ 無（閒置不收費） | ✅ 有（VM 開著就計費） |
| **適合環境** | 測試 + 正式皆可 | 正式環境（高流量） |
| **Docker 支援** | ✅ 原生支援容器 | ✅ 自行管理 Docker |
| **冷啟動時間** | ⚠️ 約 2~5 秒 | ✅ VM 常駐無冷啟動 |
| **每月費用(測試)** | **~$25 USD** | **~$60 USD** |
| **每月費用(正式)** | **~$85 USD** | **~$130 USD** |

---

## 3. 方案 A：Cloud Run 首選方案（推薦）

### 3.1 架構圖

```
                          ┌─────────────┐
                          │  Cloud DNS  │
                          │  npodomain  │
                          └──────┬──────┘
                                 │
                          ┌──────┴──────┐
                          │  Cloud Load │
                          │  Balancer   │
                          └──────┬──────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
     ┌──────┴──────┐    ┌──────┴──────┐    ┌─────────┴─────────┐
     │  Cloud Run   │    │  Cloud Run   │    │  Cloud Storage    │
     │  Frontend   │    │  Backend API │    │  (靜態檔案/匯出)    │
     │  Next.js 14 │    │  FastAPI     │    │                   │
     │  Port 3001  │    │  Port 8001   │    │                   │
     └──────┬──────┘    └──────┬──────┘    └───────────────────┘
            │                  │
            │                  │
            │           ┌──────┴──────┐
            │           │ Cloud SQL   │
            │           │ PostgreSQL  │
            │           │ 16 (minimal)│
            │           └──────┬──────┘
            │                  │
            │           ┌──────┴──────┐
            │           │ Memorystore │
            │           │ Redis 7     │
            │           └─────────────┘
            │
     ┌──────┴──────┐
     │ Artifact    │
     │ Registry    │
     │ (Docker)    │
     └─────────────┘
```

### 3.2 測試環境配置 (Staging)

| 服務 | 規格 | 配置說明 |
|:-----|:-----|:---------|
| **Cloud Run - Frontend** | 1 vCPU, 1GB RAM, min=0, max=2 | 閒置時自動縮至 0 |
| **Cloud Run - Backend** | 1 vCPU, 1GB RAM, min=0, max=2 | 閒置時自動縮至 0 |
| **Cloud SQL PostgreSQL** | db-f1-micro (0.25 vCPU, 0.6GB, 10GB SSD) | 共用核心，最低配置 |
| **Memorystore Redis** | 基本版 1GB | 測試用不需高可用 |
| **Cloud Storage** | 標準儲存桶 ~5GB | 靜態檔案 |
| **Artifact Registry** | 基本版 | Docker 映像儲存 |

### 3.3 正式環境配置 (Production)

| 服務 | 規格 | 配置說明 |
|:-----|:-----|:---------|
| **Cloud Run - Frontend** | 2 vCPU, 2GB RAM, min=1, max=10 | 保持至少 1 個實例 |
| **Cloud Run - Backend** | 2 vCPU, 2GB RAM, min=1, max=10 | 保持至少 1 個實例 |
| **Cloud SQL PostgreSQL** | db-custom-1-3840 (1 vCPU, 3.75GB, 50GB SSD) | 專用核心，自動備份 |
| **Memorystore Redis** | 標準版 2GB (高可用) | 雙節點主從架構 |
| **Cloud Storage** | 標準儲存桶 ~20GB | 靜態檔案 + 備份 |
| **Cloud Load Balancer** | 外部 HTTPS 負載平衡器 | SSL 終止 + CDN |
| **Cloud DNS** | 代管區域 | DNS 解析 |
| **Cloud Armor** | WAF 安全防護 | DDoS 防護 + IP 白名單 |

---

## 4. 方案 B：Compute Engine 傳統方案

### 4.1 架構圖

```
                          ┌─────────────┐
                          │  Cloud DNS  │
                          └──────┬──────┘
                                 │
                          ┌──────┴──────┐
                          │  Cloud Load │
                          │  Balancer   │
                          └──────┬──────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────┴───────┐        ┌───────┴───────┐
            │  VM Instance  │        │  VM Instance  │
            │  (Frontend)   │        │  (Backend)    │
            │  Docker Comp. │        │  Docker Comp. │
            │  Next.js      │        │  FastAPI      │
            └───────────────┘        └───────┬───────┘
                                             │
                                    ┌────────┴────────┐
                                    │  Cloud SQL      │
                                    │  PostgreSQL 16  │
                                    └────────┬────────┘
                                             │
                                    ┌────────┴────────┐
                                    │  Memorystore    │
                                    │  Redis 7        │
                                    └─────────────────┘
```

### 4.2 規格配置

**測試環境：** 1 台 e2-small VM (2 vCPU, 2GB RAM) + Cloud SQL db-f1-micro

**正式環境：** 2 台 e2-medium VM (各 2 vCPU, 4GB RAM) + Cloud SQL 專用核心

---

## 5. 測試環境 vs 正式環境配置

| 項目 | 🧪 測試/開發環境 | 🚀 正式/生產環境 |
|:-----|:----------------:|:----------------:|
| **目的** | 內部開發測試、功能驗證 | 對外正式上線營運 |
| **Cloud Run min** | 0（關機不計費） | 1（保持最低服務） |
| **Cloud Run max** | 2 | 10 |
| **PostgreSQL** | db-f1-micro (0.25 vCPU) | db-custom-1-3840 (1 vCPU) |
| **Redis** | 基本版 1GB | 標準版 2GB HA |
| **備份策略** | 無自動備份 | 每日自動備份 + 保留 7 天 |
| **SSL** | 可選 (非必要) | 強制 HTTPS |
| **監控告警** | 基本 (錯誤通知) | 完整 (CPU/記憶體/錯誤率) |
| **SLA** | 無保證 | 99.95%+ |
| **可維護時間** | 任何時間 | 公告維護視窗 |

---

## 6. 費用評估總表

### 6.1 方案 A：Cloud Run — 每月預估費用

#### 🧪 測試環境每月費用

| 服務 | 用量估算 | 月費 (USD) |
|:-----|:---------|:----------:|
| Cloud Run - Frontend | 1 vCPU, 1GB, 每月 200 小時 | ~$10 |
| Cloud Run - Backend | 1 vCPU, 1GB, 每月 200 小時 | ~$10 |
| Cloud SQL PostgreSQL | db-f1-micro, 10GB SSD | ~$7 |
| Memorystore Redis | 基本版 1GB | ~$0 (測試用可省略) |
| Cloud Storage | 5GB 標準 | ~$0.10 |
| Artifact Registry | 基本儲存 | ~$0.50 |
| **小計** | | **~$25/月** |
| **年費** | | **~$300/年** |

#### 🚀 正式環境每月費用

| 服務 | 用量估算 | 月費 (USD) |
|:-----|:---------|:----------:|
| Cloud Run - Frontend | 2 vCPU, 2GB, min=1, 每月 720 小時 | ~$35 |
| Cloud Run - Backend | 2 vCPU, 2GB, min=1, 每月 720 小時 | ~$35 |
| Cloud Load Balancer | 外部 HTTPS LB | ~$18 |
| Cloud SQL PostgreSQL | db-custom-1-3840, 50GB SSD | ~$55 |
| Memorystore Redis | 標準版 2GB HA | ~$40 |
| Cloud Storage | 20GB 標準 | ~$0.40 |
| Artifact Registry | Docker 映像儲存 | ~$0.50 |
| Cloud Logging | 基本用量 | ~$2 |
| **小計** | | **~$186/月** |
| **年費** | | **~$2,232/年** |

### 6.2 方案 B：Compute Engine — 每月預估費用

#### 🧪 測試環境

| 服務 | 月費 (USD) |
|:-----|:----------:|
| VM e2-small (2 vCPU, 2GB) | ~$17 |
| Cloud SQL db-f1-micro | ~$7 |
| **小計** | **~$24/月** |

#### 🚀 正式環境

| 服務 | 月費 (USD) |
|:-----|:----------:|
| VM x2 (e2-medium, 各 2 vCPU, 4GB) | ~$55 × 2 = $110 |
| Cloud SQL db-custom-1-3840 | ~$55 |
| Memorystore Redis 2GB HA | ~$40 |
| Load Balancer | ~$18 |
| **小計** | **~$223/月** |

### 6.3 費用比較總表

| 環境 | Cloud Run (方案 A) | Compute Engine (方案 B) |
|:-----|:------------------:|:----------------------:|
| 🧪 測試環境 | **~$25/月** | ~$24/月 |
| 🚀 正式環境 | **~$186/月** | ~$223/月 |
| 🏢 兩年總計 (測試+正式) | **~$5,064** | ~$5,928 |
| 管理維護成本 | ✅ 低 (Serverless) | ⚠️ 需定時 OS 更新 |

> 💡 **建議：** 測試環境使用 Cloud Run (可縮至 0 不計費)，正式環境可依團隊熟悉度選擇 Cloud Run 或 Compute Engine。

---

## 7. CI/CD 部署流程

### 7.1 建議部署流程

```
開發者 Push 到 GitHub main
        │
        ▼
Cloud Build Trigger 自動觸發
        │
        ├── 1. 建置 Frontend Docker 映像
        │       └── Push 至 Artifact Registry
        ├── 2. 建置 Backend Docker 映像
        │       └── Push 至 Artifact Registry
        ├── 3. 執行 DB Migration (Alembic)
        └── 4. 部署至 Cloud Run
                ├── Staging: 自動部署
                └── Production: 手動核准部署
```

### 7.2 cloudbuild.yaml 範例

```yaml
steps:
  # Backend Build
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/nposystem/backend:$SHORT_SHA', './backend']
  # Frontend Build
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/nposystem/frontend:$SHORT_SHA', './frontend']
  # Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/$PROJECT_ID/nposystem/backend:$SHORT_SHA']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/$PROJECT_ID/nposystem/frontend:$SHORT_SHA']
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'nposystem-backend'
      - '--image=us-central1-docker.pkg.dev/$PROJECT_ID/nposystem/backend:$SHORT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'nposystem-frontend'
      - '--image=us-central1-docker.pkg.dev/$PROJECT_ID/nposystem/frontend:$SHORT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
```

---

## 8. 啟動步驟

### 8.1 建立 GCP 專案

```bash
# 1. 登入 GCP
gcloud auth login

# 2. 建立新專案
gcloud projects create nposystem-project --name="NPOSystem"

# 3. 設定預設專案
gcloud config set project nposystem-project

# 4. 啟用所需 API
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  storage.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com
```

### 8.2 建立資料庫

```bash
# 測試環境
gcloud sql instances create nposystem-db-staging \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \
  --storage-size=10GB \
  --region=us-central1

# 正式環境
gcloud sql instances create nposystem-db-prod \
  --database-version=POSTGRES_16 \
  --tier=db-custom-1-3840 \
  --storage-size=50GB \
  --backup-start-time=02:00 \
  --region=us-central1

# 建立資料庫
gcloud sql databases create NPOSystem --instance=nposystem-db-staging
gcloud sql databases create NPOSystem --instance=nposystem-db-prod
```

### 8.3 部署至 Cloud Run

```bash
# 後端
gcloud run deploy nposystem-backend \
  --source ./backend \
  --region=us-central1 \
  --allow-unauthenticated

# 前端
gcloud run deploy nposystem-frontend \
  --source ./frontend \
  --region=us-central1 \
  --allow-unauthenticated
```

---

## 9. 附錄：GCP 免費方案

GCP 新用戶可獲得 **$300 USD 免費試用額度**（90 天內有效），可用於：

| 服務 | 免費方案內容 |
|:-----|:------------|
| **Cloud Run** | 每月 200 萬次請求 + 360,000 vCPU 秒 + 240,000 GB-秒記憶體 |
| **Cloud SQL** | ❌ 無免費方案 (PostgreSQL 最低 $7/月) |
| **Cloud Storage** | 5GB/月 標準儲存 |
| **Cloud Build** | 每月 120 分鐘建置時間 |
| **Artifact Registry** | 每月 0.5 GB 儲存 |

> 💡 **開發初期**可使用免費額度 + Cloud Run 的免費方案將費用壓至 **$7/月（僅 Cloud SQL）**，非常適合 MVP 階段。

---

## 附錄 B：建議 Region

| Region | 位置 | 適合原因 |
|:-------|:-----|:---------|
| `us-central1` ( Iowa ) | 美國中部 | 最便宜，最穩定 |
| `asia-east1` ( Taiwan ) | 台灣彰化 | 低延遲，價格略高 (~+10%) |
| `asia-northeast1` ( Tokyo ) | 日本東京 | 低延遲，價格中 (~+15%) |

> 💡 若主要使用者在台灣，建議使用 `asia-east1` (台灣) 以獲得最低延遲。

---

*本文件為評估建議，實際費用可能因使用量而異。建議使用 GCP Pricing Calculator 進行精算。*
