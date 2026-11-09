"""本機資料：SQLite（ADR-002）。

表格對應 data-model.md §2：player_progress、question、question_bank、answer_record、reminder_log，
加上 answer_latency（Owner 決定 2026-11-09，A：作答紀錄只新增不修改，毫秒數另外存）。

- 時間一律存 UTC 的 ISO 8601 文字。
- 作答紀錄＋經驗值、題庫＋題庫版本，各自在同一個 transaction 寫入，失敗就全部不變（AC-10、AC-13）。
- 每個 SqliteStore 有自己的連線；背景下載題庫時另外開一個（SQLite 連線不能跨執行緒共用）。
"""
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .bank import BankManifest, Question, QuestionBank
from .progress import AnswerRecord, SaveError

SCHEMA_VERSION = 1  # 存在 SQLite 的 user_version；以後改欄位時用來判斷要從哪一版升級

_SCHEMA = """
CREATE TABLE player_progress (
    id          TEXT PRIMARY KEY,
    nickname    TEXT,
    xp          INTEGER NOT NULL DEFAULT 0 CHECK (xp >= 0),
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    version     INTEGER NOT NULL DEFAULT 1,
    deleted_at  TEXT
);

CREATE TABLE question (
    id               TEXT PRIMARY KEY,
    concept          TEXT NOT NULL,
    type             TEXT NOT NULL CHECK (type IN ('multiple_choice', 'code_fill')),
    code             TEXT,
    prompt           TEXT NOT NULL,
    choices          TEXT,              -- JSON 陣列
    answer           TEXT NOT NULL,
    explanation      TEXT NOT NULL,
    status           TEXT NOT NULL CHECK (status IN ('active', 'retired')),
    added_in_version INTEGER NOT NULL,
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL,
    version          INTEGER NOT NULL DEFAULT 1,
    deleted_at       TEXT
);

CREATE TABLE question_bank (
    id              INTEGER PRIMARY KEY CHECK (id = 1),
    bank_version    INTEGER NOT NULL CHECK (bank_version >= 1),
    question_count  INTEGER NOT NULL,
    last_checked_at TEXT,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    version         INTEGER NOT NULL DEFAULT 1,
    deleted_at      TEXT
);

CREATE TABLE answer_record (
    id               TEXT PRIMARY KEY,
    player_id        TEXT NOT NULL REFERENCES player_progress(id) ON DELETE RESTRICT,
    question_id      TEXT NOT NULL REFERENCES question(id) ON DELETE RESTRICT,
    concept          TEXT NOT NULL,
    answered_at      TEXT NOT NULL,
    selected_choice  TEXT NOT NULL CHECK (selected_choice <> ''),
    is_correct       INTEGER NOT NULL,
    is_first_attempt INTEGER NOT NULL,
    xp_gained        INTEGER NOT NULL,
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL,
    version          INTEGER NOT NULL DEFAULT 1,
    deleted_at       TEXT
);

CREATE TABLE answer_latency (
    answer_id   TEXT PRIMARY KEY REFERENCES answer_record(id) ON DELETE CASCADE,
    update_ms   INTEGER NOT NULL CHECK (update_ms >= 0),
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    version     INTEGER NOT NULL DEFAULT 1,
    deleted_at  TEXT
);

CREATE TABLE reminder_log (
    id          TEXT PRIMARY KEY,
    player_id   TEXT NOT NULL REFERENCES player_progress(id) ON DELETE CASCADE,
    shown_at    TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    version     INTEGER NOT NULL DEFAULT 1,
    deleted_at  TEXT
);

-- data-model.md §6
CREATE INDEX idx_answer_player_time ON answer_record (player_id, answered_at DESC);
CREATE UNIQUE INDEX uq_answer_first_attempt ON answer_record (player_id, question_id)
    WHERE is_first_attempt = 1;
CREATE INDEX idx_answer_concept_time ON answer_record (player_id, concept, answered_at);
CREATE INDEX idx_reminder_player_time ON reminder_log (player_id, shown_at DESC);
CREATE INDEX idx_question_status_concept ON question (status, concept);
"""


