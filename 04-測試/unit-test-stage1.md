---
doc_type: "unit-test"
variant: "light"
status: "draft"
owner: "Avi"
last_updated: "2026-11-08"
upstream:
  required: ["function-signature", "spec"]
  optional: ["existing-coverage"]
---

# Unit Test Plan: 學習精靈 · 階段 1 核心規則

**Status:** Draft v0.1 · **Owner:** Avi（Claude 起草） · **Last updated:** 2026-11-08

> [!NOTE]
> **範圍（Owner 決定 2026-11-08，1A）：** 階段 1 的核心規則：經驗值、等級、只算第一次作答、提醒時間、題庫檢查。階段 1 的程式**還沒寫**，所以這是「先寫測試、再寫程式」的計畫；§2 的函式名稱和參數是 **Claude 提議**，寫程式時可以改名，但規則不變。階段 5 的寫程式題遞減經驗值不在範圍內。
>
> **不綁定語言（2A）：** 每條只寫「輸入 → 預期結果」。ADR-001 選定後再寫成程式：PySide6 用 pytest，Godot 用 GUT。
>
> **只寫計畫（4A）：** 不產出可執行的測試程式。
>
> 依據：`prd.md` FR-1、FR-2、FR-6；`acceptance-criteria.md` AC-1～AC-13；`api-spec.md` §3；`data-model.md` §2；`non-functional-reqs.md` A3；ADR-002。**現有測試覆蓋率：0**（專案沒有任何測試）。

---

## 1. Executive Summary

- **7 個 target**、**38 條 test case**：happy 9 條、boundary 18 條、error 11 條。
- 最容易寫錯的地方都有邊界測試：升級的 19／20 點、9 級上限的 160／170 點、提醒的「剛好 24 小時」、題庫的版本號和題數。
- 提醒規則已依 Owner 決定（3A）定清楚：「任何 24 小時內」**不含**剛好 24 小時，所以提醒固定在 T+24、T+36、T+48……小時。
- 這份計畫只能測「規則算得對不對」；存檔真的「全部成功才算數」要另外用真的 SQLite 檔做整合測試（§9 R2）。

> **TL;DR:** 先把經驗值、等級、提醒、題庫檢查的規則寫成 38 條測試，以後寫程式、改程式時，跑一次就知道有沒有改壞。

---

## 2. Targets

> 全部是 Claude 提議的名稱和參數 **[M]**（還沒有程式碼）。時間一律由呼叫的人傳進來（`now`），函式自己不讀系統時間，才能測（見 §4）。

| # | Kind | Name | Signature | Public API | Confidence |
|---|---|---|---|---|---|
| T1 | function | `level_from_xp` | `(xp: int) → int` | true | **[M]** |
| T2 | function | `xp_for_answer` | `(is_correct: bool, is_first_attempt: bool) → int` | true | **[M]** |
| T3 | function | `submit_answer` | `(store: ProgressStore, question: Question, selected_choice: str or 空值, now: datetime) → SubmitResult`；`SubmitResult` 有 `is_correct`、`is_first_attempt`、`xp_gained`、`total_xp`、`level`、`leveled_up` | true | **[M]** |
| T4 | function | `next_reminder_at` | `(last_answered_at: datetime, reminders_since_last_answer: int) → datetime`；還沒作答過時，`last_answered_at` 傳第一次開啟的時間 | true | **[M]** |
| T5 | function | `count_reminders_since` | `(shown_at: list of datetime, last_answered_at: datetime) → int` | true | **[M]** |
| T6 | function | `needs_download` | `(remote_version: int, local_version: int) → bool` | true | **[M]** |
| T7 | function | `validate_bank` | `(manifest: BankManifest, bank: QuestionBank) → 通過，或丟出 BankError(code)` | true | **[M]** |

- `ProgressStore` 是本機存資料的介面（讀經驗值、查這題有沒有作答過、把「作答紀錄＋新經驗值」一起存檔），實作是 ADR-002 的 SQLite。
- 不測：畫面、出題的隨機挑選、下載本身（網路）、`ProgressStore` 的 getter／setter。

---

## 3. Test Cases（3 categories minimum）

### T1 `level_from_xp`

#### TC-001 · Category **happy** · **[H]**
- **Target:** `level_from_xp`
- **Input:** `xp = 0`
- **Expected:** `1`
- **Edge rationale:** 新玩家從 1 級開始
- **Source:** prd FR-2；progress 11-08 H3

#### TC-002 · Category **boundary** · **[H]**
- **Target:** `level_from_xp`
- **Input:** `xp = 19`
- **Expected:** `1`
- **Edge rationale:** 升級門檻前 1 點
- **Source:** prd FR-2「20 點升一級」

