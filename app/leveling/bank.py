"""題庫的資料格式和檢查規則（api-spec.md §3）。

下載的題庫要整份通過 validate_bank 才能替換本機題庫；沒過就保留舊的（AC-13）。
"""
from dataclasses import dataclass

BANK_INVALID_FORMAT = "BANK_INVALID_FORMAT"      # 內容不符合規則，要等 Avi 修雲端題庫
BANK_VERSION_MISMATCH = "BANK_VERSION_MISMATCH"  # 版本號或題數對不上（下載不完整、GitHub 快取），下次再試

QUESTION_TYPES = ("multiple_choice", "code_fill")
QUESTION_STATUSES = ("active", "retired")
CHOICES_PER_QUESTION = 4


class BankError(Exception):
    def __init__(self, code: str, message: str = ""):
        super().__init__(f"{code}: {message}" if message else code)
        self.code = code


@dataclass(frozen=True)
class Question:
    id: str
    concept: str
    type: str
    code: str
    prompt: str
    choices: tuple[str, ...]
    answer: str
    explanation: str
    status: str
    added_in_version: int


@dataclass(frozen=True)
class BankManifest:
    bank_version: int
    question_count: int
    updated_at: str


@dataclass(frozen=True)
class QuestionBank:
    bank_version: int
    questions: tuple[Question, ...]


def manifest_from_dict(data: dict) -> BankManifest:
    """把 manifest.json 讀進來的 dict 轉成 BankManifest；缺欄位或型別不對算 BANK_INVALID_FORMAT。"""
    try:
        return BankManifest(
            bank_version=_int(data["bank_version"]),
            question_count=_int(data["question_count"]),
            updated_at=str(data["updated_at"]),
        )
    except (KeyError, TypeError, ValueError) as e:
        raise BankError(BANK_INVALID_FORMAT, f"manifest 格式錯誤：{e!r}") from e


def bank_from_dict(data: dict) -> QuestionBank:
    """把 question-bank.json 讀進來的 dict 轉成 QuestionBank；缺欄位或型別不對算 BANK_INVALID_FORMAT。"""
    try:
        questions = tuple(
            Question(
                id=str(q["id"]),
                concept=str(q["concept"]),
                type=str(q["type"]),
                code=str(q["code"]),
                prompt=str(q["prompt"]),
                choices=tuple(str(c) for c in q.get("choices") or ()),
                answer=str(q["answer"]),
                explanation=str(q["explanation"]),
                status=str(q["status"]),
                added_in_version=_int(q["added_in_version"]),
            )
            for q in data["questions"]
        )
        return QuestionBank(bank_version=_int(data["bank_version"]), questions=questions)
    except (KeyError, TypeError, ValueError, AttributeError) as e:
        raise BankError(BANK_INVALID_FORMAT, f"題庫格式錯誤：{e!r}") from e


def _int(value) -> int:
    # JSON 的 true/false 在 Python 也是 int，要排除
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"應該是整數：{value!r}")
    return value


def validate_bank(manifest: BankManifest, bank: QuestionBank) -> None:
    """整份題庫都合格才回傳；任何一項不合格就丟出 BankError(code)。"""
    if manifest.bank_version < 1 or bank.bank_version < 1:
        raise BankError(BANK_INVALID_FORMAT, "bank_version 最小是 1")
    if manifest.question_count < 1:
        raise BankError(BANK_INVALID_FORMAT, "question_count 最小是 1")
    if bank.bank_version != manifest.bank_version:
        raise BankError(BANK_VERSION_MISMATCH,
                        f"版本檔是 {manifest.bank_version}，題庫是 {bank.bank_version}")
    if len(bank.questions) != manifest.question_count:
        raise BankError(BANK_VERSION_MISMATCH,
                        f"版本檔說有 {manifest.question_count} 題，題庫有 {len(bank.questions)} 題")

    seen_ids = set()
    for q in bank.questions:
        _validate_question(q, bank.bank_version)
        if q.id in seen_ids:
            raise BankError(BANK_INVALID_FORMAT, f"題號重複：{q.id}")
        seen_ids.add(q.id)


def _validate_question(q: Question, bank_version: int) -> None:
    def fail(reason: str):
        raise BankError(BANK_INVALID_FORMAT, f"{q.id or '(沒有題號)'}：{reason}")

    if not q.id.strip():
        fail("題號是空的")
    if not q.concept.strip():
        fail("concept 是空的")
    if not q.prompt.strip():
        fail("prompt 是空的")
    if not q.explanation.strip():
        fail("explanation 是空的")
    if q.type not in QUESTION_TYPES:
        fail(f"不認得的 type：{q.type}")
    if q.status not in QUESTION_STATUSES:
        fail(f"不認得的 status：{q.status}")
    if not 1 <= q.added_in_version <= bank_version:
        fail(f"added_in_version 要在 1～{bank_version} 之間：{q.added_in_version}")

    if q.type == "multiple_choice":
        if len(q.choices) != CHOICES_PER_QUESTION:
            fail(f"選擇題要剛好 {CHOICES_PER_QUESTION} 個選項，現在有 {len(q.choices)} 個")
        if len(set(q.choices)) != len(q.choices):
            fail("選項重複")
        if q.answer not in q.choices:
            fail("answer 不在選項裡")
    # code_fill（階段 5）的 answer 格式還沒定（api-spec TODO），階段 1 先只檢查共通欄位
