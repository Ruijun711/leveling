---
name: non-functional-reqs-quick
description: "把『要很快、要很穩』改寫成可驗收的數字"
metadata:
  type: work-package
  variant: quick
  source: launch-atlas
  stage: "design"
  roles: ["architect", "sa"]
  deliverable_slug: "non-functional-reqs"
  context_strategy: repository-first
---

# 非功能需求 · NFR · Quick (≤ 12 行) · 工作包

**何時用：** 功能規格已寫，但延遲、容量、可用性、安全還只是形容詞

**AI 加速：** 用 Claude 把 PRD 形容詞轉成 SLI/SLO/threshold 候選

## Agent 協作規則

1. 這份工作包定義輸出品質，不代表上游文件必須依序存在。
2. 先搜尋 Repository、既有文件、設定與測試；找到等價證據即可使用，並標示來源路徑。
3. 人類負責需求、限制、驗收標準與衝突決策。不得替人類猜測決策。
4. 先回報 FOUND、MISSING、CONFLICT。只有缺口會改變輸出時才提問，每次最多 5 題。
5. 資訊不足但不阻擋草稿時保留 TODO，並註明需要什麼證據，不得編造。

## 輸出範本

```
---
doc_type: "non-functional-reqs"
variant: "light"
status: "draft"
owner: "<your-name>"
last_updated: "YYYY-MM-DD"
upstream:
  required: ["prd"]
  optional: ["platform-baseline", "competitive-baseline"]
---

# Non-Functional Requirements: <system-name>

**Status:** Draft · **Owner:** <Architect/SA> · **Last updated:** YYYY-MM-DD

> [!IMPORTANT]
> **AI 填寫規則：** 本範本 5 段（編號 1, 2, 4, 10, 12），全部必填——刻意沿用完整版的章節編號讓兩版可對照。每條 NFR 行內加 `（依據：prd §XXX）`；每量化欄位帶 `[H]/[M]/[L]` confidence badge；缺資料寫 `_TODO: 需要 XXX_` **不抄業界數字**（例：別寫「99.99% 因為大家都這樣寫」）；每條 NFR 必含可量測 SLI + 目標 SLO + 量測方法（缺一不可）。

---

## 1. Executive Summary

<!-- ai-fill: 3-5 行說明範圍、SLA 對外承諾與否、目前最不確定的閾值 -->

<3-5 行說明>

> **TL;DR:** <一句話：哪幾個維度是 hard target、哪幾個是 best-effort>

---

## 2. Core NFR Matrix

<!-- ai-rule: 至少 4 象限（latency / availability / security / a11y）。每條含 SLI + SLO + 量測方法 -->

| Dimension | SLI | SLO target | Measurement | Confidence |
|---|---|---|---|---|
| **Latency** | API p95 | < Xms | <e.g. RUM + synthetic> | **[H]** |
| **Availability** | uptime | 99.X% rolling 28-day | <SLI 定義> | **[M]** |
| **Security** | data class | PII encrypted at-rest | <稽核方式> | **[H]** |
| **A11y** | WCAG 2.2 AA | <scope> | <e.g. axe-core CI> | **[H]** |

---

## 4. Compliance（核心）

<!-- ai-rule: 列出本系統涉及的合規條目，N/A 必須說明為何不適用 -->

| Regime | Applicable | Notes |
|---|---|---|
| GDPR | [YES] / [NO] | <若 [YES]：列關鍵條款 + 對應控制> |
| SOC 2 | [YES] / [NO] | <若 [NO]：不對外提供 SaaS> |
| PCI DSS | [YES] / [NO] | <若 [NO]：不處理卡號> |

---

## 10. Decision Log

<!-- ai-rule: 每條必含 chosen + 至少 1 個 rejected option + 拒絕原因 -->

| Date | Decision | Options | Chosen | Rejected why | Confidence |
|---|---|---|---|---|---|
| YYYY-MM-DD | Availability SLO | 99.9% / 99.95% / 99.99% | 99.9% | 99.95% (cost +50%)、99.99% (需 multi-region) | **[H]** |

---

## 12. Confidence & Sources & TODO

- **整份文件最低 confidence 欄位：** <列出所有 [L] 與 [M]>
- **Fabricated assumptions（推測但 input 未明說）：**
  - <假設 1：例：假設無 HIPAA 負擔>
- **Highest-value next input:** <下一份最該補的：實際 traffic profile / 競品 baseline>

### TODO（缺資料）

- _TODO: 需要實際 traffic profile 校準 latency p99 threshold_

---

> [!CAUTION]
> **輸出前 AI 自檢：**
> - [ ] 5 段 H2 章節齊全（編號 1, 2, 4, 10, 12，刻意不連號）
> - [ ] Core NFR Matrix 至少 4 象限（latency / availability / security / a11y）
> - [ ] 每條 NFR 含 SLI + SLO + Measurement
> - [ ] 沒有任何 threshold 抄業界數字（每筆都有 source 或 _TODO_）
> - [ ] Compliance 不適用項有說明為何不適用
> - [ ] Decision Log ≥ 1 條，每條有 rejected reason
> - [ ] 無 YAML / JSON schema 輸出（NFR 是給人讀的 markdown）
```
