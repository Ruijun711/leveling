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

# ADR-001: 階段 1 桌面程式要用哪個語言和框架

**Status:** Proposed · **Owner:** Avi · **Last updated:** 2026-11-08

> [!NOTE]
> 依據：`prd.md` v0.6（§6 NFR Platform、Latency；FR-5；§9 R2）、`roadmap.md` v0.1（階段 1、3、5）、`acceptance-criteria.md` v0.1（AC-1、AC-4、AC-9、AC-10）、`project-brief.md`（§主要約束）。範圍、Owner 技能、作業系統、是否考慮階段 3 由 Owner 決定（2026-11-07：1A 2B 3C 4A）；先做小試驗再決定由 Owner 決定（2026-11-07：1A、2 可以）。
>
> 這份 ADR 是**單一決策**：只決定桌面程式的語言和框架。本機存資料的方式、AI 服務、批改程式碼的方式、同學互看等級的伺服器，之後各自另寫 ADR。

---

## 1. Context

- `roadmap.md` 階段 1 要做一個 Windows 桌面程式：從題庫出選擇題、自動判斷對錯、3 秒內更新經驗值和等級、答錯顯示說明、超過 1 天沒練習時在桌面提醒、開機自動執行。（依據：roadmap §2 階段 1；acceptance-criteria AC-1～AC-10）
- 開始寫程式前要先選語言和框架。之後換框架等於整個重寫，所以這是很難回頭的決定。
- 這個選擇要顧到**階段 3**：Boss 出現在電腦桌面上，和玩家的角色即時戰鬥，要有動畫。（依據：Owner 決定 4A；prd FR-5）
- 約束：Owner 會 Python 和一點 HTML／JavaScript（2B），brief 提到寫程式還不是很強；目前只考慮 Windows，同學用什麼作業系統還不知道（3C）。（依據：brief §主要約束；prd §9 R2）

> **TL;DR:** 階段 1 要開始寫程式，得先選一個 Owner 學得會、又能做到階段 3 桌面 Boss 戰的框架；A（PySide6）和 B（Godot）各有優勢，先各做一個小試驗再決定。

---

## 2. Decision Drivers

| Driver | Weight | Why this matters |
|---|---|---|
| 好不好學 | High | Owner 會 Python、只會一點 HTML／JavaScript，寫程式還不是很強（依據：Owner 2B；brief §主要約束） |
| 做不做得出階段 3：Boss 出現在桌面上、即時戰鬥動畫 | High | 框架做不到的話，到階段 3 要整個重寫（依據：Owner 4A；prd FR-5） |
| 能不能做出 Windows 安裝程式，開機自動執行、在桌面跳出提醒 | High | prd §6 Platform；acceptance-criteria AC-4、AC-9 |
| 經驗值 3 秒內更新 | High | prd §6 Latency；AC-1、AC-2 |
| 方不方便執行並批改玩家寫的 Python 程式 | Medium | 階段 5 才需要（依據：roadmap §2 階段 5） |
| 費用 | Medium | 個人專案，最好免費 |
| 問 AI 和查資料方不方便 | Medium | brief 提到 Owner 會大量和 AI 討論 |

---

## 3. Options Considered

### Option A: Python + PySide6（Qt）

- **Pros:** 用 Owner 已經會的 Python；可以做透明、無邊框、永遠在最上層的視窗，讓 Boss 出現在桌面上；有系統匣，可以跳出提醒；階段 5 執行 Python 程式比較直接；網路資料多，問 AI 容易得到答案
- **Cons:** 不是遊戲引擎，即時戰鬥的動畫、碰撞、血條都要自己寫，階段 3 工作量大；要學 Qt 的視窗觀念；打包出來的安裝檔比較大
- **Cost:** 免費；一次性成本是學 Qt，階段 3 要多花時間寫動畫

### Option B: Godot 4（遊戲引擎，語言是 GDScript）

- **Pros:** 本來就是做遊戲的工具，角色動畫、即時戰鬥、技能特效比較好做；可以做透明、無邊框、永遠在最上層的視窗；GDScript 寫法很像 Python；匯出 Windows 程式簡單
- **Cons:** 要學新工具和新語言；階段 5 要執行玩家的 Python 程式，得另外呼叫 Python，比較麻煩；網路資料和 AI 的回答比 Python 少；做題目畫面這類表單式介面沒有 Qt 方便
- **Cost:** 免費、開源；一次性成本是學 Godot 和 GDScript

