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

# ADR-002: 本機資料怎麼存

**Status:** Proposed · **Owner:** Avi · **Last updated:** 2026-11-08

> [!NOTE]
> 依據：`data-model.md` v0.1（§2 entity、§6 需要的查詢）、`acceptance-criteria.md` v0.3（AC-5、AC-9、AC-10、AC-13、§4 Privacy）、`c4-diagram.md` v0.2（§3 本機資料、§9 R1、R2）、`adr-001-desktop-framework.md`（Proposed）、`roadmap.md` v0.3（§3 試用方式）。格式、決定方式、試用資料怎麼收、備份由 Owner 決定（2026-11-08：1A 2A 3A 4A）。
>
> 這份 ADR 是**單一決策**：只決定本機資料用什麼格式存。存放位置、匯出檔、備份是這個決定的直接後果，寫在 §6。雲端資料服務、AI 服務、程式碼批改另寫 ADR。

---

## 1. Context

- 階段 1 要在使用者的電腦上存 5 種資料：玩家進度、題目、題庫版本、作答紀錄、提醒紀錄（依據：data-model §2）。
- 有兩個「失敗時不能弄壞資料」的要求：存檔失敗時，作答紀錄和經驗值都不能變（AC-10）；題庫下載到一半中斷時，要維持舊版（AC-13）。
- 重開機後進度和提醒時間都要還在（AC-9）；經驗值要先存在本機再顯示，3 秒內更新（prd §6 Latency；c4-diagram R2）。
- 階段 1 不上傳任何作答資料（AC §4 Privacy；Owner 決定 C）。但 roadmap 規定每階段試用後要算 G1、G2、反指標，資料只在同學電腦上，Avi 拿不到——這份 ADR 要一起解決。
- 桌面程式的框架（PySide6 或 Godot）還沒決定（ADR-001 Proposed），儲存方式要兩邊都做得到。

> **TL;DR:** 階段 1 要開始寫程式，得先決定進度和作答紀錄存在哪種檔案裡，才能做到「失敗不弄壞資料」，並讓 Avi 拿得到試用資料。

---

## 2. Decision Drivers

| Driver | Weight | Why this matters |
|---|---|---|
| 失敗時不弄壞資料（全部成功才算數） | High | AC-10、AC-13 直接要求；做錯的話經驗值和作答紀錄會對不上 |
| 好不好學、好不好寫 | High | Owner 會 Python，寫程式還不是很強（brief §主要約束；adr-001 Owner 2B） |
| PySide6、Godot 兩邊都做得到 | High | ADR-001 還沒選（adr-001 §6） |
| 支援 data-model §6 的 5 種查詢 | Medium | G1、G2、提醒「24 小時內最多 2 則」都要用；資料量很小（一個人幾百筆），速度不是問題 |
| 出問題時 Avi 看得懂資料 | Medium | 試用期間要能查「為什麼經驗值不對」 |
| 費用 | Medium | 個人專案，要免費 |

---

## 3. Options Considered

### Option A: SQLite（一個資料庫檔案）

- **Pros:** 內建「全部成功才算數」（transaction），AC-10、AC-13 直接做得到；Python 內建，不用另外安裝；§6 的查詢可以直接寫、加索引；只有一個檔案，好管理；網路資料多，問 AI 容易得到答案
- **Cons:** 不能用記事本打開，Avi 要看資料得用免費工具（例如 DB Browser for SQLite）；Godot 沒有內建，要另外裝外掛；要學一點 SQL；以後改欄位要寫「升級資料表」的程式
- **Cost:** 免費；一次性成本是學基本 SQL

### Option B: JSON 檔（一般文字檔）

- **Pros:** 用記事本就能打開看；PySide6、Godot 都內建讀寫 JSON；不用學 SQL
- **Cons:** 沒有「全部成功才算數」，要自己寫「先寫到暫存檔、成功再換掉舊檔」，寫錯就可能弄壞資料；作答紀錄越來越多時，每次都要整個檔案重寫；§6 的查詢要自己寫迴圈；使用者容易手動改經驗值
- **Cost:** 免費；一次性成本是自己寫安全存檔的程式

### Option C: 框架內建的設定檔（QSettings／Godot ConfigFile）

- **Pros:** 最簡單，幾行就能存經驗值
- **Cons:** 設計來存設定，不適合存一筆一筆的作答紀錄；沒有「全部成功才算數」；PySide6、Godot 寫法完全不同，換框架要重寫
- **Cost:** 免費

### Option D: 保持現狀（Google 表單＋試算表）

- **Pros:** 已經做好，Avi 直接看得到所有資料
- **Cons:** 要連網路才能存，違反「沒網路照常練」（AC-12）和「階段 1 不上傳作答資料」（AC §4 Privacy）；做不到 3 秒內更新
- **Cost:** 免費；prd 已經排除（Owner 決定 5A）

---

## 6. Decision & Consequences

### Chosen: **暫定 Option A（SQLite），ADR-001 小試驗確認後定案** · **[M]**

- **Scope:** 適用於階段 1～5 存在使用者電腦上的所有資料（data-model §2，包含之後的職業、技能、寶物）。不包含雲端資料（另寫「雲端資料服務」ADR）。
- **怎麼確認（Owner 決定 2A）：** 在 ADR-001 小試驗加第 4 項「把經驗值存進 SQLite，關掉程式重開，讀回來是對的」。PySide6、Godot 都要試。
  - 選定的框架做得到：本 ADR 改成 Accepted，Confidence 改成 **[H]**。
  - 選了 Godot 但 SQLite 外掛不好用：改用 Option B，並重寫本 ADR 的 §6。
