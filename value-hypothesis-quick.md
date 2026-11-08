---
name: value-hypothesis-quick
description: "把「我覺得有用」翻成可驗證的假設"
metadata:
  type: work-package
  variant: quick
  source: launch-atlas
  stage: "discovery"
  roles: ["po", "pm"]
  deliverable_slug: "value-hypothesis"
  context_strategy: repository-first
---

# 價值假設卡 · Quick (≤ 12 行) · 工作包

**何時用：** 新功能進 backlog 前、需要決定是否投入 sprint 資源時

**AI 加速：** 用 Claude 把模糊想法 → 可驗證假設 + 驗證實驗

## Agent 協作規則

1. 這份工作包定義輸出品質，不代表上游文件必須依序存在。
2. 先搜尋 Repository、既有文件、設定與測試；找到等價證據即可使用，並標示來源路徑。
3. 人類負責需求、限制、驗收標準與衝突決策。不得替人類猜測決策。
4. 先回報 FOUND、MISSING、CONFLICT。只有缺口會改變輸出時才提問，每次最多 5 題。
5. 資訊不足但不阻擋草稿時保留 TODO，並註明需要什麼證據，不得編造。

## 輸出範本

```
---
doc_type: "value-hypothesis"
variant: "light"
status: "draft"
owner: "<your-name>"
last_updated: "YYYY-MM-DD"
upstream:
  required: ["persona", "jtbd"]
  optional: ["journey-map", "north-star"]
---

# Value Hypothesis: <feature-or-idea-name>

**Status:** Draft v0.X · **Owner:** <PO name> · **Last updated:** YYYY-MM-DD

> [!IMPORTANT]
> **AI 填寫規則：** 本範本 6 段（編號 1, 2, 4, 5, 10, 12），全部必填——刻意沿用完整版章節編號讓兩版可對照。每結論行內加 `（依據：persona §XXX / JTBD-NNN / metric §YYY）`；每量化欄位 `[H]/[M]/[L]` confidence badge；缺資料寫 `_TODO: 需要 XXX_` 不編造；hypothesis **必須可證偽**、kill criteria **必須可被觸發**（不能寫「不管結果都繼續」）。

---

## 1. Executive Summary

<!-- ai-fill: 3-5 行：要驗證什麼 idea、給哪個 segment、預期 leading indicator -->

<3-5 行說明>

> **TL;DR:** <一句話：我們相信 X 對 Y 有價值，因為 Z，用 M 指標驗證>

---

## 2. Customer Segment & Problem

<!-- ai-rule: segment 必須對應 persona id；problem 用「<segment> struggles to <job> because <pain>」格式 -->

| Field | Value | Confidence | Source |
|---|---|---|---|
| **Customer segment** | <persona id + 描述> | **[H]** | persona §P1 |
| **Problem statement** | <segment> struggles to <job> because <pain> | **[H]** | JTBD-001 + interview §3 |
| **Proposed value** | 我們相信 <行為改變> 對 <使用者> 有價值，因為 <理由> | **[M]** | persona §pain + journey §S3 |

---

## 4. Riskiest Assumption

<!-- ai-rule: 只列 1 條最 riskiest（錯了整個 idea 死），category 必須是 desirability / viability / feasibility 之一 -->

> **A1 (riskiest):** <一句話描述>
>
> - **Category:** desirability / viability / feasibility
> - **Why risky:** <若錯了 idea 就死的具體原因>
> - **Confidence:** **[L]** — _尚未有 user evidence_

---

## 5. Test Method & Success Threshold

<!-- ai-rule: test_method 必須 < 1 週且優先選 no-code / mock；threshold 必須含 baseline + target 兩值 -->

| Field | Value | Confidence | Source |
|---|---|---|---|
| **Method** | <fake_door / concierge / wizard_of_oz / prototype_test / smoke_test / painted_door> | **[H]** | _自選_ |
| **Cost** | ≤ X days · no-code: yes/no · participants: N | — | — |
| **Metric** | <e.g., click-through rate on fake door> | **[H]** | metric §baseline |
| **Baseline** | <current value> | **[M]** | analytics §XX |
| **Target** | <value that confirms hypothesis> | **[M]** | _推導自 persona §pain_ |

### Kill criteria（必須可被觸發）

- [NO] 若 < X% 受測者觸發 leading indicator，**放棄此題目**
- [NO] 若 cost-to-acquire > 3× LTV proxy，**放棄**

---

## 10. Decision Log（key 1-2 條）

<!-- ai-rule: 每條必含 chosen + 至少 1 個 rejected option + 拒絕原因 -->

| Date | Decision | Options | Chosen | Rejected why | Confidence |
|---|---|---|---|---|---|
| YYYY-MM-DD | test_method 選擇 | fake_door / concierge / prototype | fake_door | concierge (成本 > 1 週)、prototype (太重) | **[H]** |

---

## 12. Confidence & Sources & TODO

- **整份文件最低 confidence 欄位：** <列出所有 [L] 與 [M]>
- **Fabricated assumptions（推測但 input 未明說）：**
  - <假設 1>
- **Highest-value next input:** <下一份最該補的訪談 / analytics baseline / 競品 benchmark>

### TODO（缺資料）

- _TODO: 需要 XXX 校準 baseline_

---

> [!CAUTION]
> **輸出前 AI 自檢：**
> - [ ] 6 段 H2 章節齊全（編號 1, 2, 4, 5, 10, 12，刻意沿用完整版編號）
> - [ ] Riskiest assumption 只有 1 條，且 category 為 desirability / viability / feasibility
> - [ ] Test method cost ≤ 1 週（超過必須在 Decision Log 解釋）
> - [ ] Kill criteria 至少 1 條，且為「可被觸發」的硬門檻（非「再評估」這種模糊話）
> - [ ] Success threshold 含 baseline + target 兩值（單有 target 不算）
> - [ ] 每個量化欄位帶 `[H/M/L]` badge + 行內 `（依據：...）`
> - [ ] 無 YAML / JSON schema 輸出（價值假設卡是給人讀的 markdown）
```
