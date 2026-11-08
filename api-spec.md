---
doc_type: "api-spec"
variant: "light"
status: "draft"
owner: "Avi"
last_updated: "2026-11-08"
upstream:
  required: ["srs", "user-story"]
  optional: ["api-style-guide", "error-taxonomy"]
---

# API Spec: 學習精靈 · 雲端資料介面 v0.1

**Status:** Draft · **Owner:** Avi · **Last updated:** 2026-11-08

> [!NOTE]
> 依據：`prd.md` v0.7（§6 Privacy、題目更新；FR-1～FR-3；Counter）、`acceptance-criteria.md` v0.3（AC-5、AC-11～AC-13、§4 Privacy；User Story）、`c4-diagram.md` v0.2（§2、§3、§9 R6）、`roadmap.md` v0.3、`practice-questions-stage0.md`、`create-stage0-form.gs`。沒有 SRS，以 PRD 和驗收條件代替。範圍、題庫是否要登入、上傳時的身分確認、題目能不能修改由 Owner 決定（2026-11-08：1B 2A 3C 4A）。
>
> **這份文件和一般 API Spec 的差別：** 學習精靈**沒有自己的伺服器**，雲端部分用現成服務（Owner 決定 3B）。所以這裡定義的是「**邏輯上的介面**」：桌面程式和雲端之間要交換哪些資料、格式長什麼樣子、出錯時怎麼處理。實際的網址、登入方式和服務回傳的錯誤，要等「雲端資料服務」ADR 選定服務後再對應。

---

## 1. Executive Summary

- **用途：** 定義學習精靈桌面程式和雲端資料服務之間的資料格式。階段 1 下載題庫；階段 3 之後上傳自己的經驗值和等級，並讀取同學的經驗值和等級。（依據：c4-diagram §3；roadmap §2）
- **使用者（consumer）：** 只有學習精靈桌面程式。題庫由 Avi 編輯 GitHub 公開題庫 repo 的檔案，跑檢查程式後 push（`adr-003-cloud-data-service.md`，Owner 決定 2026-11-08，4A）。
- **共 4 個介面：** 2 個階段 1 用（**[M]**），2 個階段 3+ 用（**[L]**，身分確認方式還沒定）。
- **凍結狀態：** 題庫格式（§3 的 Question）建議在階段 0 結束、開始寫階段 1 程式前凍結；經驗值的格式等階段 3 前再凍結。_TODO: 凍結時間待 Owner 確認_
- **這份文件也補上之前列的缺口 M5「題庫格式說明」**（progress 11-08 問題清單）。

> **TL;DR:** 學習精靈從雲端下載不能修改、只能新增的題庫（不用登入）；階段 3 之後上傳和讀取「暱稱、經驗值、等級」三個欄位，其他作答資料都不離開玩家的電腦。

---

## 2. Endpoints（核心）

> 路徑是邏輯名稱，不代表實際網址。

| # | Method | Path | Operation | 做什麼 | Auth | Idempotency | 階段 | Confidence |
|---|---|---|---|---|---|---|---|---|
| E1 | GET | `/v1/question-bank/manifest` | getBankManifest | 讀取雲端題庫的版本號，判斷有沒有新題目 | 不用登入（2A） | n/a（只讀取） | 1 | **[M]** |
| E2 | GET | `/v1/question-bank` | getQuestionBank | 下載整份題庫 | 不用登入（2A） | n/a（只讀取） | 1 | **[M]** |
| E3 | PUT | `/v1/players/{player_id}/progress` | putMyProgress | 上傳自己的暱稱、經驗值、等級（整筆覆蓋） | 匿名登入，只能寫自己那一筆（ADR-006） | **required**：同樣內容重送，結果相同；用 `player_id` 決定要覆蓋哪一筆 | 3+ | **[L]** |
| E4 | GET | `/v1/players/progress` | listClassProgress | 讀取同學的暱稱、經驗值、等級 | 匿名登入（ADR-006） | n/a（只讀取） | 3+ | **[L]** |

**使用流程（依據：AC-11～AC-13）：**
1. 桌面程式檢查題庫時呼叫 E1。_TODO: 開機時檢查還是每天檢查，待 Owner 決定（AC-11 TODO）_
2. E1 的 `bank_version` **大於**本機題庫的版本號，才呼叫 E2 下載。
3. E2 下載完成後，**整份通過 §3 的檢查**才替換本機題庫；任何一項檢查沒過，就保留原本的題庫，下次檢查時再試（AC-13）。
4. 沒有網路時跳過 1～3，直接用本機題庫出題（AC-12）。

