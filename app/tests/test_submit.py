"""T3 submit_answer（store 用假的記憶體版本）。

tcNNN 對應 04-測試/unit-test-stage1.md。題目 Q1～Q5 是 acceptance-criteria 的「第 1～5 題」（Q013～Q017）。
"""
import pytest

from conftest import Q1, Q2, Q3, Q4, Q5
from fakes import InMemoryStore
from leveling.progress import (
    AnswerRecord,
    InvalidChoiceError,
    NoChoiceError,
    SaveError,
    submit_answer,
)


def _wrong(q):
    return next(c for c in q.choices if c != q.answer)


def test_tc010_first_correct_answer(now):
    store = InMemoryStore(xp=0)
    r = submit_answer(store, Q1, "55", now)

    assert (r.is_correct, r.is_first_attempt, r.xp_gained) == (True, True, 10)
    assert (r.total_xp, r.level, r.leveled_up) == (10, 1, False)
    assert len(store.records) == 1
    rec = store.records[0]
    assert rec == AnswerRecord(
        question_id="Q013",
        concept="字串與數字",
        answered_at=now,
        selected_choice="55",
        is_correct=True,
        is_first_attempt=True,
        xp_gained=10,
    )


def test_tc011_level_up_at_20(now):
    store = InMemoryStore(xp=10)
    r = submit_answer(store, Q3, Q3.answer, now)
    assert (r.total_xp, r.level, r.leveled_up) == (20, 2, True)


def test_tc012_level_9_cap_keeps_adding_xp(now):
    store = InMemoryStore(xp=160)
    r = submit_answer(store, Q5, Q5.answer, now)
    assert (r.total_xp, r.level, r.leveled_up) == (170, 9, False)


def test_tc013_repeated_question_correct_gives_no_xp(now):
    store = InMemoryStore(xp=10)
    submit_answer(store, Q4, _wrong(Q4), now)  # 第一次答錯
    r = submit_answer(store, Q4, Q4.answer, now)

    assert (r.is_correct, r.is_first_attempt, r.xp_gained, r.total_xp) == (True, False, 0, 10)
    assert len(store.records) == 2
    assert store.records[-1].is_first_attempt is False


def test_tc014_xp_always_equals_sum_of_records(now):
    store = InMemoryStore(xp=0)
    submit_answer(store, Q1, Q1.answer, now)
    submit_answer(store, Q2, _wrong(Q2), now)
    submit_answer(store, Q1, Q1.answer, now)
    r = submit_answer(store, Q3, Q3.answer, now)

    assert r.total_xp == 20
    assert store.xp == sum(rec.xp_gained for rec in store.records) == 20


@pytest.mark.parametrize("blank", [None, ""])
def test_tc015_blank_answer_rejected_and_keeps_first_attempt(now, blank):
    store = InMemoryStore(xp=0)
    with pytest.raises(NoChoiceError):
        submit_answer(store, Q2, blank, now)
    assert store.xp == 0 and store.records == []

    r = submit_answer(store, Q2, Q2.answer, now)
    assert r.is_first_attempt is True


def test_tc016_save_failure_changes_nothing(now):
    store = InMemoryStore(xp=0)
    store.fail_next_save = True
    with pytest.raises(SaveError):
        submit_answer(store, Q1, Q1.answer, now)
    assert store.xp == 0 and store.records == []


def test_tc017_resubmit_after_save_failure_is_still_first_attempt(now):
    store = InMemoryStore(xp=0)
    store.fail_next_save = True
    with pytest.raises(SaveError):
        submit_answer(store, Q1, Q1.answer, now)

    r = submit_answer(store, Q1, Q1.answer, now)
    assert (r.is_first_attempt, r.xp_gained, r.total_xp) == (True, 10, 10)


def test_tc018_choice_not_in_options_rejected_and_keeps_first_attempt(now):
    store = InMemoryStore(xp=0)
    with pytest.raises(InvalidChoiceError):
        submit_answer(store, Q1, "不存在的選項", now)
    assert store.xp == 0 and store.records == []

    r = submit_answer(store, Q1, Q1.answer, now)
    assert r.is_first_attempt is True
