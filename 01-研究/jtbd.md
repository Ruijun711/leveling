---
doc_type: "jtbd"
variant: "light"
status: "draft"
owner: "Avi"
last_updated: "2026-11-07"
upstream:
  required: ["persona", "user-research"]
  optional: ["competitive-scan"]
---

# Jobs To Be Done: 學習精靈

**Status:** Draft v0.2 · **Owner:** Avi · **Last updated:** 2026-11-07

> [!NOTE]
> 證據來源：`responses.csv`（4 份問卷 R1–R4，全部是 aipe05 學員）與 `persona.md` v0.4。沒有訪談逐字稿。R1 屬於 P2，R2、R3、R4 屬於 P1。

---

## 1. Executive Summary

- 從 4 份問卷整理出 **5 個 JTBD**，依**提到人數**排序（Owner 決定 2026-11-05）。（依據：progress.md JTBD 摘要）
- 最常見的需求是**看到自己的進步**，4 人都提到；這也是唯一標 [M] 的 JTBD。（依據：responses.csv 第 9 題）**[M]**
- 痛點主要有兩類：**上課內容太多、吸收不來**（JTBD-002），以及**卡住後找不到自己錯在哪**（JTBD-003）。這兩類都和「課後練習漸漸停止」有關。（依據：responses.csv 第 7、8 題）**[L]**
- P0 為 JTBD-001～003（提到人數 ≥ 2 人，Owner 確認 2026-11-05）。成功標準由 Owner 提供（2026-11-07）：JTBD-001、003 已訂；JTBD-002 在 v1 不做（`prd.md` 列為 Non-Goal），先保留 TODO。
- 最強的證據來源是第 9 題（4 人一致）；其餘都只有 1–2 人提到。

> **TL;DR:** 程式新手最想完成的任務是：在課後練習中**確認自己真的有在進步**，並且在內容太多或卡住時**還能繼續往下練**。**[L]**

---

## 2. JTBD Statements

| ID | 優先級 | Statement | Functional job | Persona | 提到人數 | Confidence | Source |
|---|---|---|---|---|---|---|---|
| JTBD-001 | P0 | When 練習了一段時間、卻不確定自己有沒有變強時, I want to 清楚看到自己累積了多少、進步到哪裡, so I can 有動力繼續練下去 | 確認自己的學習進度 | P1、P2 | 4 人 | **[M]** | responses.csv 第 9 題全員選「看得到自己的進步」；R2 第 11 題（quote: "有一步一步進步的感覺"）；R3 第 11 題（quote: "因為能有一個指標看得到自己的進步"） |
| JTBD-002 | P0 | When 上課一次接收太多內容、聽不懂或跟不上時, I want to 把內容分成自己吸收得了的份量、一點一點練熟, so I can 不會練完就忘，也跟得上課程 | 消化並記住上課內容 | P1 | 2 人 | **[L]** | R2 第 8 題（quote: "一次資訊太多吸收不來或者練完就忘記"）；R4 第 7 題（quote: "老師講解後還是聽不懂、打字也跟不上"）；另見 R3 第 12 題（quote: "光是消化教材就很需要時間"） |
| JTBD-003 | P0 | When 程式出錯，對照解答或問 AI 之後還是找不到問題時, I want to 弄清楚自己的邏輯在哪一步出錯, so I can 修正後繼續往下練，而不是卡住就停下 | 找出並理解自己的錯誤 | P1、P2 | 2 人 | **[L]** | R1 第 8 題（quote: "有錯，但對照解答後依然找不到錯在哪。"）；R3 第 8 題（quote: "包括問ai也好，自己的邏輯卡在哪裡?尤其那些很陌生的語法時"） |
| JTBD-004 | — | When 剛開課面對大量陌生的技術內容時, I want to 知道哪些一定要會、下一步該先練什麼, so I can 把有限的時間花在重點上，而不是因為不確定就先放下 | 決定練習的重點與順序 | P1 | 1 人 | **[L]** | R3 第 7 題（quote: "當時剛開課我就在想是否都要會?……就先暫時放下"）；R3 第 8 題（quote: "我不知道在做什麼?"） |
| JTBD-005 | — | When 時間被其他事情擠壓時, I want to 讓練習的時間直接幫助到我正在做的作品, so I can 不必在練習和作品之間二選一 | 讓練習成果用在自己的作品上 | P2 | 1 人 | **[L]** | R1 第 7 題（quote: "時間不夠了，先完成別的事。"）；R1 第 9 題選「練習內容和自己想做的作品有關」；R1 第 11 題（quote: "要看得到的東西與我在做的東西的關聯性和幫助程度"） |

---

## 5. Current Solution & Success Criteria

> 只列 P0（JTBD-001～003）。成功標準由 Owner 提供（Owner 決定 2026-11-05）。

### JTBD-001 · 看到自己的進步