**階段 1 實際做法（`adr-003-cloud-data-service.md`，Proposed）：** E1 是題庫 repo 裡的題庫版本檔、E2 是整份題庫檔，程式用 GitHub 的 raw 網址下載。GitHub 有快取，push 後幾分鐘內可能讀到新版本檔、舊題庫檔，會被當成 `BANK_VERSION_MISMATCH`，下次再試即可。_TODO: 實際網址，等 Avi 建好 repo_。E3、E4 等階段 3+ 的雲端 ADR。

---

## 3. Request / Response Schemas

### E1 `GET /v1/question-bank/manifest` · Request

沒有參數。**[M]**

### E1 · Response `200` `BankManifest`

| Field | Type | Required | Validation | Confidence |
|---|---|---|---|---|
| `bank_version` | integer | [YES] | ≥ 1；每次發布新題目就加 1，不會變小 | **[M]** |
| `question_count` | integer | [YES] | ≥ 1；等於 E2 `questions` 的筆數（含已停用的題目） | **[M]** |
| `updated_at` | string（日期時間） | [YES] | ISO 8601，例如 `2026-11-09T09:00:00+08:00` | **[M]** |

### E2 `GET /v1/question-bank` · Request

沒有參數，每次下載整份題庫。**[M]**（見 §12 假設）

### E2 · Response `200` `QuestionBank`

| Field | Type | Required | Validation | Confidence |
|---|---|---|---|---|
| `bank_version` | integer | [YES] | 要和 E1 的 `bank_version` 相同，不同就視為下載不完整（AC-13） | **[M]** |
| `questions` | array of `Question` | [YES] | 筆數要和 E1 的 `question_count` 相同；`id` 不能重複 | **[M]** |

### `Question`（題庫裡的一題）

| Field | Type | Required | Validation | Confidence | 依據 |
|---|---|---|---|---|---|
| `id` | string | [YES] | 整個題庫唯一；**發布後永遠不改、不重複使用**（4A）。_TODO: 正式的編號格式待 Owner 決定（階段 0 用 A1～D3）_ | **[M]** | Owner 決定 4A；AC-5「題號」 |
| `concept` | string | [YES] | 不能空白，例如「字串與數字」；同一個觀念的題目要用完全相同的文字 | **[M]** | prd G2、§12 假設；AC-5「觀念」 |
| `type` | string | [YES] | `multiple_choice`（選擇題）或 `code_fill`（程式填空，階段 5） | **[M]** / **[L]**（`code_fill`） | prd FR-1 |
| `code` | string | [YES] | 題目的 Python 程式碼，保留換行和縮排 | **[H]** | practice-questions-stage0 |
| `prompt` | string | [YES] | 題目文字，例如「這段程式會印出什麼？」 | **[H]** | practice-questions-stage0 |
| `choices` | array of string | 選擇題 [YES] | 選擇題剛好 4 個、不能重複；程式填空不用 | **[M]** | prd Counter「4 選 1」；practice-questions-stage0 |
| `answer` | string | [YES] | 選擇題：必須是 `choices` 其中一個。程式填空：_TODO: 答案格式和批改方式待「程式碼批改」ADR_ | **[M]** / **[L]** | prd FR-1；AC-1 |
| `explanation` | string | [YES] | 不能空白；答錯時顯示，也是沒網路時的備用說明 | **[H]** | prd FR-3（4-4A）；AC-3 |
| `status` | string | [YES] | `active`（會出題）或 `retired`（停用，不再出題，但保留給舊的作答紀錄對照） | **[M]** | Owner 決定 4A |
| `added_in_version` | integer | [YES] | 這題在哪個 `bank_version` 加入；≤ `bank_version` | **[M]** | 依 4A 推得 |

**題目修改規則（4A）：** 題目發布後不能修改。要改錯字或答案時，把舊題的 `status` 改成 `retired`，再新增一題新的 `id`。只有 `status` 可以從 `active` 改成 `retired`，其他欄位一律不改。

### E1、E2 · 錯誤情況

| Status | Schema | Notes |
|---|---|---|
| `400` | `ValidationError` | 下載的內容沒通過上面的檢查（例如 `bank_version` 對不上、`answer` 不在 `choices` 裡）。這是桌面程式自己判斷的，不是服務回傳的。錯誤代碼：`BANK_INVALID_FORMAT`、`BANK_VERSION_MISMATCH` |
| `401` | `AuthError` | 題庫不用登入（2A），正常情況不會發生；如果雲端權限設錯才會出現。錯誤代碼：`AUTH_REQUIRED` |
| `500` | `InternalError` | 雲端服務出錯。錯誤代碼：`SERVICE_ERROR` |
| — | — | 沒網路（AC-12）：`NETWORK_UNAVAILABLE`；下載到一半中斷（AC-13）：`BANK_DOWNLOAD_INTERRUPTED` |

