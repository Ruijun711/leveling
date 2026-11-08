---
doc_type: "code-review-checklist"
variant: "light"
status: "draft"
owner: "Avi"
last_updated: "2026-11-08"
upstream:
  required: ["git-diff", "coding-standard"]
  optional: ["existing-checklist"]
---

# Code Review Checklist: create-stage0-form.gs（階段 0 表單腳本）

**Status:** Draft v0.1 · **Owner:** Avi（Claude first-pass） · **Last updated:** 2026-11-08

> [!NOTE]
> **範圍（Owner 決定 2026-11-08，1A）：** 只 review `create-stage0-form.gs` 全檔 369 行（git `64adcf7` 建立、`4fffd84` 修改；沒有 PR，視為「從空白到現在」的整份改動）。`create-form.gs`、`create-practice-form.gs` 已執行完畢，不在範圍內。
>
> **標準（2A）：** 專案沒有 coding standard，改用專案文件當標準：`roadmap.md` §3「階段 0 細節」（經驗值、等級、只算第一次作答、G1 週別與分母、反指標）、`practice-questions-stage0.md`（12 題答案）、progress 11-05（只公開「經驗值」工作表）、`data-model.md` 2B（暱稱不能用真名），以及 Google Apps Script／試算表函式的行為。
>
> **方法（3A）：** Claude 讀程式碼＋用 node 做語法和資料檢查；**沒有在 Google 上執行**。所以另附「試跑步驟」（F-007），請 Avi 發給同學前做一次。
>
> **修改（4A）：** 這份只列問題，不改 `.gs`；要修哪一條，Claude 再逐項問 Avi。

---

## 1. Executive Summary

- 共 **7 條 finding**：**must_block 1 條**、should_fix 6 條（輕量版不列 nit）。
- **最危險：** F-001 —— 5 題靠縮排判斷答案（B1、C1、B2、C2、C3），如果 Google 表單把題目說明開頭的空白吃掉，題目就變了，答案可能變錯。這要在表單預覽裡看一眼才確定。
- 其次是 F-002、F-006：暱稱大小寫、第 1 次出題日的格式，都可能讓 G1 算錯，也就是讓階段 0 的結論不可信。
- 已通過的自動檢查：語法正確；12 題的答案都在選項裡、每題剛好 4 個不重複選項、題號不重複、每次 3 題；12 題答案和 `practice-questions-stage0.md` 完全一致。

> **TL;DR:** 程式邏輯大致正確，但**確認 F-001（縮排）之前不要發給同學**；其餘 6 條建議在試跑時一起確認或修掉。

---

## 2. Dimension Coverage

| Dimension | Status | Finding count | Confidence |
|---|---|---|---|
| Correctness | covered | 6（F-001～F-006） | **[M]** |
| Readability | covered | 0（已檢視：分段清楚、常數集中、錯誤訊息是中文且告訴 Avi 下一步） | **[H]** |
| Perf | covered | 0（已檢視：約 30 列 × 12 題的公式，資料量是幾十份回覆，不會慢） | **[M]** |
| Security | covered | 0（已檢視：不收 Email、試算表預設不分享；「只公開經驗值工作表」靠手動設定，列在 §9 R1） | **[M]** |
| Test | covered | 1（F-007） | **[H]** |
| Observability | covered | 0（已檢視：Logger 印出所有連結和下一步；每個錯誤都有說明） | **[H]** |
| A11y | covered | 0（已檢視：表單畫面由 Google 提供，腳本無法調整；縮排顯示的問題歸在 F-001） | **[M]** |

---

## 5. Findings

### F-001 · Severity **must_block** · **[L]**

- **File:line:** `create-stage0-form.gs:231`（題目資料：B1 第 42 行、C1 第 49 行、B2 第 73 行、C2 第 83 行、C3 第 114 行）
- **Dimension:** correctness
- **Evidence:** 程式碼放在 `setHelpText(p.code + ...)`。Python 用縮排決定哪幾行屬於 `if`／`for`，C3 的答案「只印出 C」完全靠縮排。Google 表單的說明文字會不會保留每行開頭的空白，**Claude 無法在這裡確認**。
- **Suggested fix:** 執行 `releaseBatch1()` 前，先在表單「預覽」看 B1、C1 有沒有縮排。如果縮排不見，把開頭的空白換成不會被吃掉的空白：`p.code.replace(/^ +/gm, function (s) { return ' '.repeat(s.length); })`（修改前再問 Avi）。
- **Source:** diff `create-stage0-form.gs:231`；standard `practice-questions-stage0.md` C3 解說「有縮排的兩行都在 if 裡面」

