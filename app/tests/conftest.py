"""測試共用的資料：題庫 repo 第 1 版的 Q013～Q017（acceptance-criteria.md「測試資料」）。

acceptance-criteria 稱呼的「第 1 題」～「第 5 題」就是 Q013～Q017。
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

# 讓測試找得到 app/leveling（不用安裝成套件）
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from leveling.bank import Question  # noqa: E402

UTC = timezone.utc
T = datetime(2026, 11, 9, 1, 0, tzinfo=UTC)  # 固定的「最後作答時間」，時間一律用 UTC


def _q(id, concept, code, choices, answer, explanation):
    return Question(
        id=id,
        concept=concept,
        type="multiple_choice",
        code=code,
        prompt="這段程式會印出什麼？",
        choices=tuple(choices),
        answer=answer,
        explanation=explanation,
        status="active",
        added_in_version=1,
    )


Q1 = _q("Q013", "字串與數字", 'x = "5"\ny = 2\nprint(x * y)',
        ["10", "55", "7", "會出現錯誤"], "55",
        'x 是字串 "5"，字串乘以 2 是重複兩次，不是數學相乘。')
Q2 = _q("Q014", "縮排", 'for i in range(3):\n    print("A")\nprint("B")',
        ["印出 A、A、A，最後印出 1 次 B", "A 和 B 交替印 3 次", "印出 A、A、A、B、B、B", "只印出 B"],
        "印出 A、A、A，最後印出 1 次 B",
        'print("B") 沒有縮排，不在迴圈裡，所以迴圈跑完才印 1 次。')
Q3 = _q("Q015", "if/elif",
        'score = 85\nif score >= 60:\n    print("及格")\nelif score >= 80:\n    print("良好")\nelse:\n    print("不及格")',
        ["及格", "良好", "及格 和 良好 都會印出", "不及格"], "及格",
        "85 ≥ 60 先成立，後面的 elif 就不會再檢查。")
Q4 = _q("Q016", "range 和 for", "print(list(range(1, 5)))",
        ["[1, 2, 3, 4, 5]", "[0, 1, 2, 3, 4]", "[1, 2, 3, 4]", "[2, 3, 4, 5]"], "[1, 2, 3, 4]",
        "range(1, 5) 包含 1、不包含 5。")
Q5 = _q("Q017", "list 索引", "nums = [10, 20, 30]\nnums.append(40)\nprint(nums[1] + nums[-1])",
        ["50", "60", "70", "會出現錯誤"], "60",
        "nums[1] 是 20，append 後 nums[-1] 是 40，加起來 60。")


@pytest.fixture
def now():
    return T