#### TC-003 · Category **boundary** · **[H]**
- **Target:** `level_from_xp`
- **Input:** `xp = 20`
- **Expected:** `2`
- **Edge rationale:** 剛好到升級門檻
- **Source:** AC-2

#### TC-004 · Category **boundary** · **[H]**
- **Target:** `level_from_xp`
- **Input:** `xp = 160`
- **Expected:** `9`
- **Edge rationale:** 剛好升滿 9 級
- **Source:** prd FR-2 等級上限；AC-8

#### TC-005 · Category **boundary** · **[H]**
- **Target:** `level_from_xp`
- **Input:** `xp = 170`、`xp = 180`、`xp = 1000`
- **Expected:** 都是 `9`
- **Edge rationale:** 超過上限不能變成 10 級（公式 `1+INT(180/20)` 會算出 10）
- **Source:** prd FR-2；AC-8；api-spec E3 `level = min(9, …)`

#### TC-006 · Category **error** · **[M]**
- **Target:** `level_from_xp`
- **Input:** `xp = -10`
- **Expected:** 丟出錯誤（不合法的經驗值）
- **Edge rationale:** 經驗值不會是負數，出現就代表資料壞了，不能默默算成某個等級
- **Source:** data-model PlayerProgress `xp ≥ 0`

### T2 `xp_for_answer`

#### TC-007 · Category **happy** · **[H]**
- **Target:** `xp_for_answer`
- **Input:** `is_correct = true, is_first_attempt = true`
- **Expected:** `10`
- **Edge rationale:** 標準路徑
- **Source:** prd FR-2；AC-1

#### TC-008 · Category **boundary** · **[H]**
- **Target:** `xp_for_answer`
- **Input:** `is_correct = true, is_first_attempt = false`
- **Expected:** `0`
- **Edge rationale:** 重複出現的題目答對不加分
- **Source:** AC-6；prd FR-1

#### TC-009 · Category **boundary** · **[H]**
- **Target:** `xp_for_answer`
- **Input:** `is_correct = false, is_first_attempt = true`
- **Expected:** `0`
- **Edge rationale:** 第一次就答錯，這題以後也拿不到分
- **Source:** prd FR-1「只有第一次作答會計入經驗值」

### T3 `submit_answer`（`store` 用假的記憶體版本，見 §4）

#### TC-010 · Category **happy** · **[H]**
- **Target:** `submit_answer`
- **Input:** store：經驗值 0、沒有任何紀錄；題目第 1 題（答案 B）；`selected_choice = B`
- **Expected:** `is_correct = true`、`is_first_attempt = true`、`xp_gained = 10`、`total_xp = 10`、`level = 1`、`leveled_up = false`；store 多 1 筆作答紀錄，內容含作答時間、題號、觀念、選的答案、對錯、第一次作答、得到的經驗值
- **Edge rationale:** 標準路徑
- **Source:** AC-1；AC-5

#### TC-011 · Category **happy** · **[H]**
- **Target:** `submit_answer`
- **Input:** store：經驗值 10；第 3 題從沒作答過；選對
- **Expected:** `total_xp = 20`、`level = 2`、`leveled_up = true`
- **Edge rationale:** 升級
- **Source:** AC-2

#### TC-012 · Category **boundary** · **[H]**
- **Target:** `submit_answer`
- **Input:** store：經驗值 160；第 5 題從沒作答過；選對
- **Expected:** `total_xp = 170`、`level = 9`、`leveled_up = false`
- **Edge rationale:** 9 級上限，經驗值照加但不升級
- **Source:** AC-8

#### TC-013 · Category **boundary** · **[H]**
- **Target:** `submit_answer`
- **Input:** store：經驗值 10，第 4 題已有一筆「答錯」的紀錄；第 4 題再出現，這次選對
- **Expected:** `is_correct = true`、`is_first_attempt = false`、`xp_gained = 0`、`total_xp = 10`；store 多 1 筆紀錄，標記「不是第一次作答」
- **Edge rationale:** 同一題第二次出現
- **Source:** AC-6

#### TC-014 · Category **boundary** · **[M]**
- **Target:** `submit_answer`
- **Input:** 依序作答：第 1 題對、第 2 題錯、第 1 題又對、第 3 題對
- **Expected:** 最後 `total_xp = 20`，而且等於所有作答紀錄 `xp_gained` 的總和
- **Edge rationale:** 經驗值和紀錄要一直對得上
- **Source:** data-model PlayerProgress「`xp` 要等於所有作答紀錄 `xp_gained` 的總和」

