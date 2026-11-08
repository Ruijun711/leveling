---
name: jtbd-quick
description: "把功能慾望翻成使用者真正想完成的任務"
metadata:
  type: work-package
  variant: quick
  source: launch-atlas
  stage: "discovery"
  roles: ["pm", "ux"]
  deliverable_slug: "jtbd"
  context_strategy: repository-first
---

# JTBD · 任務驅動 · Quick (≤ 12 行) · 工作包

**何時用：** 團隊在爭論「要做哪個功能」而非「使用者要解什麼問題」時

**AI 加速：** 用 Claude 把 persona + scenario 反推 JTBD statement

## Agent 協作規則

1. 這份工作包定義輸出品質，不代表上游文件必須依序存在。
2. 先搜尋 Repository、既有文件、設定與測試；找到等價證據即可使用，並標示來源路徑。
3. 人類負責需求、限制、驗收標準與衝突決策。不得替人類猜測決策。
4. 先回報 FOUND、MISSING、CONFLICT。只有缺口會改變輸出時才提問，每次最多 5 題。
5. 資訊不足但不阻擋草稿時保留 TODO，並註明需要什麼證據，不得編造。

## 輸出範本

```
---
doc_type: "jtbd"
variant: "light"
status: "draft"
owner: "<your-name>"
last_updated: "YYYY-MM-DD"
upstream:
  required: ["persona", "user-research"]
  optional: ["competitive-scan"]
---

# Jobs To Be Done: <product-name>

**Status:** Draft v0.X · **Owner:** <PM name> · **Last updated:** YYYY-MM-DD

> [!IMPORTANT]
> **AI 填寫規則：** 本範本 5 段，全部必填。每結論行內加 `（依據：interview §XXX）` 或 `（quote: "..."）` 可追溯；每量化欄位帶 `[H]/[M]/[L]` confidence badge；缺資料寫 `_TODO: 需要 XXX_` 不編造；JTBD statement **不能寫解法**（不出現「按鈕、頁面、API」這類 how）。

---

## 1. Executive Summary

<!-- ai-fill: 3-5 行說明：identified N 個 JTBDs、top 痛點主題、最強 evidence 來源 -->

<3-5 行說明>

> **TL;DR:** <一句話：使用者最常僱用這個產品來完成什麼任務>

---

## 2. JTBD Statements

<!-- ai-rule: 3-5 個 JTBD 為宜。每條格式：When <situation>, I want to <motivation>, so I can <expected outcome>。statement 中不能出現「按鈕/頁面/API」這類解法字眼 -->

| ID | Statement | Functional job | Confidence | Source |
|---|---|---|---|---|
| JTBD-001 | When <情境>, I want to <動機>, so I can <預期結果> | <核心功能任務> | **[H]** | interview-04 §3 |
| JTBD-002 | ... | ... | **[M]** | ... |

---

## 5. Current Solution & Success Criteria

<!-- ai-rule: 每個 P0 JTBD 都要列「現在怎麼解 + 為何不夠好 + 成功門檻」三件 -->

### JTBD-001

- **Current solution:** <使用者現在怎麼解這個問題>
- **Gap:** <為何不夠好>
- **Success criteria:** <做到什麼程度算解了>
- **Source:** interview §XX + ticket-keyword §YY

---

## 10. Decision Log

<!-- ai-rule: 每條必含 chosen + 至少 1 個 rejected option + 拒絕原因 -->

| Date | Decision | Options | Chosen | Rejected why |
|---|---|---|---|---|
| YYYY-MM-DD | 5 個 JTBD 用哪個維度排序 | by_frequency / by_pain_severity / by_strategic_fit | by_pain_severity | by_frequency (高頻不等於高痛)、by_strategic_fit (尚無策略明示) |

---

## 12. Confidence & Sources & TODO

- **整份文件最低 confidence 欄位：** <列出所有 [L] 與 [M] 欄位>
- **Fabricated assumptions（推測但 input 未明說）：**
  - <假設 1>
- **Highest-value next input:** <下一份最該補的訪談 / 觀察 / 競品流失訪談>

### TODO（缺資料）

- _TODO: 需要 X 份 switch interview 校準 emotional_job_

---

> [!CAUTION]
> **輸出前 AI 自檢：**
> - [ ] 5 段 H2 章節齊全（編號 1, 2, 5, 10, 12，刻意沿用完整版編號）
> - [ ] 每個 JTBD 帶 `[H/M/L]` confidence badge + `（依據：...）` 行內引用
> - [ ] 沒有任何 JTBD statement 出現解法字眼（按鈕 / 頁面 / API / 流程）
> - [ ] Current solution 段每個 JTBD 含 gap + success criteria 三件
> - [ ] Decision Log ≥ 1 條，每條有 rejected reason
> - [ ] 無 YAML / JSON schema 輸出（JTBD 是給人讀的 markdown）
```
