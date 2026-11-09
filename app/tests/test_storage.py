"""SqliteStore 整合測試：用真的 SQLite 暫存檔（unit-test-stage1.md §9 R2）。

S 開頭的編號是第三批新增，不在 38 條裡。
"""
import sqlite3
from dataclasses import replace
from datetime import timedelta

import pytest

from conftest import Q1, Q2, Q3, T
from leveling.bank import BankManifest, QuestionBank
from leveling.progress import SaveError, submit_answer
from leveling.storage import SCHEMA_VERSION, SqliteStore

H = timedelta(hours=1)


def _bank(version, questions):
    return (BankManifest(version, len(questions), "2026-11-09T09:00:00+08:00"),
            QuestionBank(version, tuple(questions)))


@pytest.fixture
def db(tmp_path):
    return tmp_path / "學習精靈" / "leveling.db"  # 中文路徑也要能用


@pytest.fixture
def store(db):
    s = SqliteStore(db, T)
    s.replace_bank(*_bank(1, [Q1, Q2, Q3]), T)
    yield s
    s.close()


def test_s01_new_store_starts_at_0_xp_with_schema_version(store):
    assert store.get_xp() == 0
    assert store.conn.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    assert store.player_created_at() == T


def test_s02_ac9_progress_survives_reopen(db):
    s = SqliteStore(db, T)
    s.replace_bank(*_bank(1, [Q1, Q2, Q3]), T)
    submit_answer(s, Q1, Q1.answer, T)
    submit_answer(s, Q3, Q3.answer, T + H)
    s.add_reminder(T + 30 * H)
    player = s.player_id
    s.close()

    s2 = SqliteStore(db, T + 100 * H)  # 重開機
    assert s2.player_id == player
    assert s2.get_xp() == 20
    assert len(s2.export_rows()) == 2
    assert s2.last_answered_at() == T + H
    assert s2.reminder_times() == [T + 30 * H]
    assert s2.player_created_at() == T  # 不會因為重開就重設
    s2.close()


def test_s03_ac10_failure_in_middle_of_save_changes_nothing(store):
    # 作答紀錄先寫進去，更新經驗值時才失敗：transaction 要把作答紀錄也還原
    store.conn.execute(
        "CREATE TEMP TRIGGER fail_xp BEFORE UPDATE ON player_progress "
        "BEGIN SELECT RAISE(ABORT, 'disk full'); END"
    )
    with pytest.raises(SaveError):
        submit_answer(store, Q1, Q1.answer, T)
    assert store.get_xp() == 0
    assert store.export_rows() == []

    store.conn.execute("DROP TRIGGER fail_xp")
    r = submit_answer(store, Q1, Q1.answer, T)
    assert (r.is_first_attempt, r.total_xp) == (True, 10)


def test_s04_ac13_failure_in_middle_of_bank_replace_keeps_old_bank(store):
    new_q = replace(Q2, id="Q099", added_in_version=2)
    store.conn.execute(
        "CREATE TEMP TRIGGER fail_bank BEFORE UPDATE ON question_bank "
        "BEGIN SELECT RAISE(ABORT, 'network gone'); END"
    )
    with pytest.raises(SaveError):
        store.replace_bank(*_bank(2, [Q1, Q2, Q3, new_q]), T)
    assert store.bank_version() == 1
    assert [q.id for q in store.active_questions()] == ["Q013", "Q014", "Q015"]


def test_s05_replace_bank_adds_new_and_retires_old(store):
    submit_answer(store, Q2, Q2.answer, T)
    new_q = replace(Q1, id="Q099", added_in_version=2)
    store.replace_bank(*_bank(2, [Q1, replace(Q2, status="retired"), Q3, new_q]), T + H)

    assert store.bank_version() == 2
    assert [q.id for q in store.active_questions()] == ["Q013", "Q015", "Q099"]
    # 停用的題目還在，舊的作答紀錄對得上
    assert store.export_rows()[0]["question_id"] == "Q014"


def test_s06_only_one_first_attempt_per_question(store):
    submit_answer(store, Q1, Q1.answer, T)
    with pytest.raises(sqlite3.IntegrityError):
        store.conn.execute(
            "INSERT INTO answer_record (id, player_id, question_id, concept, answered_at, selected_choice, "
            "is_correct, is_first_attempt, xp_gained, created_at, updated_at) "
            "VALUES ('x', ?, 'Q013', 'c', 't', '55', 1, 1, 10, 't', 't')",
            (store.player_id,),
        )


def test_s07_question_with_answers_cannot_be_deleted(store):
    submit_answer(store, Q1, Q1.answer, T)
    with pytest.raises(sqlite3.IntegrityError):
        store.conn.execute("DELETE FROM question WHERE id = 'Q013'")


def test_s08_latency_is_stored_separately_and_joined_on_export(store):
    r1 = submit_answer(store, Q1, Q1.answer, T)
    submit_answer(store, Q2, Q2.answer, T + H)  # 這筆沒有記到毫秒數
    store.record_latency(r1.answer_id, 12, T)

    rows = store.export_rows()
    assert [r["update_ms"] for r in rows] == [12, None]


def test_s09_answered_ids_and_questions_round_trip(store):
    submit_answer(store, Q3, Q3.answer, T)
    assert store.answered_question_ids() == {"Q015"}
    q = next(q for q in store.active_questions() if q.id == "Q014")
    assert q == Q2  # 選項、換行、縮排都原樣讀回


def test_s10_last_checked_round_trip(store):
    assert store.last_checked_at() is None
    store.set_last_checked(T + 5 * H)
    assert store.last_checked_at() == T + 5 * H


def test_s11_naive_datetime_rejected(store):
    with pytest.raises(ValueError):
        store.add_reminder(T.replace(tzinfo=None))