#### TC-015 · Category **error** · **[H]**
- **Target:** `submit_answer`
- **Input:** store：經驗值 0；第 2 題；`selected_choice` 是空值
- **Expected:** 丟出「沒有選答案」的錯誤；經驗值仍是 0；不新增作答紀錄；之後選了答案再送出，`is_first_attempt = true`
- **Edge rationale:** 空白不能用掉第一次作答
- **Source:** AC-7（Owner 決定 3A）

#### TC-016 · Category **error** · **[H]**
- **Target:** `submit_answer`
- **Input:** store：經驗值 0；第 1 題；選對；store 存檔時丟出寫入失敗
- **Expected:** 丟出「存檔失敗」的錯誤；store 的經驗值仍是 0、沒有新紀錄
- **Edge rationale:** 存檔失敗不能只存一半
- **Source:** AC-10（Owner 決定 4A）；ADR-002

#### TC-017 · Category **error** · **[H]**
- **Target:** `submit_answer`
- **Input:** 接 TC-016，store 恢復正常後再送出同一個答案
- **Expected:** `is_first_attempt = true`、`xp_gained = 10`、`total_xp = 10`
- **Edge rationale:** 存檔失敗的那次不能算「已作答」
- **Source:** AC-10「寫入恢復正常後再送出，仍算第一次作答」

#### TC-018 · Category **error** · **[H]**
- **Target:** `submit_answer`
- **Input:** store：經驗值 0；第 1 題；`selected_choice` 是不在 4 個選項裡的文字
- **Expected:** 丟出「答案不在選項裡」的錯誤；經驗值仍是 0；不新增作答紀錄；之後送出合法答案，`is_first_attempt = true`（處理方式和 TC-015 空白答案一樣）
- **Edge rationale:** 畫面上不會發生，發生就是程式或題庫資料有 bug；不能讓 bug 用掉玩家的第一次作答
- **Source:** AC-7；Owner 決定 2026-11-08（unit-test TODO 1A）

### T4 `next_reminder_at`（T = 最後作答時間）

#### TC-019 · Category **happy** · **[H]**
- **Target:** `next_reminder_at`
- **Input:** `last_answered_at = T`、`reminders_since_last_answer = 0`
- **Expected:** `T + 24 小時`
- **Edge rationale:** 第一則提醒
- **Source:** AC-4

#### TC-020 · Category **happy** · **[H]**
- **Target:** `next_reminder_at`
- **Input:** `T`、`1`
- **Expected:** `T + 36 小時`
- **Edge rationale:** 之後每 12 小時
- **Source:** AC-4

#### TC-021 · Category **boundary** · **[H]**
- **Target:** `next_reminder_at`
- **Input:** `T`、`2`
- **Expected:** `T + 48 小時`（和第一則剛好相隔 24 小時，**可以**提醒）
- **Edge rationale:** 「任何 24 小時內最多 2 則」不含剛好 24 小時
- **Source:** AC-4；Owner 決定 2026-11-08（unit-test 3A）

#### TC-022 · Category **boundary** · **[H]**
- **Target:** `next_reminder_at`
- **Input:** `T`，`reminders_since_last_answer` 從 0 到 9，算出 10 個提醒時間
- **Expected:** 任選一個起點 `t`，落在 `[t, t + 24 小時)` 裡的提醒都不超過 2 則
- **Edge rationale:** 用很多則一起檢查「最多 2 則」，不只看前 3 則
- **Source:** AC-4；3A

#### TC-023 · Category **boundary** · **[M]**
- **Target:** `next_reminder_at`
- **Input:** `T`、`1`（第一則實際在 `T + 24 小時 10 分` 才跳出，在 NFR A3 的 15 分鐘內）
- **Expected:** 仍是 `T + 36 小時`，不會因為第一則晚跳就整個往後延
- **Edge rationale:** 用預定時間算，不用實際跳出時間算
- **Source:** NFR A3；Claude 假設（見 §12）

#### TC-024 · Category **error** · **[M]**
- **Target:** `next_reminder_at`
- **Input:** `T`、`-1`
- **Expected:** 丟出錯誤（次數不能是負數）
- **Edge rationale:** 不合法的輸入
- **Source:** signature 推導

#### TC-038 · Category **boundary** · **[H]**
- **Target:** `next_reminder_at`
- **Input:** 剛安裝、還沒有任何作答紀錄；第一次開啟時間是 `C`（data-model PlayerProgress `created_at`）。呼叫的人傳入 `last_answered_at = C`、`reminders_since_last_answer = 0`
- **Expected:** `C + 24 小時`；之後的規則和 AC-4 一樣（`C + 36 小時`……）
- **Edge rationale:** 裝了程式卻從沒練習，也要被提醒
- **Source:** AC-4；Owner 決定 2026-11-08（unit-test TODO 3A）

