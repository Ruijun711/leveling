---
name: unit-test-quick
description: "讓重構不再靠賭"
metadata:
  type: work-package
  variant: quick
  source: launch-atlas
  stage: "build"
  roles: ["dev", "qa"]
  deliverable_slug: "unit-test"
  context_strategy: repository-first
---

# Unit Test · 單元測試 · Quick (≤ 12 行) · 工作包

**何時用：** 邏輯有分支、邊界條件、或會被其他模組依賴時

**AI 加速：** 用 Claude 從函數簽名生成 edge case 矩陣

## Agent 協作規則

1. 這份工作包定義輸出品質，不代表上游文件必須依序存在。
2. 先搜尋 Repository、既有文件、設定與測試；找到等價證據即可使用，並標示來源路徑。
3. 人類負責需求、限制、驗收標準與衝突決策。不得替人類猜測決策。
4. 先回報 FOUND、MISSING、CONFLICT。只有缺口會改變輸出時才提問，每次最多 5 題。
5. 資訊不足但不阻擋草稿時保留 TODO，並註明需要什麼證據，不得編造。

## 輸出範本

```
---
doc_type: "unit-test"
variant: "light"
status: "draft"
owner: "<your-name>"
last_updated: "YYYY-MM-DD"
upstream:
  required: ["function-signature", "spec"]
  optional: ["existing-coverage"]
---

# Unit Test Plan: <module-or-function-name>

**Status:** Draft v0.X · **Owner:** <Dev> · **Last updated:** YYYY-MM-DD

> [!IMPORTANT]
> **AI 填寫規則：** 本範本 6 段（編號 1, 2, 3, 4, 9, 12），全部必填——刻意沿用完整版的章節編號讓兩版可對照。每 test case 行內加 `（依據：spec §X / signature 推導）`；每 case 帶 `[H]/[M]/[L]` confidence badge；缺資料寫 `_TODO: 需要 XXX_` 不編造；**輕量版至少覆蓋 happy + boundary + error 三類**；不測 wiring code / setter / getter；不 mock 同 module 內 pure function。

---

## 1. Executive Summary

<!-- ai-fill: 3-5 行，Dev 30 秒讀完。內容：N 個 target、N 個 test case、覆蓋哪些 case 類別 -->

<3-5 行說明>

> **TL;DR:** <一句話：這份 plan 解什麼重構恐懼>

---

## 2. Targets

<!-- ai-rule: kind + name + signature + public_api 四件齊 -->

| Kind | Name | Signature | Public API | Confidence |
|---|---|---|---|---|
| function | `<fqn>` | `(input: T) => R` | true | **[H]** |

---

## 3. Test Cases（3 categories minimum）

<!-- ai-rule: 至少 happy / boundary / error 三類，每條附 input / expected / edge_rationale -->

### TC-001 · Category **happy** · **[H]**

- **Target:** `<fqn>`
- **Input:** `<inline value>`
- **Expected:** `<value 或 exception>`
- **Edge rationale:** 標準路徑
- **Source:** spec §XX

### TC-002 · Category **boundary** · **[H]**

- **Target:** `<fqn>`
- **Input:** `<邊界值，例：max int>`
- **Expected:** `<value>`
- **Edge rationale:** 邊界條件

### TC-003 · Category **error** · **[H]**

- **Target:** `<fqn>`
- **Input:** `<無效 input>`
- **Expected:** `throw ValidationError`
- **Edge rationale:** 錯誤路徑

---

## 4. Mocking Strategy

<!-- ai-rule: mock / do_not_mock + rationale。預設不 mock 同 module pure function -->

| Action | Items | Rationale |
|---|---|---|
| **Mock** | external IO / time / random / network | 不可控 |
| **Do not mock** | same-module pure function / value object | 同邏輯邊界 |

---

## 9. Risks（top 3）

<!-- ai-rule: 每條格式：失效模式 + Mitigation + Owner 三件齊 -->

> **R1:** <風險描述> — **Mitigation:** <如何降低> — **Owner:** <誰負責>
>
> **R2:** ...
>
> **R3:** ...

---

## 12. Confidence & Sources & TODO

- **整份 plan 最低 confidence 項：** <列出所有 [L] 與 [M]>
- **Fabricated assumptions（推測但 input 未明說）：**
  - <假設 1>
- **Highest-value next input:** <下一份最該補的 spec 細節 / production error log>

### TODO（缺資料）

- _TODO: spec 沒寫錯誤訊息文案，TC-003 expected 待補_

---

> [!CAUTION]
> **輸出前 AI 自檢：**
> - [ ] 6 段 H2 章節齊全（編號 1, 2, 3, 4, 9, 12，刻意不連號）
> - [ ] 至少覆蓋 happy + boundary + error 三類
> - [ ] 每個 test case 帶 inline `[H/M/L]` badge + source
> - [ ] Mocking Strategy 含 do_not_mock 並寫 rationale
> - [ ] Risks 每條格式：失效模式 + Mitigation + Owner
> - [ ] 無 YAML / JSON schema 輸出（plan 是給人讀的 markdown）
```