- **存放位置（Claude 提議）：** `%APPDATA%\學習精靈\` 底下的一個資料庫檔案。不需要管理員權限；移除程式時可以選擇保留資料。**[M]**
- **安全存檔：** 作答紀錄和經驗值放在同一個 transaction 裡寫入（AC-10）；新題目和新的題庫版本號也放在同一個 transaction（AC-13）。**[H]**
- **試用資料（Owner 決定 3A）：** 程式有「匯出作答紀錄」按鈕，產生 CSV 檔，由同學自己決定要不要傳給 Avi。程式本身不上傳任何資料，符合 AC §4 Privacy。驗收條件見 AC-14。**[M]**
- **備份（Owner 決定 4A）：** v1 不做備份，接受「換電腦或重灌時資料不見」的風險（c4-diagram R1）。**[M]**
- **Positive consequences:** AC-10、AC-13 不用自己寫複雜的存檔程式；§6 的查詢都能直接做；Avi 拿得到試用資料算 G1、G2；同學看得到自己交出了什麼。
- **Negative consequences（必填）:**
  - Avi 要學一點 SQL，看資料要另外裝 DB Browser for SQLite。
  - 選 Godot 的話要多裝一個外掛，外掛更新慢或有問題時會卡住。
  - 以後改欄位（例如階段 2 加職業）要寫「升級資料表」的程式，不能直接改檔案。
  - 匯出檔要靠同學記得傳，G1、G2 可能收不齊；沒傳的人只能算成「不知道」。
  - 不備份：硬碟壞掉、重灌或換電腦時，進度全部不見；資料也可能被會用 DB Browser 的同學改掉（c4-diagram R6）。
- **Follow-up:**
  - ADR-001 小試驗做第 4 項，結果寫回本 ADR。
  - 開發時用 SQLite 內建的 `user_version` 記資料表版本，之後升級資料表才知道要從哪一版改起。_TODO: 開發時確認_
  - 階段 2 以後有職業、寶物，資料不見的損失變大時，重新考慮備份。
  - 試用時告訴同學怎麼匯出、傳給誰。

---

## 10. Decision Log

| Date | Decision | Options | Chosen | Rejected why | Confidence |
|---|---|---|---|---|---|
| 2026-11-08 | 本機資料的格式（**Owner 決定** 1A） | A SQLite / B JSON 檔 / C 框架內建設定檔 / D 保持現狀 | A（暫定） | B：沒有「全部成功才算數」，要自己寫，容易弄壞資料；C：不適合存作答紀錄，換框架要重寫；D：要連網路、會上傳作答資料，prd 已排除 | **[M]** |
| 2026-11-08 | 框架還沒選怎麼辦（**Owner 決定** 2A） | A 先 Proposed，加進 ADR-001 小試驗 / B 現在直接定案 / C 等 ADR-001 選完再寫 | A | B：不確定 Godot 的 SQLite 外掛好不好用；C：小試驗本來就要做，多試一項只多一點時間，不用等 | **[H]** |
| 2026-11-08 | Avi 怎麼拿到試用資料（**Owner 決定** 3A） | A 匯出 CSV、同學自己傳 / B 自動上傳到雲端 / C 不收集、問卷自填 | A | B：違反「階段 1 不上傳作答資料」（Owner 決定 C）和 Privacy；C：靠同學自己回報，G1、G2 不準 | **[H]** |
| 2026-11-08 | 備份（**Owner 決定** 4A） | A v1 不做 / B 用匯出檔匯入還原 / C 自動備份到雲端 | A | B：匯入要處理資料重複、格式不對，工作量大，違反 roadmap「最難的放後面」；C：違反「只下載、不上傳」 | **[H]** |

---

## 12. Confidence & Sources & TODO

- **整份文件最低 confidence 欄位：** §6 Chosen **[M]**（還沒試驗）；存放位置、匯出檔、備份 **[M]**；§10 第 1 條 **[M]**。
- **Fabricated assumptions（推測但 input 未明說）：**
  - Godot 4 可以透過外掛（例如 godot-sqlite）使用 SQLite，是 Claude 依一般資料判斷，還沒在 Owner 的電腦上試過。
  - 存放位置 `%APPDATA%\學習精靈\` 是 Claude 提議的一般做法，Owner 沒有特別指定。
  - 匯出的 CSV 只放作答紀錄（data-model AnswerRecord 的欄位），不放暱稱和玩家代號；Avi 從「誰傳來的」就知道是誰（Claude 提議，見 AC-14）。
  - 同學願意把匯出檔傳給 Avi（階段 0、concierge 時同學願意交表單，所以推測願意）。
- **Highest-value next input:** ADR-001 小試驗第 4 項的結果。

### TODO（缺資料）

- _TODO: 需要 ADR-001 小試驗第 4 項的結果，才能改成 Accepted_
- _TODO: 匯出檔用什麼方式傳給 Avi（Email、Line、雲端硬碟），試用前決定_
- _TODO: 資料表版本怎麼記（`user_version`），開發時確認_
- _TODO: 作答紀錄保留期限（data-model §12）_
