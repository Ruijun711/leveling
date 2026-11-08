---
name: adr-quick
description: "把「為什麼這樣選」寫下來，半年後不用考古"
metadata:
  type: work-package
  variant: quick
  source: launch-atlas
  stage: "design"
  roles: ["architect"]
  deliverable_slug: "adr"
  context_strategy: repository-first
---

# ADR · 架構決策紀錄 · Quick (≤ 12 行) · 工作包

**何時用：** 跨服務影響、不可逆決策、有 ≥ 2 個合理選項時

**AI 加速：** 用 Claude 從技術討論紀錄 → ADR 草稿（option / trade-off / consequence）

## Agent 協作規則

1. 這份工作包定義輸出品質，不代表上游文件必須依序存在。
2. 先搜尋 Repository、既有文件、設定與測試；找到等價證據即可使用，並標示來源路徑。
3. 人類負責需求、限制、驗收標準與衝突決策。不得替人類猜測決策。
4. 先回報 FOUND、MISSING、CONFLICT。只有缺口會改變輸出時才提問，每次最多 5 題。
5. 資訊不足但不阻擋草稿時保留 TODO，並註明需要什麼證據，不得編造。

## 輸出範本

```
---
doc_type: "adr"
variant: "light"
status: "proposed"
owner: "<your-name>"
last_updated: "YYYY-MM-DD"
upstream:
  required: ["technical-discussion-notes"]
  optional: ["prd", "c4-diagram", "nfr"]
---

# ADR-NNN: <短描述決策題目>

**Status:** Proposed · **Owner:** <Architect name> · **Last updated:** YYYY-MM-DD

> [!IMPORTANT]
> **AI 填寫規則：** 本範本 6 段（編號 1, 2, 3, 6, 10, 12），全部必填——刻意沿用完整版的章節編號讓兩版可對照。每結論行內加 `（依據：discussion §XXX）`；每量化欄位加 `[H]/[M]/[L]` confidence badge；缺資料寫 `_TODO: 需要 XXX_` 不編造選項；ADR 是**單一決策原子文件**，若 input 含多個決策必須拆多份輸出。

---

## 1. Context

<!-- ai-fill: 3-5 行說明當前問題、約束、為何現在需要決策 -->

<3-5 行說明當前面對的問題與約束>

> **TL;DR:** <一句話：為何需要這個決策>

---

## 2. Decision Drivers

<!-- ai-rule: 至少列 3 個 driver，每個帶權重原因。輕量版可省略 5 象限要求 -->

| Driver | Weight | Why this matters |
|---|---|---|
| <e.g. Time-to-market> | High | <為何此優先> |
| <e.g. Operability> | Medium | ... |

---

## 3. Options Considered

<!-- ai-rule: ≥ 2 個選項（含「保持現狀」或「不做」），每個都要 pros/cons 至少各 1 -->

### Option A: <name>

- **Pros:** <好處 1>、<好處 2>
- **Cons:** <代價 1>、<代價 2>
- **Cost:** <一次性 + 經常性>

### Option B: <name>

...

---

## 6. Decision & Consequences

### Chosen: **Option A** · **[H]**

- **Scope:** <適用範圍 / 不適用範圍>
- **Positive consequences:** <好處>
- **Negative consequences（必填）:** <代價，例：選 Kafka 需新增 KRaft 維運負擔>
- **Follow-up:** <後續需處理事項>

---

## 10. Decision Log

<!-- ai-rule: 每條必含 chosen + 至少 1 個 rejected option + 拒絕原因 -->

| Date | Decision | Options | Chosen | Rejected why | Confidence |
|---|---|---|---|---|---|
| YYYY-MM-DD | <本 ADR 主題> | A / B | A | B (成本 > 收益) | **[H]** |

---

## 12. Confidence & Sources & TODO

- **整份文件最低 confidence 欄位：** <列出所有 [L] 與 [M]>
- **Fabricated assumptions（推測但 input 未明說）：**
  - <假設 1>
- **Highest-value next input:** <下一份最該補的資料：benchmark / spike / interview>

### TODO（缺資料）

- _TODO: 需要 spike 驗證 Option A 在 X scale 下的可用性_

---

> [!CAUTION]
> **輸出前 AI 自檢：**
> - [ ] 6 段 H2 章節齊全（編號 1, 2, 3, 6, 10, 12，刻意不連號）
> - [ ] Options ≥ 2 個，每個含 pros + cons
> - [ ] Decision 段含 negative consequences（必填）
> - [ ] 每個 chosen 帶 inline `[H/M/L]` badge
> - [ ] Decision Log ≥ 1 條，每條有 rejected reason
> - [ ] 單一決策原子文件（input 含多決策應拆多份）
> - [ ] 無 YAML / JSON schema 輸出（ADR 是給人讀的 markdown）
```
