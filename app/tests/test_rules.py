"""T1 level_from_xp、T2 xp_for_answer、T4 next_reminder_at、T5 count_reminders_since、T6 needs_download。

每個測試名稱前面的 tcNNN 對應 04-測試/unit-test-stage1.md 的 TC 編號。
"""
from datetime import timedelta

import pytest

from conftest import T
from leveling.rules import (
    count_reminders_since,
    level_from_xp,
    needs_download,
    next_reminder_at,
    xp_for_answer,
)

H = timedelta(hours=1)


# ---------- T1 level_from_xp ----------

def test_tc001_new_player_is_level_1():
    assert level_from_xp(0) == 1


def test_tc002_one_point_before_level_up():
    assert level_from_xp(19) == 1


def test_tc003_exactly_20_is_level_2():
    assert level_from_xp(20) == 2


def test_tc004_exactly_160_is_level_9():
    assert level_from_xp(160) == 9


@pytest.mark.parametrize("xp", [170, 180, 1000])
def test_tc005_never_above_level_9(xp):
    assert level_from_xp(xp) == 9


def test_tc006_negative_xp_raises():
    with pytest.raises(ValueError):
        level_from_xp(-10)


# ---------- T2 xp_for_answer ----------

def test_tc007_correct_first_attempt_gives_10():
    assert xp_for_answer(is_correct=True, is_first_attempt=True) == 10


def test_tc008_correct_but_not_first_attempt_gives_0():
    assert xp_for_answer(is_correct=True, is_first_attempt=False) == 0


def test_tc009_wrong_first_attempt_gives_0():
    assert xp_for_answer(is_correct=False, is_first_attempt=True) == 0


# ---------- T4 next_reminder_at ----------

def test_tc019_first_reminder_after_24h():
    assert next_reminder_at(T, 0) == T + 24 * H


def test_tc020_second_reminder_12h_later():
    assert next_reminder_at(T, 1) == T + 36 * H


def test_tc021_third_reminder_exactly_24h_after_first_is_allowed():
    assert next_reminder_at(T, 2) == T + 48 * H


def test_tc022_never_more_than_2_in_any_24h_window():
    times = [next_reminder_at(T, n) for n in range(10)]
    # 任選一個起點 t：用每一則提醒的時間當起點，再加上前後各偏一點
    starts = [t + d for t in times for d in (-1 * H, timedelta(0), timedelta(minutes=1))]
    for start in starts:
        in_window = [x for x in times if start <= x < start + 24 * H]
        assert len(in_window) <= 2, f"{start} 起的 24 小時內有 {len(in_window)} 則"


def test_tc023_uses_scheduled_time_not_actual_shown_time():
    # 第一則實際在 T+24h10m 才跳出，但第二則仍以預定時間算
    assert next_reminder_at(T, 1) == T + 36 * H


def test_tc024_negative_count_raises():
    with pytest.raises(ValueError):
        next_reminder_at(T, -1)


def test_tc038_never_answered_counts_from_first_open():
    C = T - 100 * H  # 第一次開啟時間（PlayerProgress.created_at）
    assert next_reminder_at(C, 0) == C + 24 * H
    assert next_reminder_at(C, 1) == C + 36 * H


# ---------- T5 count_reminders_since ----------

def test_tc025_counts_reminders_after_last_answer():
    assert count_reminders_since([T + 24 * H, T + 36 * H], T) == 2


def test_tc026_answering_again_resets_count():
    last = T + 40 * H
    n = count_reminders_since([T + 24 * H, T + 36 * H], last)
    assert n == 0
    assert next_reminder_at(last, n) == T + 64 * H


def test_tc027_reminder_at_same_instant_as_answer_not_counted():
    assert count_reminders_since([T + 24 * H], T + 24 * H) == 0


# ---------- T6 needs_download ----------

def test_tc028_newer_remote_needs_download():
    assert needs_download(remote_version=3, local_version=2) is True


def test_tc029_same_version_no_download():
    assert needs_download(remote_version=3, local_version=3) is False


def test_tc030_older_remote_no_download():
    assert needs_download(remote_version=2, local_version=3) is False
