# NPOSystem — 非營利組織管理系統

將舊有 **Access 前端 + MS-SQL 後端** 的非營利組織管理系統，轉換為現代化 **Web-Based + PostgreSQL + Python** 架構。

## 子系統

| 模組 | 代號 | 說明 |
|:-----|:-----|:------|
| 捐款系統 | DonationSys | 捐款人管理、捐款紀錄、自動扣款、會計報表、銀行類別 |
| 組織系統 | OrganizeSys | 黨員管理、個人資料、公職人員、黨費、活動、推薦人 |

## 技術棧

- **前端**: Next.js 14 + TypeScript + shadcn/ui + Tailwind CSS
- **後端**: FastAPI + SQLAlchemy + Pydantic (Python 3.11)
- **資料庫**: PostgreSQL 16 + Redis 7
- **容器化**: Docker + Docker Compose

## 快速啟動

```bash
cd config
docker compose -p NPOSystem up -d
```

## 文件

- [功能需求規格書](docs/功能需求規格書.md)
- [系統設計文件](docs/SYSTEM_DESIGN.md)
- [API 參考手冊](docs/api/API.md)

## 授權

Private