不管哪一種錯誤：保留本機原本的題庫，不影響作答紀錄、經驗值和等級，下次檢查時再試。（依據：AC-12、AC-13）

### E3 `PUT /v1/players/{player_id}/progress` · Request（階段 3+）

| Field | Type | Required | Validation | Confidence |
|---|---|---|---|---|
| `player_id`（路徑） | string | [YES] | 代表這位玩家的固定代號。就是雲端服務匿名登入拿到的代號；雲端規則只允許寫入自己代號的那一筆（`adr-006-stage3-cloud.md`，Proposed） | **[L]** |
| `nickname` | string | [YES] | 不能空白。_TODO: 長度上限、能不能和別人重複，待 Owner 決定_ | **[L]** |
| `xp` | integer | [YES] | ≥ 0 | **[M]** |
| `level` | integer | [YES] | 1～9（v1 上限 9 級），而且要等於 `min(9, 1 + INT(xp / 20))` | **[M]** |
| `updated_at` | string（日期時間） | [YES] | ISO 8601 | **[M]** |

**不能出現的欄位（Privacy）：** 作答紀錄、選的答案、程式碼、「卡在哪裡」的回答都不上傳。（依據：prd §6 Privacy；AC §4）

### E3 · Responses

| Status | Schema | Notes |
|---|---|---|
| `200` | `PlayerProgress` | 和 Request 相同的 `nickname`、`xp`、`level`、`updated_at` |
| `400` | `ValidationError` | `xp` 是負數、`level` 和 `xp` 對不上。錯誤代碼：`PROGRESS_INVALID` |
| `401` | `AuthError` | 不能確認身分，或想改別人的資料。錯誤代碼：`AUTH_REQUIRED`（實際行為要等 3C 決定） |
| `500` | `InternalError` | 雲端服務出錯。錯誤代碼：`SERVICE_ERROR` |

上傳失敗時，本機的經驗值和等級不受影響，畫面照常 3 秒內更新，之後再上傳。（依據：c4-diagram §9 R2；prd §6 Latency）

### E4 `GET /v1/players/progress` · Request（階段 3+）

沒有參數，一次讀取全部同學。**[L]**（見 §12 假設）

### E4 · Responses

| Status | Schema | Notes |
|---|---|---|
| `200` | array of `PlayerProgress` | 每筆**只有** `nickname`、`xp`、`level`、`updated_at`，不含 `player_id` 和任何作答資料（prd §6 Privacy） |
| `401` | `AuthError` | 錯誤代碼：`AUTH_REQUIRED`（實際行為要等 3C 決定） |
| `500` | `InternalError` | 錯誤代碼：`SERVICE_ERROR` |

---

## 5. Error Taxonomy（核心）

> 以下是**桌面程式內部使用的錯誤名稱**（Claude 草擬，待 Owner 確認）。雲端服務實際回傳的錯誤代碼，要等「雲端資料服務」ADR 選定服務後再對應到這些名稱。「重試」的意思是**下次檢查或下次上傳時再試**，不是馬上一直重試。

| Code | HTTP | Retryable | 什麼時候發生 | User message key | Confidence |
|---|---|---|---|---|---|
| `NETWORK_UNAVAILABLE` | — | [YES] | 沒有網路（AC-12） | _TODO: 要不要提示使用者，待 Owner 決定_ | **[M]** |
| `BANK_DOWNLOAD_INTERRUPTED` | — | [YES] | 下載題庫到一半中斷（AC-13） | `error.bank.download_failed` | **[M]** |
| `BANK_VERSION_MISMATCH` | 400 | [YES] | E1 和 E2 的版本號或題數對不上 | `error.bank.download_failed` | **[M]** |
| `BANK_INVALID_FORMAT` | 400 | [NO] | 題庫內容不符合 §3 的規則；要等 Avi 修正雲端題庫 | `error.bank.invalid` | **[M]** |
| `PROGRESS_INVALID` | 400 | [NO] | 上傳的經驗值或等級不合理（E3） | `error.progress.invalid` | **[L]** |
| `AUTH_REQUIRED` | 401 | [NO] | 沒有權限讀寫（E3、E4；E1、E2 只有權限設錯時才會發生） | `error.auth.required` | **[L]** |
| `SERVICE_ERROR` | 500 | [YES] | 雲端服務出錯 | `error.service.unavailable` | **[M]** |

