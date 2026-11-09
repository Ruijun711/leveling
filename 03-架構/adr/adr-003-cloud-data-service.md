---
doc_type: "adr"
variant: "light"
status: "accepted"
owner: "Avi"
last_updated: "2026-11-09"
upstream:
  required: ["technical-discussion-notes"]
  optional: ["prd", "c4-diagram", "nfr"]
---

# ADR-003: 階段 1 的題庫放在哪個雲端服務

**Status:** Accepted（2026-11-08）· **Owner:** Avi · **Last updated:** 2026-11-09

> [!NOTE]
> 依據：`api-spec.md` v0.1（E1、E2、2A、4A、§5）、`c4-diagram.md` v0.2（§2 雲端資料服務、§9 R3、§12 TODO）、`roadmap.md` v0.3（§2 階段 1、3+）、`prd.md` v0.7（§6 題目更新、§9 R2、Decision Log 3B、C）、`acceptance-criteria.md` v0.4（AC-11～AC-13）。範圍、服務、費用、更新題庫的方式由 Owner 決定（2026-11-08：1B 2A 3A 4A）。
>
> 這份 ADR 是**單一決策**：只決定**階段 1 的題庫**（api-spec E1、E2）放在哪裡。階段 3+ 的上傳和讀取經驗值（E3、E4）、身分確認（api-spec 3C）、防止竄改（c4-diagram R6），到階段 3 前另寫 ADR（Owner 決定 1B）。

---

## 1. Context

- 階段 1 要從雲端下載題庫，讓試用期間可以出新題目；只下載，不上傳任何玩家資料（依據：prd §6 題目更新；Owner 決定 C）。
- 題庫不用登入就能下載（api-spec 2A），題目發布後不能修改，只能新增、舊題停用（api-spec 4A）。
- 程式先讀題庫版本（E1），版本比本機新才下載整份題庫（E2）；下載不完整就保留舊版（AC-13）。
- 用現成服務，不自己寫伺服器（Owner 決定 3B）。題庫只有幾十到幾百題，資料量很小（api-spec §12）。
- 專案資料夾裡有問卷回覆和 concierge 測試資料，當時以為有同學的真名，**不能公開**；題庫要放在另外的地方。（2026-11-09 Owner 確認：問卷是匿名的；concierge 測試只有暱稱，其中一個像真名的已改成「同學 E」，連同 git 紀錄一起改寫；專案 repo 公開在 `Ruijun711/leveling`）

> **TL;DR:** 階段 1 開始寫程式前，要決定題庫檔案放在哪個雲端服務，程式才知道去哪裡下載新題目。

---

## 2. Decision Drivers

| Driver | Weight | Why this matters |
|---|---|---|
| 好不好學、好不好用 | High | Owner 寫程式還不是很強，雲端是 R2 的第 (6) 項難處（brief §主要約束；prd §9 R2） |
| 免費 | High | 個人專案；Owner 決定只用免費方案（3A） |
| 程式下載穩不穩定 | High | 下載失敗時學生看不到新題目，G1 會偏低（c4-diagram R3） |
| 題目改了什麼有沒有紀錄 | Medium | 題目只能新增、不能改（4A），要能查出每一版加了哪些題 |
| 以後換服務難不難 | Medium | 綁定一家服務，之後要換也比較麻煩（c4-diagram R3） |
| 現在用不用得到資料庫和登入 | Low | 階段 1 不需要；階段 3 另寫 ADR（1B） |

---

## 3. Options Considered

### Option A: GitHub 公開 repo（另開一個只放題庫的 repo）

- **Pros:** 免費；Owner 已經在用 git，改題目就是改檔案再 push；每次加了哪些題都有 git 紀錄，正好符合 4A；程式用固定網址直接下載檔案，不用登入；只放 2 個檔案，以後換服務只要改程式裡的網址
- **Cons:** 要申請 GitHub 帳號、學 push；repo 是公開的，Owner 的 GitHub 名稱和所有答案都公開（答案公開已在 2A 接受）；GitHub 的下載網址有快取，push 後大約要等幾分鐘學生才下載得到
- **Cost:** 免費；一次性成本是申請帳號、學 push

