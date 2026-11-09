"""經驗值、等級、提醒、題庫下載的規則（純函式，不讀系統時間，方便測試）。

依據：prd.md FR-2、FR-6；acceptance-criteria.md AC-1～AC-4、AC-8、AC-11；api-spec.md §2。
規則數字是暫定（Owner 2026-11-05），要改只改這裡的常數。
"""
from datetime import datetime, timedelta

XP_PER_CORRECT = 10        # 選擇題第一次作答答對得到的經驗值
XP_PER_LEVEL = 20          # 幾點升一級
MAX_LEVEL = 9              # v1 等級上限
FIRST_REMINDER_AFTER = timedelta(hours=24)  # 最後作答後多久第一次提醒
REMINDER_INTERVAL = timedelta(hours=12)     # 之後每隔多久提醒一次


def level_from_xp(xp: int) -> int:
    """等級 = min(9, 1 + INT(xp / 20))；等級不另外存，一律從經驗值算。"""
    if xp < 0:
        raise ValueError(f"經驗值不能是負數：{xp}")
    return min(MAX_LEVEL, 1 + xp // XP_PER_LEVEL)


def xp_for_answer(is_correct: bool, is_first_attempt: bool) -> int:
    """選擇題只有第一次作答答對才得分。"""
    return XP_PER_CORRECT if (is_correct and is_first_attempt) else 0


def next_reminder_at(last_answered_at: datetime, reminders_since_last_answer: int) -> datetime:
    """下一則提醒的預定時間：T+24h、T+36h、T+48h……

    還沒作答過時，last_answered_at 傳第一次開啟的時間（AC-4）。
    用預定時間算，不用實際跳出的時間，所以晚跳的提醒不會讓後面整個延後（TC-023）。
    每 12 小時一則，任何 [t, t+24h) 之內最多 2 則（AC-4）。
    """
    if reminders_since_last_answer < 0:
        raise ValueError(f"提醒次數不能是負數：{reminders_since_last_answer}")
    return last_answered_at + FIRST_REMINDER_AFTER + reminders_since_last_answer * REMINDER_INTERVAL


def count_reminders_since(shown_at: list[datetime], last_answered_at: datetime) -> int:
    """最後一次作答之後跳過幾則提醒；和作答同一刻的提醒不算（TC-027）。"""
    return sum(1 for t in shown_at if t > last_answered_at)


def needs_download(remote_version: int, local_version: int) -> bool:
    """雲端版本比本機大才下載；雲端比較舊（例如 GitHub 快取）時不換（TC-030）。"""
    return remote_version > local_version