_TODO: 每個 message key 實際要顯示的文字，待 Owner 提供（AC-12 規定沒網路時要能照常練習，提示不能擋住作答）_

---

## 10. Decision Log

| Date | Decision | Options | Chosen | Rejected why | Confidence |
|---|---|---|---|---|---|
| 2026-11-08 | API Spec 範圍（**Owner 決定** 1B） | A 只寫階段 1 題庫 / B 題庫＋階段 3+ 經驗值 / C 再加 AI 服務 / D 先不寫 | B，4 個邏輯介面，標出從哪個階段開始 | A：看不到階段 3 的資料格式；C：AI 是現成服務，格式由服務決定，沒有需要自己凍結的東西；D：題庫格式（M5）在階段 1 前一定要定 | **[H]** |
| 2026-11-08 | 下載題庫要不要登入（**Owner 決定** 2A） | A 不用登入 / B 要登入 / C 先留 TODO | A | B：階段 1 就要做登入功能，違反 roadmap「最難的放後面」；代價是同學可以看到答案，但階段 0 交卷後本來就會顯示答案，並由反指標（第一次作答答對率）持續觀察 | **[H]** |
| 2026-11-08 | 上傳經驗值時怎麼確認身分（**Owner 決定** 3C） | A 雲端服務帳號登入 / B 只用暱稱 / C 先留 TODO | C | A、B 現在選太早：階段 3 之後才需要，而且和「要不要防止竄改經驗值」（c4-diagram R6）是同一件事，等「雲端資料服務」ADR 一起決定 | **[H]** |
| 2026-11-08 | 題目可不可以修改（**Owner 決定** 4A） | A 不能改，只能新增、舊題停用 / B 可以改，用版本號蓋掉 / C 先留 TODO | A | B：每題只算第一次作答，題目一改，舊的作答紀錄就對不上，G2 也會算錯 | **[H]** |

---

## 12. Confidence & Sources & TODO

- **整份文件最低 confidence 欄位：** E3、E4 和它們的欄位都是 **[L]**（身分確認方式未定）；`code_fill` 題型和它的 `answer` 是 **[L]**（階段 5）；錯誤名稱是 Claude 草擬，標 **[M]** 或 **[L]**。E1、E2 和 Question 格式大多是 **[M]**：有 PRD、AC 和階段 0 題目當依據，但雲端服務還沒選。
- **Fabricated assumptions（推測但 input 未明說）：**
  - E2 每次下載整份題庫，不做「只下載新題目」。理由是題庫只有幾十到幾百題，整份下載比較簡單，也比較不容易出現資料不完整。題庫變得很大時再改。
  - 先用 E1 比對版本號、再決定要不要呼叫 E2，是為了避免每次都下載整份題庫；AC-11 沒有規定要這樣做。
  - `choices` 剛好 4 個，依據是 PRD Counter 的「4 選 1」和現有題目，Owner 沒有明說之後的題目都是 4 個選項。
  - E3 用 PUT（整筆覆蓋），因為上傳的是「目前的經驗值和等級」，重送幾次結果都一樣；Owner 沒有另外說明。
  - E4 一次讀取全部同學、不分頁，因為一個班大約 35 人。如果之後開放給其他班，要再考慮分頁。
  - `player_id` 和 `nickname` 分開，是為了讓暱稱可以改而資料不會亂掉；實際怎麼做要等 3C。
  - 路徑前面的 `/v1` 只是表示格式的版本，不代表實際網址。
- **Highest-value next input:** Avi 建好 GitHub 題庫 repo 後的實際網址，填進 E1、E2（ADR-003）；E3、E4 等階段 3+ 的雲端 ADR。

### TODO（缺資料）

- ~~E1、E2 的雲端服務~~ → GitHub 公開題庫 repo（ADR-003）；_TODO: E1、E2 的實際網址；E3、E4 的實際做法（階段 3+ 的雲端 ADR）_
- _TODO: 上傳時的身分確認、要不要防止竄改經驗值（3C；c4-diagram R6）_
- _TODO: 題目 `id` 的正式編號格式_
- _TODO: 暱稱長度上限、能不能和別人重複_
- _TODO: 程式填空題的 `answer` 格式（「程式碼批改」ADR，階段 5）_
- _TODO: 檢查新題目的時機（AC-11）_
- _TODO: 每個錯誤 message key 的顯示文字；沒網路時要不要提示_
- _TODO: 題庫格式和經驗值格式的凍結時間_
- ~~Avi 怎麼把題庫上傳到雲端~~ → 編輯檔案、跑檢查程式、push（ADR-003，4A）
