"""bank_sync：用假的下載函式，不連網路。B 開頭的編號是第三批新增。"""
from dataclasses import asdict, replace
from datetime import timedelta
from pathlib import Path

import pytest

from conftest import Q1, Q2, Q3, T
from leveling.bank import BankManifest, QuestionBank
from leveling.bank_sync import (
    BANK_URL,
    MANIFEST_URL,
    DownloadError,
    OfflineError,
    SyncStatus,
    load_bundled_bank,
    should_check,
    sync_bank,
)
from leveling.storage import SqliteStore

H = timedelta(hours=1)
APP_DATA = Path(__file__).resolve().parents[1] / "data"


def _q_dict(q):
    d = asdict(q)
    d["choices"] = list(q.choices)
    return d


def _remote(version, questions, manifest_version=None, manifest_count=None):
    return {
        MANIFEST_URL: {"bank_version": manifest_version or version,
                       "question_count": manifest_count or len(questions),
                       "updated_at": "2026-11-09T09:00:00+08:00"},
        BANK_URL: {"bank_version": version, "questions": [_q_dict(q) for q in questions]},
    }


def _fetcher(files, fail=None):
    """fail = {url: 例外}：下載那個網址時丟出例外。"""
    calls = []

    def fetch(url):
        calls.append(url)
        if fail and url in fail:
            raise fail[url]
        return files[url]
    fetch.calls = calls
    return fetch


@pytest.fixture
def store(tmp_path):
    s = SqliteStore(tmp_path / "leveling.db", T)
    s.replace_bank(BankManifest(1, 3, ""), QuestionBank(1, (Q1, Q2, Q3)), T)
    yield s
    s.close()


NEW_Q = replace(Q1, id="Q099", added_in_version=2)


def test_b01_ac11_new_questions_downloaded(store):
    status = sync_bank(store, T, _fetcher(_remote(2, [Q1, Q2, Q3, NEW_Q])))
    assert status is SyncStatus.UPDATED
    assert store.bank_version() == 2
    assert "Q099" in {q.id for q in store.active_questions()}
    assert store.last_checked_at() == T


def test_b02_same_version_does_not_download_bank(store):
    fetch = _fetcher(_remote(1, [Q1, Q2, Q3]))
    assert sync_bank(store, T, fetch) is SyncStatus.UP_TO_DATE
    assert fetch.calls == [MANIFEST_URL]


def test_b03_ac12_offline_keeps_bank_and_does_not_mark_checked(store):
    fetch = _fetcher({}, fail={MANIFEST_URL: OfflineError("no network")})
    assert sync_bank(store, T, fetch) is SyncStatus.OFFLINE
    assert store.bank_version() == 1
    assert store.last_checked_at() is None  # 沒網路不算檢查過，下次定時檢查再試


def test_b04_ac13_interrupted_download_keeps_old_bank(store):
    fetch = _fetcher(_remote(2, [Q1, Q2, Q3, NEW_Q]), fail={BANK_URL: DownloadError("cut")})
    assert sync_bank(store, T, fetch) is SyncStatus.DOWNLOAD_FAILED
    assert store.bank_version() == 1
    assert len(store.active_questions()) == 3


def test_b05_github_cache_mismatch_is_retryable_failure(store):
    # 版本檔已是第 2 版，題庫檔還是舊的第 1 版
    files = _remote(2, [Q1, Q2, Q3, NEW_Q])
    files[BANK_URL] = _remote(1, [Q1, Q2, Q3])[BANK_URL]
    assert sync_bank(store, T, _fetcher(files)) is SyncStatus.DOWNLOAD_FAILED
    assert store.bank_version() == 1


def test_b06_invalid_bank_rejected_whole(store):
    bad = replace(NEW_Q, answer="不在選項裡")
    assert sync_bank(store, T, _fetcher(_remote(2, [Q1, Q2, Q3, bad]))) is SyncStatus.INVALID
    assert store.bank_version() == 1


def test_b07_should_check_rules():
    assert should_check(T, T + H, at_startup=True) is True       # 開機一定檢查
    assert should_check(None, T, at_startup=False) is True       # 從沒檢查過
    assert should_check(T, T + 23 * H, at_startup=False) is False
    assert should_check(T, T + 24 * H, at_startup=False) is True  # 滿 24 小時


def test_b08_bundled_bank_loaded_on_first_run(tmp_path):
    s = SqliteStore(tmp_path / "leveling.db", T)
    assert load_bundled_bank(s, APP_DATA, T) is True
    assert s.bank_version() == 1
    assert len(s.active_questions()) == 17
    assert load_bundled_bank(s, APP_DATA, T) is False  # 第二次不重複放
    s.close()