### T5 `count_reminders_since`

#### TC-025 · Category **happy** · **[H]**
- **Target:** `count_reminders_since`
- **Input:** `shown_at = [T+24h, T+36h]`、`last_answered_at = T`
- **Expected:** `2`
- **Edge rationale:** 標準路徑；重開機後從提醒紀錄重新算出次數（AC-9）
- **Source:** AC-4、AC-9；data-model ReminderLog

#### TC-026 · Category **boundary** · **[H]**
- **Target:** `count_reminders_since`
- **Input:** `shown_at = [T+24h, T+36h]`、`last_answered_at = T+40h`（使用者在第 2 則之後回來作答）
- **Expected:** `0`；接著 `next_reminder_at(T+40h, 0)` 是 `T+64h`
- **Edge rationale:** 再作答後從頭計算
- **Source:** AC-4「下一次提醒改從這次作答的時間重新計算」

#### TC-027 · Category **boundary** · **[H]**
- **Target:** `count_reminders_since`
- **Input:** `shown_at = [T+24h]`、`last_answered_at = T+24h`（作答和提醒在同一刻）
- **Expected:** `0`（只算時間**晚於**最後作答的提醒）
- **Edge rationale:** 時間剛好相等；使用者已經回來作答，提醒從 0 重新計算
- **Source:** AC-4「再作答就重新計算」；Owner 決定 2026-11-08（unit-test TODO 2A）

### T6 `needs_download`

#### TC-028 · Category **happy** · **[H]**
- **Target:** `needs_download`
- **Input:** `remote_version = 3, local_version = 2`
- **Expected:** `true`
- **Edge rationale:** 有新題目
- **Source:** api-spec §2 使用流程第 2 步；AC-11

#### TC-029 · Category **boundary** · **[H]**
- **Target:** `needs_download`
- **Input:** `3, 3`
- **Expected:** `false`
- **Edge rationale:** 版本相同不下載
- **Source:** api-spec「**大於**本機版本才下載」

#### TC-030 · Category **boundary** · **[M]**
- **Target:** `needs_download`
- **Input:** `2, 3`（雲端版本比本機舊，例如 GitHub 快取）
- **Expected:** `false`
- **Edge rationale:** 版本不會變小，不能把本機換成舊題庫
- **Source:** api-spec E1「不會變小」；ADR-003 快取

### T7 `validate_bank`（下面的「合格題庫」：版本 3、2 題，都是合格的選擇題）

#### TC-031 · Category **happy** · **[H]**
- **Target:** `validate_bank`
- **Input:** manifest `bank_version = 3, question_count = 2`；合格題庫（其中 1 題 `status = retired`）
- **Expected:** 通過
- **Edge rationale:** 停用的題目也算在題數裡
- **Source:** api-spec E1 `question_count`「含已停用的題目」

#### TC-032 · Category **error** · **[H]**
- **Target:** `validate_bank`
- **Input:** manifest 版本 3；題庫 `bank_version = 2`
- **Expected:** `BankError(BANK_VERSION_MISMATCH)`
- **Edge rationale:** 下載到新舊混在一起的檔案（GitHub 快取）
- **Source:** api-spec E2；AC-13；ADR-003

#### TC-033 · Category **error** · **[H]**
- **Target:** `validate_bank`
- **Input:** manifest `question_count = 3`；題庫只有 2 題
- **Expected:** `BankError(BANK_VERSION_MISMATCH)`
- **Edge rationale:** 下載不完整
- **Source:** api-spec E2；§5「版本號或題數對不上」

#### TC-034 · Category **error** · **[H]**
- **Target:** `validate_bank`
- **Input:** 每次只壞一個地方，各測一次：(a) `answer` 不在 `choices` 裡；(b) `choices` 只有 3 個；(c) `choices` 有重複；(d) 兩題 `id` 相同；(e) `status = "deleted"`；(f) `explanation` 是空字串；(g) `concept` 是空字串
- **Expected:** 每一種都是 `BankError(BANK_INVALID_FORMAT)`
- **Edge rationale:** §3 每一條規則都要有一個反例
- **Source:** api-spec §3 Question

#### TC-035 · Category **boundary** · **[H]**
- **Target:** `validate_bank`
- **Input:** 某題 `added_in_version = 3`（等於 `bank_version`）
- **Expected:** 通過
- **Edge rationale:** `≤` 的等號那一邊
- **Source:** api-spec `added_in_version ≤ bank_version`