- **Current solution:** 問卷沒有直接問「現在怎麼確認自己的進步」。已知 3 人沒用過 streak、badge、level 這類工具（R2、R3、R4 第 12 題）；1 人用過，但已經不用了（R1 第 12 題）。4 人過去兩週課外主動練習都是 0 次，所以課外幾乎沒有能累積的進度。（依據：responses.csv 第 3、12 題）**[L]**
- **Gap:** 用過的那位認為進度要自己設定、自己勾選，沒有可信度。（quote: "要自己製作任務再自己點選"已完成"甚至要自己選擇獎勵幅度，覺得在坑自己。"——R1 第 12 題）**[L]**
- **Success criteria:** 使用者在 **2 週**內，每週至少練習 1 次的比例 **≥ 50%**（Owner 決定 2026-11-07；與 `prd.md` G1 相同）
- **Source:** responses.csv 第 3、9、11、12 題

### JTBD-002 · 消化上課內容

- **Current solution:** 卡住時問 AI、上網搜尋、問同學或老師、直接看解答。（依據：R2、R4 第 5 題）**[L]**
- **Gap:** 兩人都是卡 10 分鐘內就想放棄（R2、R4 第 6 題）；R4 到現在還是搞不懂基本語法規則。（quote: "搞不懂什麼時候要換行，哪幾行要對齊"——R4 第 8 題）**[L]**
- **Success criteria:** _TODO: 待 Owner 提供（Owner 決定先保留 2026-11-07；v1 不做，`prd.md` 列為 Non-Goal）_
- **Source:** responses.csv R2、R4 第 5–8 題

### JTBD-003 · 找出自己的錯

- **Current solution:** 對照解答、問 AI、上網搜尋。R3 會先整理自己要做什麼再問 AI。（依據：R1、R3 第 5 題）**[L]**
- **Gap:** 對照解答還是找不到錯（R1 第 8 題）；問 AI 也還是不知道自己的邏輯卡在哪（R3 第 8 題）。現有方法給的是正確答案，但說不出「你錯在哪」。**[L]**
- **Success criteria:** 答錯並看完說明後，再做同一個觀念的題目，答對率 **≥ 60%**（Owner 決定 2026-11-07；與 `prd.md` G2 相同）
- **Source:** responses.csv R1、R3 第 5、8 題

---

## 10. Decision Log

| Date | Decision | Options | Chosen | Rejected why |
|---|---|---|---|---|
| 2026-11-05 | JTBD 用哪個維度排序（**Owner 決定**） | by_frequency（提到人數）/ by_pain_severity / by_strategic_fit | by_frequency | by_pain_severity：需要主觀判斷，目前資料不足以比較嚴重度；by_strategic_fit：容易只挑出支持現有設計（經驗值、升級、Boss）的需求 |
| 2026-11-05 | P0 範圍（**Owner 確認**） | 001～003（提到 ≥ 2 人）/ 只留 001 / 001 + 003 | 001～003 | 只留 001：會漏掉 2 人提到的痛點；001 + 003：沒有理由排除提到人數相同的 002 |
| 2026-11-05 | P0 成功標準由誰撰寫（**Owner 決定**） | Owner 提供 / Claude 依問卷提案 | Owner 提供 | Claude 提案：Owner 選擇自己提供 |
| 2026-11-07 | P0 成功標準（**Owner 決定** 11A、12C、13A，從 Claude 列的選項中選定） | 行為指標 / 自評分數 / 兩者都要；JTBD-002 另有「先留 TODO」 | 001、003 用行為指標；002 先留 TODO | 自評分數：問卷顯示「說的」興趣不等於「做的」行為（給 5 分、練習 0 次）；002 現在訂：v1 不做 |

---

## 12. Confidence & Sources & TODO

- **整份文件最低 confidence 欄位：** 只有 JTBD-001 標 **[M]**（4 人一致）；JTBD-002～005 與第 5 章所有欄位都是 **[L]**。
- **Fabricated assumptions（推測但 input 未明說）：**
  - **各條「so I can」的預期結果**有一部分是推論。例如 JTBD-001 的「有動力繼續練下去」是從第 9 題題目「什麼會讓你更願意繼續練習」推得的，受訪者沒有用自己的話說出來。
  - R2 第 7 題只寫了「累了」。把 R2 歸進 JTBD-002（內容吸收不來），依據的是 R2 第 8 題；「累」和「吸收不來」之間的因果關係是推測。
  - JTBD-001 的 4 人裡包含 R1（P2），但 R1 對遊戲化只給 2 分。R1 想要的「進步」可能是指和自己作品的關聯，不一定和 P1 相同。
- **Highest-value next input:** 追問 P1 新手（R2、R3、R4）：「你現在怎麼判斷自己有沒有進步？」「做到什麼程度你會覺得『這個問題解決了』？」這能補 JTBD-001 的 current solution，也能協助 Owner 訂成功標準。

### TODO（缺資料）

- _TODO: JTBD-002 的成功標準，待 Owner 提供（v1 不做，`prd.md` 列為 Non-Goal）_
- _TODO: 需要追問訪談，才能確認使用者的情緒任務（例如「想對自己更有自信」，brief §期望成果有提到，但問卷沒有直接證據）_
- _TODO: 需要問卷或訪談資料，才能寫 JTBD-001 的 current solution（問卷沒有直接詢問）_
