---
name: api-spec-quick
description: "Freeze 契約，讓 FE/BE/QA 可平行開發"
metadata:
  type: work-package
  variant: quick
  source: launch-atlas
  stage: "design"
  roles: ["architect", "sd", "dev"]
  deliverable_slug: "api-spec"
  context_strategy: repository-first
---

# API Spec · OpenAPI 契約 · Quick (≤ 12 行) · 工作包

**何時用：** 跨團隊整合、FE/BE 並行開發、對外開放 API 時

**AI 加速：** 用 Claude 從 SRS / user story → OpenAPI 3.1 spec draft

## Agent 協作規則

1. 這份工作包定義輸出品質，不代表上游文件必須依序存在。
2. 先搜尋 Repository、既有文件、設定與測試；找到等價證據即可使用，並標示來源路徑。
3. 人類負責需求、限制、驗收標準與衝突決策。不得替人類猜測決策。
4. 先回報 FOUND、MISSING、CONFLICT。只有缺口會改變輸出時才提問，每次最多 5 題。
5. 資訊不足但不阻擋草稿時保留 TODO，並註明需要什麼證據，不得編造。

## 輸出範本

```
---
doc_type: "api-spec"
variant: "light"
status: "draft"
owner: "<your-name>"
last_updated: "YYYY-MM-DD"
upstream:
  required: ["srs", "user-story"]
  optional: ["api-style-guide", "error-taxonomy"]
---

# API Spec: <api-name> v0.X

**Status:** Draft · **Owner:** <Architect/BE Lead> · **Last updated:** YYYY-MM-DD

> [!IMPORTANT]
> **AI 填寫規則：** 本範本 6 段（編號 1, 2, 3, 5, 10, 12），全部必填——刻意沿用完整版的章節編號讓兩版可對照。每結論行內加 `（依據：srs §XXX）`；每欄位帶 `[H]/[M]/[L]` confidence badge；缺資料寫 `_TODO: 需要 XXX_` 不編造欄位或 error code；endpoint 涵蓋 happy path 即可，但 error response 至少含 400/401/500 三類。

---

## 1. Executive Summary

<!-- ai-fill: 3-5 行說明 API 用途、主要 consumer、freeze 狀態 -->

<3-5 行說明>

> **TL;DR:** <一句話：本 API 服務什麼業務動作>

---

## 2. Endpoints（核心 CRUD）

<!-- ai-rule: 輕量版列 3-5 個核心 endpoint。Idempotency 在 POST/PATCH 必標 -->

| Method | Path | Operation | Auth | Idempotency | Confidence |
|---|---|---|---|---|---|
| POST | `/v1/<resource>` | createX | `<resource>:write` | required | **[H]** |
| GET | `/v1/<resource>/{id}` | getX | `<resource>:read` | n/a | **[H]** |
| PATCH | `/v1/<resource>/{id}` | updateX | `<resource>:write` | optional | **[M]** |

---

## 3. Request / Response Schemas

<!-- ai-rule: 每個 endpoint 至少列出 required fields + 型別 + 主要 validation -->

### `POST /v1/<resource>` · Request

| Field | Type | Required | Validation |
|---|---|---|---|
| `customer_id` | string (uuid) | [YES] | pattern `^[0-9a-f-]{36}$` |
| `items` | array | [YES] | minItems 1, maxItems 100 |

### `POST /v1/<resource>` · Responses

| Status | Schema | Notes |
|---|---|---|
| `201` | `XCreated` | success |
| `400` | `ValidationError` | error codes: `INVALID_CUSTOMER`, `ITEMS_EMPTY` |
| `401` | `AuthError` | missing / invalid token |
| `409` | `IdempotencyConflict` | duplicate Idempotency-Key |
| `500` | `InternalError` | unhandled |

---

## 5. Error Taxonomy（核心）

<!-- ai-rule: 至少列出本 spec 涉及的 5-8 個 error code -->

| Code | HTTP | Retryable | User message key |
|---|---|---|---|
| `INVALID_CUSTOMER` | 400 | [NO] | `error.customer.invalid` |
| `ITEMS_EMPTY` | 400 | [NO] | `error.items.empty` |
| `AUTH_TOKEN_EXPIRED` | 401 | [NO] | `error.auth.expired` |

---

## 10. Decision Log

<!-- ai-rule: 每條必含 chosen + 至少 1 個 rejected option + 拒絕原因 -->

| Date | Decision | Options | Chosen | Rejected why | Confidence |
|---|---|---|---|---|---|
| YYYY-MM-DD | 分頁策略 | cursor / offset | cursor | offset (大資料集 deep page 效能差) | **[H]** |

---

## 12. Confidence & Sources & TODO

- **整份文件最低 confidence 欄位：** <列出所有 [L] 與 [M]>
- **Fabricated assumptions（推測但 input 未明說）：**
  - <假設 1：例：假設 JWT bearer auth>
- **Highest-value next input:** <下一份最該補的資料>

### TODO（缺資料）

- _TODO: 需要 BE 確認 ratelimit 預設值_

---

> [!CAUTION]
> **輸出前 AI 自檢：**
> - [ ] 6 段 H2 章節齊全（編號 1, 2, 3, 5, 10, 12，刻意不連號）
> - [ ] 每個 POST/PATCH endpoint 標 idempotency
> - [ ] Error response 至少含 400/401/500 三類
> - [ ] Decision Log ≥ 1 條，每條有 rejected reason
> - [ ] 無 YAML / JSON schema 直接傾倒（用表格表達 spec 結構）
```