### Option C: Electron（HTML、CSS、JavaScript）

- **Pros:** 用 HTML 做畫面，介面最容易做漂亮；可以做透明、永遠在最上層的視窗；套件非常多
- **Cons:** Owner 的 JavaScript 只會一點，遊戲邏輯要用 JavaScript 寫；程式檔案大、佔記憶體；要多學 Node.js 和打包工具；執行 Python 程式也要另外處理
- **Cost:** 免費；一次性成本是學 JavaScript、Node.js 和打包工具

### Option D: 保持現狀（繼續用 Google 表單＋試算表）

- **Pros:** 已經做好，不用寫程式
- **Cons:** 做不到 3 秒內更新，也做不出桌面提醒和桌面 Boss 戰
- **Cost:** 免費；但 prd 已經排除，只用在階段 0（依據：Owner 決定 5A「v1 不能沿用 Google 表單＋試算表」）

---

## 6. Decision & Consequences

### Chosen: **暫定——先做小試驗，再從 Option A 和 Option B 選一個** · **[M]**

- **Scope:** 適用於學習精靈桌面程式（階段 1～5 的畫面、遊戲邏輯、桌面 Boss 戰）。不包含本機存資料的方式、AI 服務、批改程式碼的方式、同學互看等級的伺服器（之後另寫 ADR）。
- **小試驗：** A、B 各做一個最簡單的版本，內容是「出 1 題選擇題、答對加 10 點經驗值，再讓一張哥布林圖片出現在桌面上，並把經驗值存起來」，用以下 4 個標準比較：

  | # | 要試的事 | 判斷標準 |
  |---|---|---|
  | 1 | Boss 能不能出現在桌面上 | 哥布林圖片顯示在桌面上，背景透明、沒有視窗邊框、蓋在其他視窗上面，而且會移動 |
  | 2 | 經驗值能不能 3 秒內更新 | 從按下送出到畫面顯示新的經驗值，不超過 3 秒（依據：AC-1） |
  | 3 | 做到可以動要花多久 | 記錄 Owner 從開始到 1、2 都做到的時間；其中一個花的時間**不到另一個的一半**，才算明顯比較快（Owner 決定 2026-11-08，3A） |
  | 4 | 經驗值能不能存起來（ADR-002） | 把經驗值存進 SQLite，關掉程式重開，讀回來的經驗值是對的（依據：AC-9；adr-002 §6，Owner 決定 2026-11-08，2A） |

  - 兩個都過 1、2：其中一個花的時間不到另一個的一半，選它；沒差這麼多，就看 Owner 看不看得懂、改不改得動，再看階段 3（動畫）、階段 5（執行 Python）的已知代價（Owner 決定 2026-11-08，3A；程式主要由 Claude 寫，時間差主要反映 Claude 的速度）。
  - 只有一個過 1、2：選那一個。
  - 兩個都沒過：重新考慮 Option C，或調整階段 3 的設計。
  - 第 4 項不影響選 A 或 B，結果寫回 `adr-002-local-storage.md`（選定的框架做不到時，ADR-002 改用 JSON 檔）。
  - _TODO: 試驗結果出來後，把 Chosen 改成 A 或 B，Status 改成 Accepted，Confidence 改成 [H]_

- **試驗結果（2026-11-08）：** 程式由 Claude 寫、Avi 執行和檢查（Owner 決定 spike 3A）。

  | # | 判斷標準 | A：PySide6 6.12.0 | B：Godot |
  |---|---|---|---|
  | 1 | 哥布林出現在桌面（透明、無邊框、最上層、會移動） | ✅ 通過（Avi 確認） | _待試_ |
  | 2 | 送出到畫面更新 < 3 秒 | ✅ **9.9 毫秒** | _待試_ |
  | 3 | 做到可以動花多久 | 約 **15 分鐘**（15:50 開始安裝，16:06 Avi 全部確認完；中間含整理資料夾的時間） | _待試_ |
  | 4 | 經驗值存進 SQLite，重開後還在 | ✅ 通過（Python 內建 `sqlite3`） | _待試_ |
  | 加測 | Avi 自己改 `XP_PER_CORRECT` 10 → 20 | ✅ 看得懂、改得動 | _待試_ |

  程式：`spike/pyside6/main.py`（commit `2d05fb9`）。