### F-002 · Severity **should_fix** · **[M]**

- **File:line:** `create-stage0-form.gs:296`、`:302`
- **Dimension:** correctness
- **Evidence:** 暱稱比對用 `=`（試算表的 `=` 不分大小寫），但暱稱清單用 `UNIQUE`（分大小寫）。同學一次填 `Avi`、一次填 `avi`，清單會出現 2 列，而且**每一列都把兩次的交卷算進去**：經驗值重複出現，「兩週都有交卷」也會多算一人，G1 偏高。
- **Suggested fix:** 把第 296 行改成 `'LOWER(TRIM(' + nickRaw + '))'`，第 302 行的 `UNIQUE` 也用同一個 `nick`，讓大小寫不同的暱稱合併成同一人。
- **Source:** diff `create-stage0-form.gs:296,302`；standard `roadmap.md` §3 G1 算法。`UNIQUE` 分大小寫、`=` 不分，是 Claude 依一般資料判斷，試跑步驟 6 會確認。

### F-003 · Severity **should_fix** · **[H]**

- **File:line:** `create-stage0-form.gs:24`（使用處 `:313`、`:344`）
- **Dimension:** correctness
- **Evidence:** `XP_ROWS = 30`，公式只寫到第 31 列。暱稱清單由 `UNIQUE` 往下長，沒有上限；超過 30 個不同暱稱時（例如打錯字、測試用暱稱），第 32 列以後的人看得到暱稱但沒有經驗值，「統計」也不會算到他們，G1 偏低。
- **Suggested fix:** 把 `XP_ROWS` 改成 60；或在 `buildSheets_` 最後檢查暱稱數量，超過 `XP_ROWS` 時用 Logger 提醒 Avi。
- **Source:** diff `create-stage0-form.gs:24,313,344`；standard `roadmap.md` §3（受測 ≥ 8 人，班上 35 人）

### F-004 · Severity **should_fix** · **[M]**

- **File:line:** `create-stage0-form.gs:209-218`
- **Dimension:** correctness
- **Evidence:** 先加題目、最後才把 `RELEASED` 加 1。如果加到第 2 題時出錯（例如 Google 暫時連不上），`RELEASED` 沒變，Avi 重新執行同一個 `releaseBatchN()` 會**再加一次已經加過的題目**，表單出現重複的題目；`header.indexOf` 只會找到第一個同名欄位，第二個欄位的作答不會被算到。
- **Suggested fix:** `addProblem_` 開頭先檢查表單裡有沒有同標題的題目，有就跳過。
- **Source:** diff `create-stage0-form.gs:209-218`、`:286`

### F-005 · Severity **should_fix** · **[L]**

- **File:line:** `create-stage0-form.gs:216`
- **Dimension:** correctness
- **Evidence:** 第 1 次出題日用「腳本專案的時區」（`Session.getScriptTimeZone()`），交卷時間用「試算表的時區」。兩邊不一樣時（新的 Apps Script 專案時區不一定是台北），第 1 週、第 2 週的分界會差幾個小時，剛好在週界交卷的人會被算到錯的一週。
- **Suggested fix:** 改用試算表的時區 `ss.getSpreadsheetTimeZone()`（要把開啟試算表移到這行前面）；或試跑時確認「專案設定」和「試算表設定」的時區都是 `(GMT+08:00) Taipei`。
- **Source:** diff `create-stage0-form.gs:216`、`:348-349`；standard `roadmap.md` §3「第 1～7 天是第 1 週」

### F-006 · Severity **should_fix** · **[M]**

- **File:line:** `create-stage0-form.gs:362`
- **Dimension:** correctness
- **Evidence:** H1 寫入的是文字 `'2026-11-09'` 這種格式，要靠試算表自動轉成日期。如果沒有轉成日期，第 348-349 行「交卷時間 ≥ H1」的比較會全部不成立，每個人的交卷次數都是 0，**G1 會變成 0%**。
- **Suggested fix:** 第 362 行改成 `setFormula('=DATEVALUE("' + 日期 + '")')`，或寫入 `Date` 物件；試跑時確認 H1 是日期（儲存格靠右對齊）。
- **Source:** diff `create-stage0-form.gs:216,362,348-349`；standard `roadmap.md` §3 G1 算法

### F-007 · Severity **should_fix** · **[H]**

