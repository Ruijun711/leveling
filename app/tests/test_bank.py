"""T7 validate_bank（api-spec.md §3 的規則）。

tcNNN 對應 04-測試/unit-test-stage1.md。「合格題庫」：版本 3、2 題，都是合格的選擇題，其中 1 題已停用。
"""
import json
from dataclasses import replace
from pathlib import Path

import pytest

from conftest import Q1, Q2
from leveling.bank import (
    BANK_INVALID_FORMAT,
    BANK_VERSION_MISMATCH,
    BankError,
    BankManifest,
    QuestionBank,
    bank_from_dict,
    manifest_from_dict,
    validate_bank,
)


def _manifest(version=3, count=2):
    return BankManifest(bank_version=version, question_count=count,
                        updated_at="2026-11-09T09:00:00+08:00")


def _good_questions():
    return (
        replace(Q1, added_in_version=1),
        replace(Q2, added_in_version=2, status="retired"),
    )


def _bank(version=3, questions=None):
    return QuestionBank(bank_version=version,
                        questions=_good_questions() if questions is None else tuple(questions))


def _assert_error(code, manifest, bank):
    with pytest.raises(BankError) as e:
        validate_bank(manifest, bank)
    assert e.value.code == code


def test_tc031_good_bank_with_retired_question_passes():
    validate_bank(_manifest(3, 2), _bank(3))


def test_tc032_version_mismatch():
    _assert_error(BANK_VERSION_MISMATCH, _manifest(3, 2), _bank(2))


def test_tc033_question_count_mismatch():
    _assert_error(BANK_VERSION_MISMATCH, _manifest(3, 3), _bank(3))


_q1 = replace(Q1, added_in_version=1)
_BROKEN = {
    "a_answer_not_in_choices": replace(_q1, answer="99"),
    "b_only_3_choices": replace(_q1, choices=_q1.choices[:3]),
    "c_duplicate_choices": replace(_q1, choices=("10", "10", "7", "會出現錯誤"), answer="10"),
    "d_duplicate_id": replace(Q2, id=_q1.id, added_in_version=1),
    "e_unknown_status": replace(_q1, status="deleted"),
    "f_empty_explanation": replace(_q1, explanation=""),
    "g_empty_concept": replace(_q1, concept=""),
}


@pytest.mark.parametrize("case", sorted(_BROKEN))
def test_tc034_each_rule_has_a_counterexample(case):
    broken = _BROKEN[case]
    if case == "d_duplicate_id":
        questions = [_q1, broken]
    else:
        questions = [broken, _good_questions()[1]]
    _assert_error(BANK_INVALID_FORMAT, _manifest(3, 2), _bank(3, questions))


def test_tc035_added_in_version_equal_to_bank_version_passes():
    qs = [replace(Q1, added_in_version=3), _good_questions()[1]]
    validate_bank(_manifest(3, 2), _bank(3, qs))


def test_tc036_added_in_version_above_bank_version_fails():
    qs = [replace(Q1, added_in_version=4), _good_questions()[1]]
    _assert_error(BANK_INVALID_FORMAT, _manifest(3, 2), _bank(3, qs))


def test_tc037_version_0_is_invalid():
    qs = [replace(q, added_in_version=0) for q in _good_questions()]
    _assert_error(BANK_INVALID_FORMAT, _manifest(0, 2), _bank(0, qs))


# ---------- 計畫外加測：真的題庫 repo 檔案要能通過檢查 ----------

_REAL_BANK = Path(__file__).resolve().parents[3] / "leveling-question-bank"


@pytest.mark.skipif(not (_REAL_BANK / "question-bank.json").exists(),
                    reason="本機沒有 Desktop/leveling-question-bank")
def test_extra_real_question_bank_passes():
    manifest = manifest_from_dict(json.loads((_REAL_BANK / "manifest.json").read_text(encoding="utf-8")))
    bank = bank_from_dict(json.loads((_REAL_BANK / "question-bank.json").read_text(encoding="utf-8")))
    validate_bank(manifest, bank)
    assert len(bank.questions) == manifest.question_count


def test_extra_malformed_json_dict_is_invalid_format():
    with pytest.raises(BankError) as e:
        bank_from_dict({"bank_version": 1, "questions": [{"id": "Q001"}]})
    assert e.value.code == BANK_INVALID_FORMAT
