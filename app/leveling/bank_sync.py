"""從雲端下載題庫（api-spec.md §2 使用流程；ADR-003；AC-11～AC-13）。

只下載，不上傳任何資料（NFR S1）。只用 Python 內建的 urllib。
"""
import http.client
import json
import socket
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

from .bank import (
    BANK_VERSION_MISMATCH,
    BankError,
    bank_from_dict,
    manifest_from_dict,
    validate_bank,
)
from .progress import SaveError
from .rules import needs_download

MANIFEST_URL = "https://raw.githubusercontent.com/Ruijun711/leveling-question-bank/main/manifest.json"
BANK_URL = "https://raw.githubusercontent.com/Ruijun711/leveling-question-bank/main/question-bank.json"
CHECK_INTERVAL = timedelta(hours=24)  # Owner 決定 2026-11-09，1C
TIMEOUT_SECONDS = 15


class SyncStatus(Enum):
    UPDATED = "updated"                  # 下載到新題目
    UP_TO_DATE = "up_to_date"            # 已是最新
    OFFLINE = "offline"                  # NETWORK_UNAVAILABLE
    DOWNLOAD_FAILED = "download_failed"  # BANK_DOWNLOAD_INTERRUPTED、BANK_VERSION_MISMATCH、SERVICE_ERROR（下次再試）
    INVALID = "invalid"                  # BANK_INVALID_FORMAT（要等 Avi 修雲端題庫）


class OfflineError(Exception):
    pass


class DownloadError(Exception):
    pass


def should_check(last_checked_at: datetime | None, now: datetime, at_startup: bool) -> bool:
    """開機（程式啟動）時檢查一次，之後距離上次檢查滿 24 小時再檢查（1C）。"""
    return at_startup or last_checked_at is None or now - last_checked_at >= CHECK_INTERVAL


def fetch_json(url: str) -> dict:
    """下載一個 JSON 檔。連不上網路丟 OfflineError；其他下載問題丟 DownloadError。"""
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        raise DownloadError(f"HTTP {e.code}") from e
    except urllib.error.URLError as e:
        if isinstance(e.reason, (socket.gaierror, ConnectionRefusedError, OSError)) and not isinstance(
            e.reason, TimeoutError
        ):
            raise OfflineError(str(e.reason)) from e
        raise DownloadError(str(e.reason)) from e
    except (TimeoutError, http.client.HTTPException, ConnectionError) as e:
        raise DownloadError(repr(e)) from e
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise DownloadError(f"內容不完整：{e}") from e  # 下載到一半被切斷通常會走到這裡


def sync_bank(store, now: datetime, fetch=fetch_json) -> SyncStatus:
    """檢查並下載新題庫。不管結果如何，本機原本的題庫、作答紀錄、經驗值都不會壞掉。"""
    try:
        manifest = manifest_from_dict(fetch(MANIFEST_URL))
    except OfflineError:
        return SyncStatus.OFFLINE  # 沒網路不記檢查時間，下一次定時檢查再試
    except DownloadError:
        return SyncStatus.DOWNLOAD_FAILED
    except BankError:
        store.set_last_checked(now)
        return SyncStatus.INVALID

    store.set_last_checked(now)
    if not needs_download(manifest.bank_version, store.bank_version() or 0):
        return SyncStatus.UP_TO_DATE

    try:
        bank = bank_from_dict(fetch(BANK_URL))
        validate_bank(manifest, bank)
    except OfflineError:
        return SyncStatus.OFFLINE
    except DownloadError:
        return SyncStatus.DOWNLOAD_FAILED
    except BankError as e:
        return SyncStatus.DOWNLOAD_FAILED if e.code == BANK_VERSION_MISMATCH else SyncStatus.INVALID

    try:
        store.replace_bank(manifest, bank, now)
    except SaveError:
        return SyncStatus.DOWNLOAD_FAILED
    store.set_last_checked(now)
    return SyncStatus.UPDATED


def load_bundled_bank(store, data_dir: Path, now: datetime) -> bool:
    """安裝檔附的基本題庫（AC-12）：本機還沒有題庫、或附的版本比較新時放進去。回傳有沒有換。"""
    manifest = manifest_from_dict(json.loads((data_dir / "manifest.json").read_text(encoding="utf-8")))
    bank = bank_from_dict(json.loads((data_dir / "question-bank.json").read_text(encoding="utf-8")))
    validate_bank(manifest, bank)  # 附的題庫壞掉是程式的 bug，直接讓它丟錯
    if not needs_download(manifest.bank_version, store.bank_version() or 0):
        return False
    store.replace_bank(manifest, bank, now)
    return True
