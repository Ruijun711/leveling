---
doc_type: "adr"
variant: "light"
status: "proposed"
owner: "Avi"
last_updated: "2026-11-08"
upstream:
  required: ["technical-discussion-notes"]
  optional: ["prd", "c4-diagram", "nfr"]
---

# ADR-006: 階段 3 同學互看等級的雲端服務

**Status:** Proposed · **Owner:** Avi · **Last updated:** 2026-11-08

> [!NOTE]
> 依據：`api-spec.md`（E3、E4、3C）、`data-model.md`（CloudPlayerProgress、2B）、`c4-diagram.md`（§9 R3、R6）、`non-functional-reqs.md`（S3、S4、S6）、`roadmap.md`（階段 3+、4B）、`prd.md`（§10 3B）、`adr-003-cloud-data-service.md`（1B：階段 3 另寫）、`adr-004-ai-service.md`（雲端函式）。服務類型、身分確認、防竄改由 Owner 決定（2026-11-08：3A、4A）。
>
> 這份 ADR 是**單一決策**：階段 3 上傳和讀取經驗值（api-spec E3、E4）用哪一類雲端服務、怎麼確認是本人。防竄改的檢查是這個決定的直接後果，寫在 §6。階段 1 題庫仍放 GitHub（ADR-003），不搬家。

---

## 1. Context

- 階段 3 之後，同學可以互看彼此的暱稱、經驗值、等級；只有這 3 項離開玩家電腦（api-spec E3、E4；NFR S4）。
- 用現成雲端服務，不自己寫伺服器（Owner 決定 3B）。
- 身分確認（api-spec 3C）和防竄改（c4-diagram R6）留到這份 ADR：要讓「每個人只能改自己的資料」，否則拿到網址的人就能改任何人的等級。
- 階段 4 的 AI 雲端代理也需要雲端函式和身分確認（ADR-004），最好用同一家。

> **TL;DR:** 階段 3 要讓同學互看等級，得先選一個能存資料、確認本人、也能放 AI 代理的雲端服務。

---

## 2. Decision Drivers

| Driver | Weight | Why this matters |
|---|---|---|
| 每個人只能改自己的資料 | High | c4-diagram R6；否則等級失去可信度 |
| 同學用起來簡單 | High | 新手；多一個登入步驟就可能不用 |
| 只公開 3 個欄位 | High | NFR S4；prd §6 Privacy |
| 能放 AI 代理（雲端函式） | Medium | ADR-004 |
| 好不好學 | Medium | Owner 寫程式還不是很強（prd §9 R2） |
| 費用 | Medium | 個人專案；_TODO: 階段 3 是否也只用免費方案，待 Owner 確認（ADR-003 的 3A 只講階段 1）_ |

---

## 3. Options Considered

### Option A: Firebase 或 Supabase 這類服務＋匿名登入

- **Pros:** 匿名登入：每台電腦第一次連線時自動拿到一個代號，不用帳號密碼；可以設定「每個人只能改自己那一筆」；有雲端函式，可以放 AI 代理（ADR-004）；網路上教學很多
- **Cons:** 要學一個新服務和它的權限規則，規則寫錯可能讓資料外洩；匿名代號存在本機，重灌或換電腦就變成新玩家；綁定一家服務
- **Cost:** 有免費方案；部分功能（例如 Firebase 的雲端函式）可能要綁付費方案。_TODO: 試驗時確認_

### Option B: Google Apps Script 網頁程式＋試算表

- **Pros:** Owner 已經會寫 Apps Script（create-form.gs、create-stage0-form.gs）；免費；資料直接在試算表裡看得到
- **Cons:** 沒有每個人自己的身分，拿到網址的人就能改任何人的資料（R6）；同時很多人上傳時容易互相蓋掉；速度比較慢
- **Cost:** 免費

### Option C: 用 Google 帳號登入

- **Pros:** 身分最確定，換電腦也能找回同一個玩家
- **Cons:** 同學多一個登入步驟；Owner 要多做登入功能；會拿到同學的 Email（個資變多，和「不收真名」方向相反）
- **Cost:** 免費，但開發工作量大

### Option D: 保持現狀（v1 不做同學互看）

- **Pros:** 完全不用雲端資料庫和登入
- **Cons:** 違反 Owner 決定 4B（v1 要能互看）
- **Cost:** 免費

---

## 6. Decision & Consequences

### Chosen: **Option A（Firebase 或 Supabase 類服務＋匿名登入）** · **[M]**

