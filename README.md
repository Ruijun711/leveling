# 學習精靈

用遊戲的方式陪程式新手做課後練習：答對得到經驗值、升級，精靈角色會在桌面上提醒你回來練習。

- **給誰用：** 對寫程式有興趣、想學習，但課後練習難以持續的新手（第一批是 aipe05 課程學員）
- **平台：** Windows 桌面程式（Python + PySide6）
- **目前進度：** 階段 1「核心循環」開發完成（v0.1.0），準備找同學試用

---

## 階段 1 做了什麼

| 功能 | 說明 |
|---|---|
| 選擇題練習 | 從題庫出 Python 基礎語法選擇題；先出還沒做過的，全部做過後才重複 |
| 經驗值和升級 | 第一次作答答對 +10 點，20 點升一級，目前最高 9 級；送出後馬上更新 |
| 答錯說明 | 顯示這題考的觀念、正確答案和說明 |
| 桌面提醒 | 超過 1 天沒練習，精靈出現在桌面右下角提醒；之後每 12 小時一次，任何 24 小時內最多 2 則 |
| 精靈角色 | 答對開心、答錯難過、升級冒星星 |
| 自動下載新題目 | 開機時和之後每 24 小時，從 [題庫 repo](https://github.com/Ruijun711/leveling-question-bank) 下載；沒網路照常用本機題庫 |
| 匯出作答紀錄 | 匯出 CSV，由使用者自己決定要不要交出；程式不會上傳任何作答資料 |
| 系統匣 | 按視窗的 X 會縮到右下角系統匣，程式繼續跑才收得到提醒；右鍵「結束」才會關掉 |
| 開機自動執行 | 打包後的版本第一次執行時開啟；系統匣右鍵可以取消勾選 |
| 只能開一個 | 再打開一次只會把原本的視窗叫出來，提醒不會重複 |

---

## 給同學：怎麼安裝

拿到 `學習精靈-版本.zip` 後，解壓縮、雙擊 `學習精靈.exe`。不用另外裝 Python。詳細步驟（包含 Windows 跳出「已保護您的電腦」時怎麼辦）寫在壓縮檔裡的 `使用說明.txt`。

---

## 開發：怎麼執行

需要 Windows 和 Python 3.12。

```powershell
cd app
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

- 資料存在 `%APPDATA%\學習精靈\leveling.db`（SQLite）。
- **鍵盤操作：** 1～4 或 A～D 選答案，Enter 送出，再按 Enter 下一題。

### 開發用的環境變數

| 變數 | 作用 |
|---|---|
| `LEVELING_DATA_DIR` | 資料改放在別的資料夾，不會弄亂正式資料 |
| `LEVELING_REMINDER_TEST=1` | 提醒的 24 小時改成 2 分鐘、12 小時改成 1 分鐘，方便測試 |
| `LEVELING_OFFLINE=1` | 不下載題庫，模擬沒網路 |

例如在 PowerShell：

```powershell
$env:LEVELING_REMINDER_TEST="1"; $env:LEVELING_DATA_DIR="$env:TEMP\學習精靈測試"
.venv\Scripts\python main.py
```

### 跑測試

```powershell
cd app
.venv\Scripts\python -m pytest
```

目前 86 個測試：`04-測試/unit-test-stage1.md` 的 38 條規則，加上 SQLite 存檔、題庫下載、匯出、開機自動執行、只能開一個的測試。

### 打包成壓縮檔

```powershell
cd app
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

會先跑測試（沒過就停），再用 PyInstaller 打包，產生 `app\dist\學習精靈-版本.zip`（約 40 MB）。版本號在 `app/leveling/__init__.py`，每次發新版給同學前加 1。

---

## 資料夾

| 位置 | 內容 |
|---|---|
| `app/` | 階段 1 程式 |
| `app/leveling/` | `rules.py` 經驗值、等級、提醒規則；`bank.py` 題庫格式和檢查；`progress.py` 送出答案；`storage.py` SQLite；`bank_sync.py` 下載題庫；`export.py` 匯出 CSV；`messages.py` 畫面文字；`autostart.py` 開機自動執行；`single_instance.py` 只能開一個；`ui/` 畫面、提醒和精靈 |
| `app/data/` | 程式附的基本題庫（題庫 repo 第 1 版，17 題） |
| `app/tests/` | pytest |
| `app/build.ps1`、`app/tools/`、`app/packaging/` | 打包指令、產生圖示、給同學的使用說明 |
| `01-研究/` | 專案簡報、使用者輪廓、JTBD、價值假設，以及問卷和測試資料 |
| `02-產品/` | PRD、分階段規劃、驗收條件、非功能需求 |
| `03-架構/` | C4 架構圖、雲端資料介面、資料模型、ADR（架構決策紀錄） |
| `04-測試/` | 階段 1 單元測試計畫 |
| `05-階段0-未使用/` | 已跳過的階段 0 資料，保留參考 |
| `spike/` | 選框架前的小試驗（PySide6、Godot） |
| `工作包/` | 寫各份文件時用的範本 |
| `progress.md` | 專案進度和所有決定的紀錄（從這裡開始看） |

---

## 分階段規劃

| 階段 | 內容 | 狀態 |
|---|---|---|
| 1 核心循環 | 選擇題、經驗值、升級、答錯說明、提醒、下載題庫 | 開發完成，待試用 |
| 2 角色成長 | 選職業、技能點數、學技能、外觀變化 | 規劃中 |
| 3 Boss 戰 | Boss 出現在桌面上即時戰鬥、寶物；同學互看等級 | 規劃中 |
| 4 AI 精靈 | 用 AI 針對玩家的答案解釋錯在哪、鼓勵玩家 | 規劃中 |
| 5 寫程式題 | 程式填空、自動執行批改 | 規劃中 |

每個階段做完都會找同學試用 1～2 週，用數字決定要不要往下做。詳見 `02-產品/roadmap.md`。

---

## 隱私

- 階段 1～3 的作答資料（選的答案、對錯、作答紀錄）只存在使用者自己的電腦，程式只連到 GitHub 下載題庫。
- 作答紀錄只有使用者自己按「匯出」才會離開電腦，匯出檔不含暱稱。
- 研究資料裡的問卷是匿名的；測試資料只有暱稱。
