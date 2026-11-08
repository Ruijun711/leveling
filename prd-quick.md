---
name: prd-quick
description: "先把為什麼做、替誰做、這一版做到哪裡講清楚"
metadata:
  type: work-package
  variant: quick
  source: launch-atlas
  stage: "define"
  roles: ["pm"]
  deliverable_slug: "prd"
  context_strategy: repository-first
---

# PRD · 產品需求文件 · Quick (≤ 12 行) · 工作包

**何時用：** 團隊 ≥ 3 人、跨職能新功能、需求穩定度 < 60% 時必要

**AI 加速：** 先讓 AI 找出未知，再依範本產生草稿；人負責確認需求、範圍與驗收標準

## Agent 協作規則

1. 這份工作包定義輸出品質，不代表上游文件必須依序存在。
2. 先搜尋 Repository、既有文件、設定與測試；找到等價證據即可使用，並標示來源路徑。
3. 人類負責需求、限制、驗收標準與衝突決策。不得替人類猜測決策。
4. 先回報 FOUND、MISSING、CONFLICT。只有缺口會改變輸出時才提問，每次最多 5 題。
5. 資訊不足但不阻擋草稿時保留 TODO，並註明需要什麼證據，不得編造。

## 輸出範本

```
---
doc_type: "prd"
variant: "light"
status: "draft"
owner: "<your-name>"
last_updated: "YYYY-MM-DD"
upstream:
  required: ["project-brief", "jtbd"]
  optional: ["value-hypothesis"]
---

# Product Requirements: <product-name>

**Status:** Draft v0.X · **Owner:** <name> · **Last updated:** YYYY-MM-DD

> [!IMPORTANT]
> **AI 填寫規則：** 本範本 7 段（編號 1, 2, 5, 6, 9, 10, 12），全部必填——刻意沿用完整版的章節編號讓兩版可對照。每結論行內加 `（依據：brief §XXX / JTBD-NNN）`；每量化欄位加 `[H]/[M]/[L]` confidence badge；缺資料寫 `_TODO: 需要 XXX_` 不編造；不寫 how。

---

## 1. Executive Summary

<!-- ai-fill: 3-5 行，主管 30 秒讀完。只寫「解什麼問題、給誰、預期影響」，不寫實作 -->

<3-5 行說明>

> **TL;DR:** <一句話總結>

---

## 2. Goals & Non-Goals

### Goals

<!-- ai-rule: 1-3 個 Goal + 必填 Counter-metric 行（防 goal-hacking） -->

| # | Goal | Why this matters | Success metric | Confidence |
|---|---|---|---|---|
| G1 | <具體目標> | <業務影響> | <可量測門檻> | **[H]** |
| **Counter** | <反指標> | <防止為衝 G1 而破壞的東西> | <門檻> | **[H]** |

### Non-Goals

- [NO] **Not solving:** <X> — Rationale: <為何不在 scope，屬哪張卡>

---

## 5. Functional Requirements

<!-- ai-rule: 輕量版只列 P0，3-5 個為宜。P0 必須對應上游 value-hypothesis.riskiest_assumption -->

### FR-1: <name> · Priority **P0** · **[H]**

- **Statement:** <做什麼，不寫怎麼做>
- **Acceptance:**
  - Given <前置條件>
  - When <使用者動作>
  - Then <系統預期行為>
- **Source:** brief §待解痛點 + JTBD-001

### FR-2: ...

---

## 6. NFR

<!-- ai-rule: 輕量版至少 2 象限（latency 必填 + 1 個 critical）。不適用的象限直接省略 -->

| Dimension | Target | Rationale | Confidence |
|---|---|---|---|
| **Latency** | p95 < Xs | <對應 JTBD success_criteria> | **[H]** |
| **<critical 2nd>** | <target> | <rationale> | **[H]** |

---

## 9. Risks（top 3）

<!-- ai-rule: 只列 top 3，每條含「失效模式 + Mitigation + Owner」三件 -->

> **R1:** <風險描述> — **Mitigation:** <如何降低> — **Owner:** <誰負責>
>
> **R2:** ...
>
> **R3:** ...

---

## 10. Decision Log（key 2-3 條）

<!-- ai-rule: 每條必含 chosen + 至少 1 個 rejected + 拒絕原因 -->

| Date | Decision | Options | Chosen | Rejected why | Confidence |
|---|---|---|---|---|---|
| YYYY-MM-DD | <決策題目> | A / B | A | B (成本 > 收益) | **[H]** |

---

## 12. Confidence & Sources & TODO

- **整份文件最低 confidence 欄位：** <列出所有 [L] 與 [M]>
- **Fabricated assumptions（推測但 input 未明說）：**
  - <假設 1>
- **Highest-value next input:** <下一份最該補的訪談 / 資料類型>

### TODO（缺資料）

- _TODO: 需要 XXX 校準 G1 baseline_

---

> [!CAUTION]
> **輸出前 AI 自檢：**
> - [ ] 7 段 H2 章節齊全（編號 1, 2, 5, 6, 9, 10, 12，刻意不連號）
> - [ ] 每個 FR / Goal / NFR 帶 inline `[H/M/L]` badge
> - [ ] Goals 表含 `**Counter**` 行
> - [ ] Decision Log ≥ 1 條，每條有 rejected reason
> - [ ] NFR 至少 2 象限（latency 必填）
> - [ ] 無 YAML / JSON schema 輸出（PRD 是給人讀的 markdown）
```
