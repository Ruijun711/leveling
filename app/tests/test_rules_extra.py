"""第三批新增的規則：reminder_due（醒來後補跳提醒）、pick_question（出題順序 2A）。

不在 unit-test-stage1.md 的 38 條裡，編號用 X 開頭。
"""
import random
from datetime import timedelta

from conftest import Q1, Q2, Q3, T
from leveling.rules import pick_question, reminder_due

H = timedelta(hours=1)


def test_x01_not_due_one_minute_before_24h():
    assert reminder_due(T + 24 * H - timedelta(minutes=1), T, []) is False


def test_x02_due_at_24h():
    assert reminder_due(T + 24 * H, T, []) is True


def test_x03_normal_schedule_24_36_48():
    shown = []
    for hours in (24, 36, 48):
        assert reminder_due(T + hours * H, T, shown) is True
        shown.append(T + hours * H)
        assert reminder_due(T + hours * H + timedelta(minutes=1), T, shown) is False


def test_x04_after_sleeping_3_days_only_one_catch_up_then_every_12h():
    wake = T + 100 * H
    shown = []
    assert reminder_due(wake, T, shown) is True
    shown.append(wake)
    # 醒來後馬上又檢查：預定時間 T+36h 早就過了，但和上一則還不到 12 小時
    assert reminder_due(wake + timedelta(minutes=1), T, shown) is False
    assert reminder_due(wake + 12 * H, T, shown) is True


def test_x05_simulated_week_never_more_than_2_in_24h():
    # 每 10 分鐘檢查一次，中間有一段 50 小時「電腦睡著」不檢查
    shown, t = [], T
    while t < T + 7 * 24 * H:
        asleep = T + 30 * H <= t < T + 80 * H
        if not asleep and reminder_due(t, T, shown):
            shown.append(t)
        t += timedelta(minutes=10)
    for s in shown:
        assert len([x for x in shown if s <= x < s + 24 * H]) <= 2


def test_x06_answer_resets_reminders():
    shown = [T + 24 * H, T + 36 * H]
    last = T + 40 * H
    assert reminder_due(T + 50 * H, last, shown) is False
    assert reminder_due(last + 24 * H, last, shown) is True


def test_x07_pick_unanswered_first():
    rng = random.Random(0)
    for _ in range(50):
        assert pick_question([Q1, Q2, Q3], {"Q013", "Q014"}, rng) is Q3


def test_x08_all_answered_picks_from_all():
    rng = random.Random(0)
    picked = {pick_question([Q1, Q2, Q3], {"Q013", "Q014", "Q015"}, rng).id for _ in range(100)}
    assert picked == {"Q013", "Q014", "Q015"}


def test_x09_no_active_questions_returns_none():
    assert pick_question([], set(), random.Random(0)) is None