### Option B: Google 雲端硬碟公開連結

- **Pros:** Owner 已經在用 Google 表單和試算表，最熟悉；免費
- **Cons:** 公開連結的「直接下載」不穩定，常常跳到確認頁面或要求登入，程式不好處理；沒有方便的修改紀錄；每次換檔案可能要重新分享
- **Cost:** 免費

### Option C: Firebase 或 Supabase（有資料庫的雲端服務）

- **Pros:** 階段 3 的上傳經驗值、登入也能用同一家服務
- **Cons:** 階段 1 用不到資料庫和登入，太早學，違反 roadmap「最難的放後面」；設定存取權限比較複雜，設錯可能讓資料外洩；免費方案的規則可能會改
- **Cost:** 免費方案可用；一次性成本是學資料庫和權限設定

### Option D: 保持現狀（不用雲端，題庫跟著安裝檔）

- **Pros:** 不用學雲端服務；完全沒有網路連線
- **Cons:** 出新題目就要讓同學重新安裝，階段 1 試用期間很難出新題，G1 會偏低
- **Cost:** 免費；Owner 已排除（Owner 決定 2026-11-08，2B）

---

## 6. Decision & Consequences

### Chosen: **Option A（GitHub 公開題庫 repo）** · **[H]**

> 2026-11-08 已建好 repo `https://github.com/Ruijun711/leveling-question-bank`，用 raw 網址實際下載 2 個檔案、照 api-spec §3 檢查都通過，和本機檔案完全一致，依 §6 Follow-up 改成 Accepted。

- **Scope:** 只適用於階段 1 起的題庫下載（api-spec E1、E2）。**不適用**於階段 3+ 的經驗值上傳和讀取（E3、E4）、身分確認、防竄改——階段 3 前另寫 ADR。
- **做法：**
  - 另外開一個**公開**的 GitHub repo，只放題庫，不放專案資料夾的任何其他檔案（當時是為了避免同學真名外流，見 §1）。repo：`Ruijun711/leveling-question-bank`（Owner 決定 2026-11-08）。
  - repo 裡放 2 個檔案：題庫版本檔（對應 E1）和整份題庫檔（對應 E2），格式照 `api-spec.md` §3。
  - 程式用 GitHub 的 raw 網址下載這 2 個檔案：
    - E1：`https://raw.githubusercontent.com/Ruijun711/leveling-question-bank/main/manifest.json`
    - E2：`https://raw.githubusercontent.com/Ruijun711/leveling-question-bank/main/question-bank.json`
  - **第 1 版（2026-11-08）：** 17 題（Q001～Q012 是階段 0 的題目，Q013～Q017 是 concierge 測試的題目），每題答案都用 Python 實際執行確認過。
- **費用（Owner 決定 3A）：** 只用免費方案。
- **更新題庫（Owner 決定 4A）：** Owner 直接編輯題庫檔，push 前先跑檢查程式，確認：
  - 版本號比上一版大 1
  - 每題剛好 4 個選項，答案在選項裡面
  - 已發布的題目沒有被修改或刪除（只能新增、或把 `status` 改成 `retired`）
  - 題數和版本檔一致
- **Positive consequences:** 免費；不用學資料庫；每一版加了哪些題都有紀錄；以後換服務只要改 2 個網址；階段 1 完全不需要登入功能。
- **Negative consequences（必填）:**
  - Owner 要申請 GitHub 帳號、學 push；GitHub 名稱會公開。
  - 題庫和答案完全公開，同學可以先看答案再作答（2A 已接受，用反指標「第一次作答答對率」觀察）。
  - GitHub 的 raw 網址有快取：push 後幾分鐘內，有的同學可能讀到新的版本檔、舊的題庫檔，程式會判斷成「版本對不上」（`BANK_VERSION_MISMATCH`），下次檢查再下載就好，不會弄壞本機題庫（AC-13）。
  - 階段 3 可能要再用另一家服務（例如有資料庫的服務），到時候會有兩家服務要管。
  - GitHub 停止服務或改規則時，同學下載不到新題目，只能用本機已有的題庫（c4-diagram R3）。