- **Positive consequences:** 用實際做出來的結果決定，不用靠猜；如果 B 做得出來，階段 3 的動畫會比較好做；如果 A 做得出來，階段 5 執行 Python 程式比較直接。
- **Negative consequences（必填）:**
  - 階段 1 晚 1～2 天開始，而且有一個試驗版本會丟掉。
  - 試驗只做一張會動的圖片，看不出完整即時戰鬥（血條、技能、碰撞）的難度，階段 3 仍可能比預期難。
  - 不管選哪一個都有已知代價：選 A，階段 3 的動畫要自己寫；選 B，階段 5 要另外呼叫 Python 批改程式碼，而且做題目畫面比較麻煩。
- **Follow-up:**
  - 做小試驗，結果寫回本 ADR（§6、§10）。
  - 本機存資料已另寫 `adr-002-local-storage.md`（Proposed，2026-11-08）；小試驗第 4 項的結果寫回 ADR-002。
  - 同學用什麼作業系統，試用前先問（依據：Owner 3C）。

---

## 10. Decision Log

| Date | Decision | Options | Chosen | Rejected why | Confidence |
|---|---|---|---|---|---|
| 2026-11-07 | 桌面程式的語言和框架怎麼決定（**Owner 決定** 1A） | A PySide6 / B Godot / C Electron / D 保持現狀；決定方式：先做小試驗 / 現在直接選 | 先做 A、B 小試驗再決定 | C：Owner 的 JavaScript 只會一點，遊戲邏輯要用 JavaScript 寫，學習成本最高；D：做不到 3 秒內更新和桌面 Boss 戰，prd 已排除；「現在直接選」：A 好學、B 做遊戲容易，沒有哪一個明顯比較好 | **[M]** |
| 2026-11-08 | 小試驗加第 4 項「經驗值存進 SQLite、重開後讀回」（**Owner 決定** ADR-002 2A） | 加進小試驗 / 不加，ADR-002 直接定案 | 加進小試驗 | 不加：不確定 Godot 的 SQLite 外掛好不好用；第 4 項只用來確認 ADR-002，不影響選 A 或 B | **[H]** |
| 2026-11-08 | Godot 要不要也試（**Owner 決定** 1A） | A 照原計畫也試 Godot / B PySide6 已通過，直接選 | A | B：換框架等於重寫，很難回頭；Godot 的優勢在階段 3 的即時戰鬥動畫，PySide6 的走路哥布林看不出差別 | **[H]** |
| 2026-11-08 | 兩個都通過時怎麼比（**Owner 決定** 3A） | A 時間不到一半才算明顯快，否則看好不好懂、改不改得動 / B 差 30 分鐘以上 / C 不比時間 | A | B：程式主要由 Claude 寫，固定分鐘數主要反映 Claude 的速度；C：時間差很大時仍是有用的訊號 | **[H]** |
| 2026-11-07 | 小試驗的判斷標準（**Owner 同意** 2） | 桌面 Boss、3 秒內更新、花多久 / 另外加其他標準 | 這 3 項 | 其他標準（例如安裝檔大小、開機自動執行）A、B 都做得到，比較不出差別 | **[M]** |

---

## 12. Confidence & Sources & TODO

- **整份文件最低 confidence 欄位：** §6 Chosen **[M]**（還沒試驗）；§10 兩條 **[M]**。
- **Fabricated assumptions（推測但 input 未明說）：**
  - A、B、C 都做得到透明、無邊框、永遠在最上層的視窗，是 Claude 依各框架的一般功能判斷，還沒在 Owner 的電腦上試過。
  - 「開機自動執行、跳出提醒、打包安裝檔」A、B、C 都做得到，所以沒有放進試驗標準。
  - 同學用 Windows（Owner 3C 先以 Windows 為準，還沒確認）。
  - 費用都是免費，是依各框架目前的授權；PySide6 是 LGPL 授權，個人專案免費。
- **Highest-value next input:** 小試驗（spike）的結果。

### TODO（缺資料）

- _TODO: PySide6 已試完（4 項通過）；需要 Godot 的結果，才能把 Chosen 改成 A 或 B_
- ~~試驗時間差多少才算「明顯比較快」~~ → 不到另一個的一半（Owner 決定 2026-11-08，3A）
- _TODO: 需要確認同學用什麼作業系統（試用前問）_