- **File:line:** `create-stage0-form.gs`（全檔）
- **Dimension:** test
- **Evidence:** 腳本從來沒有在 Google 上執行過，也沒有任何測試；F-001、F-002、F-005、F-006 都要實際執行才能確認。
- **Suggested fix:** 發給同學前，用**另一個 Google Apps Script 專案**照下面的步驟試跑一次（不會影響正式表單），結果記在這份文件 §12：
  1. 確認「專案設定 → 時區」是台北（F-005）。
  2. 執行 `createStage0Form()`、`releaseBatch1()`。
  3. 在表單「預覽」看 B1、C1 的程式碼有沒有縮排（**F-001**）。
  4. 確認「設定 → 測驗」：每次提交後立即公布成績、看得到答錯的題目和正確答案。
  5. 用暱稱 `測試甲` 交卷：A1 選 34（對）、B1 選 1 2 3（錯）、C1 留空。「經驗值」應該是：已作答 2、答對 1、經驗值 10、等級 1、距離下一級 10。
  6. 用暱稱 `TestB` 交一次、`testb` 再交一次：「經驗值」只應該有 1 列 TestB（F-002）。
  7. 用 `測試甲` 再交一次、A1 改選 7：答對題數仍是 1（只算第一次作答）。
  8. 看「統計」：H1 是日期且靠右對齊（F-006）；第 1 週交卷次數 `測試甲` 是 2；在 H2 填 2，H4 會算出比例。
  9. 執行 `releaseBatch2()`：表單變成 6 題，「選填」題仍在最後；再執行一次 `releaseBatch2()` 應該出現錯誤訊息，不會加題。
  10. 試跑完把測試表單和試算表刪掉，正式用的專案再執行 `createStage0Form()`。
- **Source:** standard `roadmap.md` §3；progress「待 Avi 處理」第 1 項（確認立即公布成績）

---

## 9. Risks（top 3）

> **R1（隱私）：發布到網路時選錯範圍** — 「發布到網路」如果選了整份試算表而不是只選「經驗值」工作表，同學會看到回應工作表裡每個人「學程式多久」「卡在哪裡」的回答（違反 progress 11-05 的決定）。 — **Mitigation:** 發布時只選「經驗值」工作表；發布後用無痕視窗打開連結，確認只看得到經驗值。 — **Owner:** Avi
>
> **R2（G1 失真）：空白交卷、兩人同暱稱** — 所有題目都是選填，只填暱稱就交卷也算「交卷 1 次」，G1 可能偏高；兩個人用同一個暱稱會被合併成一人。腳本照 roadmap 的定義算「交卷」，但這兩種情況 roadmap 沒有說要不要排除。 — **Mitigation:** _TODO: 由 Owner 決定空白交卷算不算；第 1 週結束時看一次「統計」的暱稱清單，發現可疑的暱稱私下確認_ — **Owner:** Avi
>
> **R3（操作時機）：出題日跑錯天或忘了跑** — 第 1 次出題日（H1）是執行 `releaseBatch1()` 的那天；提早一天執行，兩週的分界就整個往前移；忘記執行某一次，同學就少了新題目。 — **Mitigation:** 4 次都在行事曆設提醒，當天早上執行；`releaseBatch1()` 執行完確認 H1 是第 1 週週一。 — **Owner:** Avi

---

## 12. Confidence & Sources & TODO

- **整份 checklist 最低 confidence 項：**
  - **[L]**：F-001（不知道表單會不會吃掉開頭空白）、F-005（不知道兩邊時區是否不同）。
  - **[M]**：F-002、F-004、F-006；Dimension 的 Correctness、Perf、Security、A11y。
- **Fabricated assumptions（推測但 input 未明說）：**
  - 試算表的 `UNIQUE` 分大小寫、`=` 不分大小寫，是 Claude 依一般資料判斷（試跑步驟 6 確認）。
  - 新的 Apps Script 專案時區可能不是台北，是 Claude 依一般經驗判斷（試跑步驟 1 確認）。
  - 回應工作表的第 1 欄是交卷時間（`tsCol` 寫死 A 欄），依 Google 表單的固定格式。
  - 「只算第一次作答」取回應工作表裡最上面一筆，假設回覆依交卷時間由上往下排（Google 表單的預設行為）。
- **Highest-value next input:** 試跑步驟（F-007）的結果，特別是第 3 步（縮排）和第 6、8 步。

### TODO（缺資料）

- _TODO: 試跑結果（F-007），確認或排除 F-001、F-002、F-005、F-006_
- _TODO: 空白交卷算不算「交卷」（R2），待 Owner 決定_
- _TODO: 要修哪幾條 finding，待 Owner 逐項決定（4A）_
