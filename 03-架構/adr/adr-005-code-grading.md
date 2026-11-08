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

# ADR-005: 階段 5 寫程式題怎麼批改

**Status:** Proposed · **Owner:** Avi · **Last updated:** 2026-11-08

> [!NOTE]
> 依據：`prd.md` v0.8（FR-1、FR-2 遞減規則、§9 R2）、`non-functional-reqs.md`（S1、S7）、`c4-diagram.md`（§3 程式碼批改環境、§9 R5）、`adr-001-desktop-framework.md`（Option B Cons）、`api-spec.md`（Question `code_fill`）、`data-model.md`（CodeSubmission）。批改方式由 Owner 決定（2026-11-08：5A）。
>
> 這份 ADR 是**單一決策**：寫程式題（程式填空）怎麼判斷對錯。

---

## 1. Context

- 階段 5 加入寫程式題：Python 基礎語法、程式填空，補上缺的一兩行（FR-1；Owner 決定 8A、9B）。
- 一定要自動判斷，不靠人工；可以送很多次，答對時經驗值 10→8→6→4→2 遞減（FR-2，10C、10-2A）。
- 作答資料不離開電腦（NFR S1）；要能擋住無窮迴圈、避免影響玩家電腦（c4-diagram R5；NFR S7）。
- ADR-001 已選 PySide6（Python），可以直接用 Python 執行玩家的程式，不用另外附帶（2026-11-08）。

> **TL;DR:** 寫程式題要自動批改，得決定「用什麼方法判斷對錯」，同時兼顧公平、隱私和安全。

---

## 2. Decision Drivers

| Driver | Weight | Why this matters |
|---|---|---|
| 判斷公平 | High | 寫法不同但正確的答案要算對，不然新手會挫折、經驗值失真 |
| 作答資料不離開電腦 | High | NFR S1；prd §6 Privacy |
| 安全：擋住無窮迴圈、不讓學習精靈當掉 | High | c4-diagram R5；NFR S7 |
| 判斷結果穩定 | High | 同樣的答案每次結果要一樣，經驗值才可信 |
| 沒網路也能批改 | Medium | NFR A1 |
| 好不好做 | Medium | Owner 寫程式還不是很強 |

---

## 3. Options Considered

### Option A: 在玩家電腦上，用獨立程式執行，比對輸出

- **Pros:** 寫法不同但輸出正確就算對；不用網路、資料不離開電腦；結果穩定；獨立程式加時間上限，可以擋住無窮迴圈，學習精靈本身不會當掉
- **Cons:** 要能執行 Python（選 Godot 時要附帶 Python）；每題要多寫「預期輸出」；時間上限只能擋無窮迴圈，擋不住玩家故意寫刪檔指令
- **Cost:** 免費；一次性成本是寫執行和比對的程式

### Option B: 不執行，只比對文字

- **Pros:** 最簡單、最安全，完全不執行玩家的程式
- **Cons:** 多一個空白、換個變數名稱就算錯，對新手不公平
- **Cost:** 免費

### Option C: 送到線上批改服務

- **Pros:** 執行環境和玩家電腦完全隔開，最安全
- **Cons:** 程式碼離開電腦，違反 NFR S1；沒網路不能批改；可能要付費
- **Cost:** 可能按用量付費

### Option D: 用 AI 批改

- **Pros:** 可以順便說明錯在哪
- **Cons:** 同樣的答案每次判斷可能不一樣，經驗值不可信；要網路、要付費；程式碼離開電腦
- **Cost:** AI 用量費用

### Option E: 保持現狀（v1 只有選擇題，不做寫程式題）

- **Pros:** 完全沒有批改的風險和工作量
- **Cons:** 違反 FR-1「選擇題和寫程式題兩種都有」（Owner 決定 3C）
- **Cost:** 免費

---

## 6. Decision & Consequences

### Chosen: **Option A（本機獨立程式執行，比對輸出）** · **[M]**