def _ts(dt: datetime) -> str:
    if dt.tzinfo is None:
        raise ValueError("時間要帶時區（一律用 UTC）")
    return dt.astimezone(timezone.utc).isoformat()


def _dt(text: str | None) -> datetime | None:
    return datetime.fromisoformat(text) if text else None


class SqliteStore:
    def __init__(self, path: str | Path, now: datetime):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path, timeout=5)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")  # 背景下載題庫時，畫面照樣能讀
        self._migrate()
        self.player_id = self._ensure_player(now)

    def close(self) -> None:
        self.conn.close()

    # ---------- 資料表版本 ----------

    def _migrate(self) -> None:
        current = self.conn.execute("PRAGMA user_version").fetchone()[0]
        if current == 0:
            # 建表和寫入版本號在同一個 transaction，中途失敗就什麼都沒建
            self.conn.executescript("BEGIN;" + _SCHEMA + f"PRAGMA user_version = {SCHEMA_VERSION}; COMMIT;")
        elif current > SCHEMA_VERSION:
            raise RuntimeError(f"資料庫是新版程式建的（版本 {current}），請更新學習精靈")

    def _ensure_player(self, now: datetime) -> str:
        row = self.conn.execute("SELECT id FROM player_progress LIMIT 1").fetchone()
        if row:
            return row[0]
        player_id = uuid.uuid4().hex
        with self.conn:
            self.conn.execute(
                "INSERT INTO player_progress (id, xp, created_at, updated_at) VALUES (?, 0, ?, ?)",
                (player_id, _ts(now), _ts(now)),
            )
        return player_id

    # ---------- ProgressStore（progress.py） ----------

    def get_xp(self) -> int:
        return self.conn.execute("SELECT xp FROM player_progress WHERE id = ?", (self.player_id,)).fetchone()[0]

    def has_answered(self, question_id: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM answer_record WHERE player_id = ? AND question_id = ? LIMIT 1",
            (self.player_id, question_id),
        ).fetchone()
        return row is not None

    def save_answer(self, record: AnswerRecord, new_total_xp: int) -> str:
        answer_id = uuid.uuid4().hex
        at = _ts(record.answered_at)
        try:
            with self.conn:  # 同一個 transaction：任何一步失敗就整個還原（AC-10）
                self.conn.execute(
                    """INSERT INTO answer_record (id, player_id, question_id, concept, answered_at,
                           selected_choice, is_correct, is_first_attempt, xp_gained, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (answer_id, self.player_id, record.question_id, record.concept, at,
                     record.selected_choice, int(record.is_correct), int(record.is_first_attempt),
                     record.xp_gained, at, at),
                )
                self.conn.execute(
                    "UPDATE player_progress SET xp = ?, updated_at = ?, version = version + 1 WHERE id = ?",
                    (new_total_xp, at, self.player_id),
                )
        except sqlite3.Error as e:
            raise SaveError(str(e)) from e
        return answer_id

    def record_latency(self, answer_id: str, update_ms: int, now: datetime) -> None:
        """記錄「從送出到畫面更新」花了幾毫秒（NFR L1）。失敗不影響作答，只是少一筆量測。"""
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT OR IGNORE INTO answer_latency (answer_id, update_ms, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?)",
                    (answer_id, max(0, int(update_ms)), _ts(now), _ts(now)),
                )
        except sqlite3.Error:
            pass

    # ---------- 作答紀錄的查詢 ----------

    def answered_question_ids(self) -> set[str]:
        rows = self.conn.execute("SELECT DISTINCT question_id FROM answer_record WHERE player_id = ?",
                                 (self.player_id,))
        return {r[0] for r in rows}

    def last_answered_at(self) -> datetime | None:
        row = self.conn.execute("SELECT MAX(answered_at) FROM answer_record WHERE player_id = ?",
                                (self.player_id,)).fetchone()
        return _dt(row[0])

    def player_created_at(self) -> datetime:
        row = self.conn.execute("SELECT created_at FROM player_progress WHERE id = ?",
                                (self.player_id,)).fetchone()
        return _dt(row[0])

    def export_rows(self) -> list[dict]:
        """匯出用（AC-14）：作答紀錄＋毫秒數，依作答時間排序。不含暱稱和玩家代號。"""
        rows = self.conn.execute(
            """SELECT a.answered_at, a.question_id, a.concept, a.selected_choice, a.is_correct,
                      a.is_first_attempt, a.xp_gained, l.update_ms
               FROM answer_record a LEFT JOIN answer_latency l ON l.answer_id = a.id
               WHERE a.player_id = ? ORDER BY a.answered_at, a.created_at""",
            (self.player_id,),
        )
        keys = ("answered_at", "question_id", "concept", "selected_choice", "is_correct",
                "is_first_attempt", "xp_gained", "update_ms")
        return [dict(zip(keys, r)) for r in rows]

    # ---------- 提醒紀錄 ----------

    def reminder_times(self) -> list[datetime]:
        rows = self.conn.execute("SELECT shown_at FROM reminder_log WHERE player_id = ? ORDER BY shown_at",
                                 (self.player_id,))
        return [_dt(r[0]) for r in rows]

    def add_reminder(self, shown_at: datetime) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO reminder_log (id, player_id, shown_at, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (uuid.uuid4().hex, self.player_id, _ts(shown_at), _ts(shown_at), _ts(shown_at)),
            )

    # ---------- 題庫 ----------

    def bank_version(self) -> int | None:
        row = self.conn.execute("SELECT bank_version FROM question_bank WHERE id = 1").fetchone()
        return row[0] if row else None

    def last_checked_at(self) -> datetime | None:
        row = self.conn.execute("SELECT last_checked_at FROM question_bank WHERE id = 1").fetchone()
        return _dt(row[0]) if row else None

    def set_last_checked(self, now: datetime) -> None:
        with self.conn:
            self.conn.execute("UPDATE question_bank SET last_checked_at = ? WHERE id = 1", (_ts(now),))

    def replace_bank(self, manifest: BankManifest, bank: QuestionBank, now: datetime) -> None:
        """換成新版題庫。呼叫前要先通過 validate_bank。

        題目不刪除（舊的作答紀錄要對得上）：已有的題目更新內容（實際上只有 status 會變），新的題目新增。
        題目和題庫版本號在同一個 transaction，中途失敗就維持舊版（AC-13）。
        """
        at = _ts(now)
        try:
            with self.conn:
                for q in bank.questions:
                    self.conn.execute(
                        """INSERT INTO question (id, concept, type, code, prompt, choices, answer, explanation,
                               status, added_in_version, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           ON CONFLICT (id) DO UPDATE SET
                               concept = excluded.concept, type = excluded.type, code = excluded.code,
                               prompt = excluded.prompt, choices = excluded.choices, answer = excluded.answer,
                               explanation = excluded.explanation, status = excluded.status,
                               added_in_version = excluded.added_in_version,
                               updated_at = excluded.updated_at, version = question.version + 1""",
                        (q.id, q.concept, q.type, q.code, q.prompt, json.dumps(list(q.choices), ensure_ascii=False),
                         q.answer, q.explanation, q.status, q.added_in_version, at, at),
                    )
                self.conn.execute(
                    """INSERT INTO question_bank (id, bank_version, question_count, last_checked_at, created_at, updated_at)
                       VALUES (1, ?, ?, ?, ?, ?)
                       ON CONFLICT (id) DO UPDATE SET
                           bank_version = excluded.bank_version, question_count = excluded.question_count,
                           updated_at = excluded.updated_at, version = question_bank.version + 1""",
                    (manifest.bank_version, manifest.question_count, None, at, at),
                )
        except sqlite3.Error as e:
            raise SaveError(str(e)) from e

    def active_questions(self) -> list[Question]:
        rows = self.conn.execute(
            """SELECT id, concept, type, code, prompt, choices, answer, explanation, status, added_in_version
               FROM question WHERE status = 'active' ORDER BY id"""
        )
        return [
            Question(id=r[0], concept=r[1], type=r[2], code=r[3] or "", prompt=r[4],
                     choices=tuple(json.loads(r[5] or "[]")), answer=r[6], explanation=r[7],
                     status=r[8], added_in_version=r[9])
            for r in rows
        ]