- **Follow-up:**
  - Owner 申請 GitHub 帳號、建立公開題庫 repo，放入階段 1 的題庫。
  - 用瀏覽器或 ADR-001 的小試驗程式確認下載得到，然後把本 ADR 改成 Accepted，Confidence 改成 **[H]**。
  - 把實際網址寫進 `api-spec.md`。
  - 階段 1 開發時寫題庫檢查程式。_TODO: 檢查程式的檔名和放在哪裡（題庫 repo 或專案資料夾），開發時決定_
  - 階段 3 前另寫 ADR：上傳和讀取經驗值、身分確認（api-spec 3C）、防止竄改（c4-diagram R6）。

---

## 10. Decision Log

| Date | Decision | Options | Chosen | Rejected why | Confidence |
|---|---|---|---|---|---|
| 2026-11-08 | ADR 範圍（**Owner 決定** 1B） | A 一份 ADR 處理階段 1 和 3 / B 只決定階段 1 題庫，階段 3 另寫 / C 等階段 3 再一起寫 | B | A：階段 3 要等階段 0～2 試用完才知道做不做，現在選只能猜；C：階段 1 開始前就一定要知道題庫放哪裡 | **[H]** |
| 2026-11-08 | 題庫放在哪裡（**Owner 決定** 2A） | A GitHub 公開 repo / B Google 雲端硬碟 / C Firebase、Supabase / D 跟著安裝檔 | A | B：直接下載連結不穩定，程式不好處理；C：階段 1 用不到資料庫和登入，太早學；D：出新題要重新安裝，Owner 已排除（2B） | **[M]** |
| 2026-11-08 | 費用（**Owner 決定** 3A） | A 只用免費方案 / B 可以付費，設每月上限 | A | B：只放題庫，免費方案就夠用 | **[H]** |
| 2026-11-08 | 怎麼更新題庫（**Owner 決定** 4A） | A 直接編輯 JSON 檔，push 前跑檢查程式 / B 在 Google 試算表出題再轉換 / C 先留 TODO | A | B：多一個轉換步驟，容易出錯；C：格式錯了同學的程式會整份拒收（`BANK_INVALID_FORMAT`），一定要有檢查 | **[H]** |

---

## 12. Confidence & Sources & TODO

- **整份文件最低 confidence 欄位：** §10 第 2 條 **[M]**（當時還沒試）。§6 Chosen 已實際下載確認，改成 **[H]**。
- **Fabricated assumptions（推測但 input 未明說）：**
  - GitHub 的 raw 網址可以不用登入直接下載、快取大約幾分鐘、一個班 35 人的下載量不會被限制，是 Claude 依一般資料判斷，還沒實際試過。
  - Google 雲端硬碟直接下載連結不穩定，是 Claude 依一般經驗判斷。
  - repo 名稱 `leveling-question-bank` 是 Claude 提議。
  - 題庫檔用 JSON 格式（Owner 在 4A 選了「編輯 JSON 檔」；api-spec 沒有指定檔案格式）。
- **Highest-value next input:** push 新版題庫後，同學的程式多久下載得到（GitHub 快取的實際時間，NFR A5）。

### TODO（缺資料）

- ~~題庫 repo 的名稱和實際下載網址~~ → 見 §6（2026-11-08）
- _TODO: 題庫檢查程式的檔名和位置，開發時決定_
- ~~檢查新題目的時機（開機時或每天，AC-11）~~ → 開機時，之後每 24 小時（Owner 決定 2026-11-09，1C）
- _TODO: 階段 3+ 的雲端 ADR：上傳和讀取經驗值、身分確認（3C）、防止竄改（R6）_