- **Scope:** 適用於階段 5 的程式填空題。不包含選擇題（直接比對選項），也不包含說明錯在哪（ADR-004 的 AI）。
- **怎麼批改：**
  1. 把玩家填的程式碼放進題目的程式範本。
  2. 用**另一個獨立的 Python 程式**執行，工作資料夾是一個暫存資料夾，不在學習精靈的資料夾裡。
  3. 超過時間上限就強制停止，算答錯，提示「程式跑太久，可能有無窮迴圈」。_TODO: 時間上限幾秒，待 Owner 決定（ADR-001 小試驗或階段 5 實測後）_
  4. 比對輸出和題目的預期輸出（忽略每行最後的空白）；一樣就算對。
- **安全補強（Claude 提議）：** 執行前先檢查程式碼，不允許 `import os`、`subprocess`、`shutil` 這類能動到檔案或系統的模組。題目只考基礎語法，用不到這些。**[L]**
- **題目要多的欄位：** 程式範本（含空格位置）、預期輸出。_TODO: 寫進 `api-spec.md` 的 Question 和 `data-model.md`，階段 5 前凍結_
- **Positive consequences:** 寫法不同但正確就算對；沒網路也能批改；資料不離開電腦；結果穩定；無窮迴圈不會讓學習精靈當掉。
- **Negative consequences（必填）:**
  - ~~選 Godot 時要附帶 Python~~ → ADR-001 選了 PySide6，不需要（2026-11-08）。打包成安裝檔時，要確認執行玩家程式用的是學習精靈自帶的 Python。
  - 每題要多寫程式範本和預期輸出，出題工作變多。
  - 只比對輸出，「印出對的結果但寫法很怪」也會算對。
  - 不是完整的隔離：會用 Python 的玩家還是可能繞過模組檢查，在自己電腦上做壞事；但影響的只有玩家自己的電腦。
- **Follow-up:**
  - ~~ADR-001 選定後確認怎麼執行 Python~~ → PySide6 直接用 Python 的 `subprocess` 執行（2026-11-08）。
  - 階段 5 前：決定時間上限，在 `api-spec.md`、`data-model.md` 加上程式範本和預期輸出欄位。
  - 寫批改的測試：正確答案、寫法不同的正確答案、無窮迴圈、禁止的模組。

---

## 10. Decision Log

| Date | Decision | Options | Chosen | Rejected why | Confidence |
|---|---|---|---|---|---|
| 2026-11-08 | 寫程式題怎麼批改（**Owner 決定** 5A） | A 本機獨立程式執行、比對輸出 / B 只比對文字 / C 線上批改服務 / D AI 批改 / E 不做寫程式題 | A | B：寫法不同就算錯，對新手不公平；C：程式碼離開電腦，違反 Privacy，沒網路不能批改；D：判斷不穩定、要付費、資料離開電腦；E：違反 FR-1（3C） | **[H]** |

---

## 12. Confidence & Sources & TODO

- **整份文件最低 confidence 欄位：** §6 Chosen **[M]**（框架還沒選）；禁止模組的檢查 **[L]**（Claude 提議）。
- **Fabricated assumptions（推測但 input 未明說）：**
  - 程式填空題都會印出結果，可以用「比對輸出」判斷（PRD 只說「補上缺的一兩行」）。
  - 禁止模組清單（`os`、`subprocess`、`shutil`）是 Claude 提議。
  - 「忽略每行最後的空白」是 Claude 提議，避免看不到的差別被判錯。
- **Highest-value next input:** 階段 5 前實測時間上限要設幾秒。

### TODO（缺資料）

- _TODO: 執行時間上限幾秒（Owner 決定）_
- _TODO: 程式範本和預期輸出的格式（api-spec、data-model，階段 5 前凍結）_
- _TODO: 禁止模組清單是否採用、要禁哪些（Owner 確認）_
