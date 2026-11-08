---
name: acceptance-criteria-quick
description: "讓「做完了」這句話有客觀證據"
metadata:
  type: work-package
  variant: quick
  source: launch-atlas
  stage: "define"
  roles: ["po", "qa"]
  deliverable_slug: "acceptance-criteria"
  context_strategy: repository-first
---

# Acceptance Criteria · 驗收條件 · Quick (≤ 12 行) · 工作包

**何時用：** 每個 user story 進 sprint 前必備

**AI 加速：** 用 Claude 從 user story → Given/When/Then 驗收 + edge case

## Agent 協作規則

1. 這份工作包定義輸出品質，不代表上游文件必須依序存在。
2. 先搜尋 Repository、既有文件、設定與測試；找到等價證據即可使用，並標示來源路徑。
3. 人類負責需求、限制、驗收標準與衝突決策。不得替人類猜測決策。
4. 先回報 FOUND、MISSING、CONFLICT。只有缺口會改變輸出時才提問，每次最多 5 題。
5. 資訊不足但不阻擋草稿時保留 TODO，並註明需要什麼證據，不得編造。

## 輸出範本

```
---
doc_type: "acceptance-criteria"
variant: "light"
status: "draft"
owner: "<your-name>"
last_updated: "YYYY-MM-DD"
upstream:
  required: ["user-story", "prd"]
  optional: ["test-data-fixtures"]
---

# Acceptance Criteria: <story-or-feature-name>

**Status:** Draft v0.X · **Owner:** <PO / QA name> · **Last updated:** YYYY-MM-DD

> [!IMPORTANT]
> **AI 填寫規則：** 本範本 5 段（編號 1, 2, 4, 10, 12），全部必填——刻意沿用完整版章節編號讓兩版可對照。每條 AC 必須 Given/When/Then 三段，**禁主觀字眼**（順、好用、合理）；每條附 `（依據：story §X / PRD §Y）` 行內引用 + `[H/M/L]` badge；缺資料寫 `_TODO: 需要 XXX_` 不編造。

---

## 1. Executive Summary

<!-- ai-fill: 3-5 行，列出 happy path 數 / edge case 數 / 涵蓋的 NFR 象限 / 最弱 confidence 項 -->

<3-5 行說明>

> **TL;DR:** <一句話：這個 story 做到什麼程度算 done>

---

## 2. Acceptance Criteria

<!-- ai-rule: 輕量版 ≥ 2 條 happy + ≥ 1 條 edge + ≥ 1 條 error。每條 Given/When/Then，無主觀字眼，可被自動化測試碼直接消費 -->

### AC-1 · Happy path · **[H]**

- **Given:** <初始狀態 + 資料 + 環境>
- **When:** <使用者動作 + 輸入>
- **Then:** <可驗證的結果 + 資料變化 + 副作用>
- **Source:** story §X.action

### AC-2 · Edge case (<empty / oversize / concurrency / perm-denied / 任選一類>) · **[H]**

- **Given:** ...
- **When:** ...
- **Then:** ...
- **Source:** PRD §NFR

### AC-3 · Error path · **[M]**

- **Given:** ...
- **When:** ...
- **Then:** <顯示 error code XXX + log level + retry policy>
- **Source:** ...

---

## 4. NFR Constraints（最小集）

<!-- ai-rule: 輕量版至少 1 個 performance + 1 個 security/audit，無關象限可省略 -->

| Dimension | Threshold | How to verify | Confidence |
|---|---|---|---|
| **Latency** | p95 < Xms at <量測點> | k6 load test | **[H]** |
| **<critical 2nd>** | <target> | <how> | **[M]** |

---

## 10. Decision Log（key 1-2 條）

<!-- ai-rule: 每條必含 chosen + 至少 1 個 rejected option + 拒絕原因 -->

| Date | Decision | Options | Chosen | Rejected why |
|---|---|---|---|---|
| YYYY-MM-DD | <例：edge case A 拆兩條還是合併> | split / merge | split | merge (失敗訊息不同，QA 難寫 assertion) |

---

## 12. Confidence & Sources & TODO

- **最低 confidence 項：** <列出所有 [L] 與 [M]>
- **Fabricated assumptions（推測但 input 未明說）：**
  - <假設 1，例：既有 mock 可用、第三方 sandbox 穩定>
- **Highest-value next input:** <NFR 數字 / 合規條款全文 / 既有 mock 清單 三選一>

### TODO（缺資料）

- _TODO: 需要 XXX 校準 p95 threshold_

---

> [!CAUTION]
> **輸出前 AI 自檢：**
> - [ ] 5 段 H2 章節齊全（編號 1, 2, 4, 10, 12，刻意不連號）
> - [ ] ≥ 2 條 happy + ≥ 1 條 edge + ≥ 1 條 error path
> - [ ] 每條 AC 含 Given/When/Then 三段且無主觀字眼（順、好用、合理）
> - [ ] 每條 AC 帶 `[H/M/L]` badge + `（依據：...）` 行內引用
> - [ ] NFR 段至少 1 個 latency + 1 個 security/audit 象限
> - [ ] Decision Log ≥ 1 條，每條有 rejected reason
> - [ ] 無 YAML / JSON schema 輸出（AC 是給人 + 機器讀的 markdown）
```
