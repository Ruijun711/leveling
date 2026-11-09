"""畫面上的文字集中放這裡，要改字只改這個檔案。

提醒文字：Owner 決定 2026-11-09（2B 輪流）；錯誤訊息：Owner 決定 2026-11-09（3A，照 Claude 草稿）。
"""

REMINDER_TEXTS = (
    "好久不見！做一題就有 10 點經驗值，要不要來一題？",
    "已經一天沒練習囉，花 1 分鐘做一題吧！",
    "你的角色在等你升級，回來做一題吧！",
)


def reminder_text(shown_count: int) -> str:
    """第幾則提醒（從 0 算，用所有提醒紀錄的筆數）就用第幾句，3 句輪流。"""
    return REMINDER_TEXTS[shown_count % len(REMINDER_TEXTS)]


# AC-7
NO_CHOICE = "請先選一個答案"


def invalid_choice(question_id: str) -> str:
    return f"這題資料有問題（題號 {question_id}），請按下一題，並告訴 Avi。"


# AC-10
SAVE_FAILED = "進度沒有存到，請再按一次送出。你的答案還在。"

# api-spec §5（角落小字，不跳視窗）
STATUS_OFFLINE = "離線中，使用本機題庫"
STATUS_DOWNLOAD_FAILED = "新題目這次沒下載到，下次會再試"
BANK_INVALID = "雲端題庫有問題，先用本機題庫練習。請告訴 Avi。"
# 下面兩句是 Claude 補的（成功時的角落小字），Owner 可以改
STATUS_UP_TO_DATE = "題庫已是最新"


def status_updated(count: int) -> str:
    return f"下載到新題目，現在共 {count} 題"