- **Scope:** 適用於階段 3+ 的 E3、E4，以及階段 4 的 AI 雲端代理（ADR-004）。不適用於階段 1 題庫（仍是 GitHub，ADR-003）。
- **選哪一家：** 階段 3 前做小試驗，Firebase、Supabase 各試一次，判斷標準：
  | # | 要試的事 | 判斷標準 |
  |---|---|---|
  | 1 | 匿名登入 | 學習精靈第一次連線自動拿到代號，重開後還是同一個 |
  | 2 | 只能改自己的資料 | 用 A 的代號改 B 的資料會被拒絕 |
  | 3 | 只公開 3 欄 | 讀全班資料時只拿得到暱稱、經驗值、等級、更新時間（NFR S4） |
  | 4 | 雲端函式 | 能放 AI 代理，而且確認得到呼叫者的匿名代號（ADR-004） |
  | 5 | 費用 | 以上都能用免費方案或在費用上限內 |
- **身分確認（取代 api-spec 3C 的 TODO）：** `player_id` 就是匿名登入的代號；雲端規則設定「只能寫入自己代號的那一筆」。
- **防竄改（Owner 決定 4A）：** 雲端只做基本檢查，不合格就拒絕（`PROGRESS_INVALID`）：
  - 經驗值只能增加，不能變少
  - 等級要等於 `min(9, 1 + INT(經驗值 / 20))`
  - 經驗值不能超過「題庫題數 × 10」
  - 接受風險：會改本機資料的同學還是能在合理範圍內作弊。
- **Positive consequences:** 每個人只能改自己的資料；同學不用帳號密碼；AI 代理和經驗值用同一家；明顯不合理的數字會被擋下。
- **Negative consequences（必填）:**
  - 要學新服務和權限規則；規則寫錯可能讓別人看到不該看的資料，試用前要照 §6 試驗第 2、3 項再檢查一次。
  - 重灌或換電腦就變成新玩家，舊的雲端紀錄留著沒人更新（和 ADR-002「不備份」一致）。
  - 基本檢查擋不住「在合理範圍內」的作弊。
  - 綁定一家服務，之後要換要改程式。
  - 經驗值上限要知道題庫題數，雲端要讀得到題庫版本（從 GitHub 或手動設定）。_TODO: 開發時決定_
- **Follow-up:**
  - 階段 3 前做小試驗，選定後改成 Accepted。
  - 把 E3、E4 對應到實際做法，寫進 `api-spec.md`。
  - 決定換電腦後的舊紀錄怎麼處理（data-model CloudPlayerProgress `deleted_at` TODO）。

---

## 10. Decision Log

| Date | Decision | Options | Chosen | Rejected why | Confidence |
|---|---|---|---|---|---|
| 2026-11-08 | 服務類型和身分確認（**Owner 決定** 3A） | A Firebase／Supabase＋匿名登入 / B Apps Script＋試算表＋班級代碼 / C Google 帳號登入 / D v1 不做互看 | A | B：拿到網址就能改任何人的資料（R6）；C：多一個登入步驟、拿到 Email、開發量大；D：違反 4B | **[H]** |
| 2026-11-08 | 防竄改（**Owner 決定** 4A） | A 基本檢查 / B 上傳作答紀錄、雲端重算 / C 不檢查 | A | B：作答紀錄離開電腦，違反 Privacy（NFR S1）；C：明顯不合理的數字也不會被發現 | **[H]** |

---

## 12. Confidence & Sources & TODO

- **整份文件最低 confidence 欄位：** §6 Chosen **[M]**（兩家都還沒試）。
- **Fabricated assumptions（推測但 input 未明說）：**
  - Firebase、Supabase 都有匿名登入、權限規則、雲端函式；Firebase 的雲端函式可能要綁付費方案——是 Claude 依一般資料判斷，試驗時確認。
  - Apps Script 網頁程式沒有每個人的身分、同時上傳容易互相蓋掉，是 Claude 依一般經驗判斷。
  - 一個班大約 35 人，資料量很小（api-spec §12）。
- **Highest-value next input:** 階段 3 前的 Firebase／Supabase 小試驗結果。

### TODO（缺資料）

- _TODO: 階段 3 是否也只用免費方案（Owner 確認）_
- _TODO: 小試驗結果，選定一家後改成 Accepted_
- _TODO: 雲端怎麼知道題庫題數（經驗值上限檢查）_
- _TODO: 換電腦或重灌後，舊的雲端紀錄怎麼處理_