#### TC-036 · Category **error** · **[H]**
- **Target:** `validate_bank`
- **Input:** 某題 `added_in_version = 4`（大於 `bank_version` 3）
- **Expected:** `BankError(BANK_INVALID_FORMAT)`
- **Edge rationale:** `≤` 超過的那一邊
- **Source:** api-spec `added_in_version ≤ bank_version`

#### TC-037 · Category **error** · **[M]**
- **Target:** `validate_bank`
- **Input:** manifest 和題庫都是版本 0
- **Expected:** `BankError(BANK_INVALID_FORMAT)`
- **Edge rationale:** 版本號最小是 1
- **Source:** api-spec E1 `bank_version ≥ 1`

---

## 4. Mocking Strategy

| Action | Items | Rationale |
|---|---|---|
| **Mock** | `ProgressStore`（本機存資料）：用記憶體版本的假 store，可以設定「下一次存檔失敗」 | 要能製造「磁碟寫入失敗」（TC-016），真的 SQLite 很難做到 |
| **Mock** | 時間：一律用參數 `now`、`last_answered_at` 傳入固定時間（UTC） | 不能真的等 24 小時；函式自己讀系統時間就沒辦法測 |
| **Mock** | 網路（E1、E2 下載） | 這份計畫不測下載本身；`validate_bank` 直接吃下載好的資料 |
| **Do not mock** | `level_from_xp`、`xp_for_answer`（在 `submit_answer` 裡直接用真的） | 同一套規則的純函式，mock 掉就測不到真正的計算 |
| **Do not mock** | `next_reminder_at`、`count_reminders_since` 互相搭配時（TC-026） | 同上 |
| **Do not mock** | `Question`、`BankManifest`、`QuestionBank` 這些資料物件 | 只是資料，直接建真的 |

---

## 9. Risks（top 3）

> **R1：函式名稱和參數是先提議的，真正的程式可能長得不一樣** — 寫程式時如果改了參數（例如提醒改成傳整個紀錄清單），測試就要跟著改，改的時候可能漏掉規則。 — **Mitigation:** ADR-001 選定後，寫程式前先把這 38 條翻成 pytest 或 GUT，規則（輸入 → 預期）不動，只改名稱和參數。 — **Owner:** Avi
>
> **R2：假的 store 證明不了「全部成功才算數」** — TC-016 只證明程式「有處理」存檔失敗；SQLite 的 transaction 是不是真的沒存一半，要用真的資料庫檔測（AC-10、AC-13）。 — **Mitigation:** 另外寫整合測試，用暫存的 SQLite 檔，在存檔中途讓它失敗，確認經驗值和紀錄都沒變；可以和 ADR-001 小試驗第 4 項一起做。 — **Owner:** Avi
>
> **R3：真實時間的問題測不到** — 測試都用固定時間；電腦睡眠、手動改時間、時區設定錯，提醒可能不準。 — **Mitigation:** 照 NFR A3 的方法，開發時把 24／12 小時縮短成幾分鐘，在真的 Windows 上試一次；時間一律用 UTC 存（data-model）。 — **Owner:** Avi

---

## 12. Confidence & Sources & TODO

- **整份 plan 最低 confidence 項：**
  - **[L]**：無（TC-018、TC-027 已由 Owner 決定，2026-11-08）。
  - **[M]**：§2 全部 7 個 target 的名稱和參數；TC-006、TC-014、TC-023、TC-024、TC-030、TC-037。
- **Fabricated assumptions（推測但 input 未明說）：**
  - 7 個函式的名稱、參數、`SubmitResult` 的欄位是 Claude 提議。
  - 下一則提醒用「預定時間」算，不用「實際跳出時間」算（TC-023）。
  - 經驗值是負數、提醒次數是負數、版本號是 0 時要丟出錯誤（TC-006、TC-024、TC-037），規格只寫了合法範圍，沒寫不合法時怎麼辦。
  - 雲端版本比本機舊時不下載（TC-030）。
- **Highest-value next input:** ADR-001 選定框架（決定用 pytest 還是 GUT，以及真正的函式名稱）。

### TODO（缺資料）

- ~~TC-018、TC-027、還沒作答過的提醒~~ → Owner 決定 2026-11-08（1A 2A 3A），見 TC-018、TC-027、TC-038
- _TODO: AC-10、AC-13 的整合測試（真的 SQLite 檔，見 R2）_
- _TODO: 階段 5 寫程式題的遞減經驗值（10→8→6→4→2）和 ADR-005 的批改，到階段 5 再加_
