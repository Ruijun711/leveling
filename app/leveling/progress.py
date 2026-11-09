"""送出答案：判斷對錯、算經驗值和等級、存作答紀錄（AC-1～AC-10）。

ProgressStore 是本機存資料的介面；真的版本是 SQLite（ADR-002），作答紀錄和經驗值要在同一個
transaction 寫入，失敗就兩邊都不變（AC-10）。
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from .bank import Question
from .rules import level_from_xp, xp_for_answer


class SaveError(Exception):
    """存檔失敗（例如磁碟已滿）。經驗值和作答紀錄都沒有改變，重送仍算第一次作答。"""


class NoChoiceError(ValueError):
    """沒選答案就送出（AC-7）。"""


class InvalidChoiceError(ValueError):
    """送出的答案不在選項裡；畫面上不會發生，發生代表程式或題庫有 bug（AC-7）。"""


@dataclass(frozen=True)
class AnswerRecord:
    """一筆作答紀錄（data-model AnswerRecord；欄位同 AC-5）。只新增，不修改。"""
    question_id: str
    concept: str
    answered_at: datetime
    selected_choice: str
    is_correct: bool
    is_first_attempt: bool
    xp_gained: int


@dataclass(frozen=True)
class SubmitResult:
    is_correct: bool
    is_first_attempt: bool
    xp_gained: int
    total_xp: int
    level: int
    leveled_up: bool
    answer_id: str | None = None  # 這筆作答紀錄的代號；畫面更新後用來記毫秒數（AnswerLatency）


class ProgressStore(Protocol):
    def get_xp(self) -> int: ...

    def has_answered(self, question_id: str) -> bool:
        """這題有沒有任何一筆作答紀錄（存檔失敗的那次不算）。"""
        ...

    def save_answer(self, record: AnswerRecord, new_total_xp: int) -> str | None:
        """作答紀錄和新的經驗值一起存，回傳這筆紀錄的代號；失敗丟出 SaveError，而且兩邊都不變。"""
        ...


def submit_answer(store: ProgressStore, question: Question, selected_choice: str | None,
                  now: datetime) -> SubmitResult:
    if not selected_choice:
        raise NoChoiceError("請先選一個答案")
    if selected_choice not in question.choices:
        raise InvalidChoiceError(f"這題資料有問題（題號 {question.id}），請按下一題，並告訴 Avi。")

    is_correct = selected_choice == question.answer
    is_first_attempt = not store.has_answered(question.id)
    xp_gained = xp_for_answer(is_correct, is_first_attempt)

    old_xp = store.get_xp()
    new_xp = old_xp + xp_gained
    record = AnswerRecord(
        question_id=question.id,
        concept=question.concept,
        answered_at=now,
        selected_choice=selected_choice,
        is_correct=is_correct,
        is_first_attempt=is_first_attempt,
        xp_gained=xp_gained,
    )
    answer_id = store.save_answer(record, new_xp)  # 失敗會丟出 SaveError，不會走到下面

    old_level, new_level = level_from_xp(old_xp), level_from_xp(new_xp)
    return SubmitResult(
        is_correct=is_correct,
        is_first_attempt=is_first_attempt,
        xp_gained=xp_gained,
        total_xp=new_xp,
        level=new_level,
        leveled_up=new_level > old_level,
        answer_id=answer_id,
    )
