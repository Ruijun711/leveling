"""匯出作答紀錄成 CSV（AC-14；ADR-002 3A）。

- 第一列是欄位名稱；不含暱稱和玩家代號（NFR S2）。
- 用 UTF-8 加 BOM，Excel 直接打開中文不會亂碼。
- 時間換成使用者電腦的時區顯示（data-model：存 UTC、顯示時再換）。
- 程式不會自動上傳或寄出這個檔案。
"""
import csv
from datetime import datetime
from pathlib import Path

COLUMNS = (
    "作答時間",
    "題號",
    "觀念",
    "選的答案",
    "對或錯",
    "是不是第一次作答",
    "得到的經驗值",
    "從送出到畫面更新的毫秒數",
)


def export_csv(store, path: str | Path) -> int:
    """寫出 CSV，回傳寫了幾筆作答紀錄。"""
    rows = store.export_rows()
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        for r in rows:
            w.writerow((
                datetime.fromisoformat(r["answered_at"]).astimezone().isoformat(timespec="seconds"),
                r["question_id"],
                r["concept"],
                r["selected_choice"],
                "對" if r["is_correct"] else "錯",
                "是" if r["is_first_attempt"] else "否",
                r["xp_gained"],
                "" if r["update_ms"] is None else r["update_ms"],
            ))
    return len(rows)
