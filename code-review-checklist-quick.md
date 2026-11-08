---
name: code-review-checklist-quick
description: "把 review 從個人品味變成可重現流程"
metadata:
  type: work-package
  variant: quick
  source: launch-atlas
  stage: "build"
  roles: ["dev"]
  deliverable_slug: "code-review-checklist"
  context_strategy: repository-first
---

# Code Review Checklist · Quick (≤ 12 行) · 工作包

**何時用：** review 品質依賴特定資深人員、或新人 onboarding 多時

**AI 加速：** 用 Claude 跑 first-pass，人類專注 trade-off 與邊界情況

## Agent 協作規則

1. 這份工作包定義輸出品質，不代表上游文件必須依序存在。
2. 先搜尋 Repository、既有文件、設定與測試；找到等價證據即可使用，並標示來源路徑。
3. 人類負責需求、限制、驗收標準與衝突決策。不得替人類猜測決策。
4. 先回報 FOUND、MISSING、CONFLICT。只有缺口會改變輸出時才提問，每次最多 5 題。
5. 資訊不足但不阻擋草稿時保留 TODO，並註明需要什麼證據，不得編造。

## 輸出範本

```
---
doc_type: "code-review-checklist"
variant: "light"
status: "draft"
owner: "<your-name>"
last_updated: "YYYY-MM-DD"
upstream:
  required: ["git-diff", "coding-standard"]
  optional: ["existing-checklist"]
---

# Code Review Checklist: <PR-or-module-name>

**Status:** Draft v0.X · **Owner:** <Dev Lead name> · **Last updated:** YYYY-MM-DD

> [!IMPORTANT]
> **AI 填寫規則：** 本範本 5 段（編號 1, 2, 5, 9, 12），全部必填——刻意沿用完整版的章節編號讓兩版可對照。每個 finding 行內加 `（依據：diff path:line / standard §X）`；每 finding 帶 `[H]/[M]/[L]` confidence badge；缺資料寫 `_TODO: 需要 XXX_` 不編造；輕量版只列 must_block 與 should_fix，nit 可省略。

---

## 1. Executive Summary

<!-- ai-fill: 3-5 行，reviewer 30 秒看完。內容：總 finding 數、must_block 數、最危險的 1-2 條 -->

<3-5 行說明>

> **TL;DR:** <一句話：這個 PR 該不該擋下、為什麼>

---

## 2. Dimension Coverage

<!-- ai-rule: 7 象限全列，沒 finding 也要寫「已檢視，無 finding」。輕量版可合併 a11y 為 N/A 並寫原因 -->

| Dimension | Status | Finding count | Confidence |
|---|---|---|---|
| Correctness | covered | 2 | **[H]** |
| Readability | covered | 1 | **[H]** |
| Perf | covered | 0 (已檢視) | **[M]** |
| Security | covered | 1 | **[H]** |
| Test | covered | 1 | **[H]** |
| Observability | covered | 0 (已檢視) | **[M]** |
| A11y | N/A (backend-only PR) | 0 | **[H]** |

---

## 5. Findings

<!-- ai-rule: 輕量版只列 must_block + should_fix，nit 省略。每條附 file:line + suggested_fix + source -->

### F-001 · Severity **must_block** · **[H]**

- **File:line:** `<path>:<line>`
- **Dimension:** security
- **Evidence:** `<code snippet 或 standard §X>`
- **Suggested fix:** <一句話>
- **Source:** diff §XX + standard §YY

### F-002 · Severity **should_fix** · **[M]**

- ...

---

## 9. Risks（top 3）

<!-- ai-rule: 只列 top 3，每條含「失效模式 + Mitigation + Owner」三件 -->

> **R1:** <風險描述> — **Mitigation:** <如何降低> — **Owner:** <誰負責>
>
> **R2:** ...
>
> **R3:** ...

---

## 12. Confidence & Sources & TODO

- **整份 checklist 最低 confidence 項：** <列出所有 [L] 與 [M] finding>
- **Fabricated assumptions（推測但 input 未明說）：**
  - <假設 1>
- **Highest-value next input:** <e.g. SLO 監控設定 / production incident 史>

### TODO（缺資料）

- _TODO: 需要 perf benchmark 確認 F-003 是否升級_

---

> [!CAUTION]
> **輸出前 AI 自檢：**
> - [ ] 5 段 H2 章節齊全（編號 1, 2, 5, 9, 12，刻意不連號）
> - [ ] 每個 finding 帶 inline `[H/M/L]` badge + `file:line` + suggested_fix
> - [ ] Dimension Coverage 7 象限全列，N/A 須寫原因
> - [ ] Findings 至少分 must_block / should_fix 兩級
> - [ ] Risks 每條格式：失效模式 + Mitigation + Owner
> - [ ] 無 YAML / JSON schema 輸出（checklist 是給人讀的 markdown）
```
