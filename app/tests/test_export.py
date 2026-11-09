"""匯出 CSV（AC-14）和提醒文字輪流（2B）。E、M 開頭的編號是第三批新增。"""
import csv
from datetime import timedelta

from conftest import Q1, Q2, Q4, T
from leveling.bank import BankManifest, QuestionBank
from leveling.export import COLUMNS, export_csv
from leveling.messages import REMINDER_TEXTS, reminder_text
from leveling.progress import submit_answer
from leveling.storage import SqliteStore

H = timedelta(hours=1)


def test_e01_ac14_export_three_records(tmp_path):
    s = SqliteStore(tmp_path / "leveling.db", T)
    s.replace_bank(BankManifest(1, 3, ""), QuestionBank(1, (Q1, Q2, Q4)), T)
    s.conn.execute("UPDATE player_progress SET nickname = '小明'")  # 有暱稱也不能匯出
    r1 = submit_answer(s, Q1, Q1.answer, T)
    s.record_latency(r1.answer_id, 15, T)
    wrong = next(c for c in Q4.choices if c != Q4.answer)
    submit_answer(s, Q4, wrong, T + H)
    submit_answer(s, Q4, Q4.answer, T + 2 * H)
    xp_before = s.get_xp()

    out = tmp_path / "匯出.csv"
    assert export_csv(s, out) == 3

    with open(out, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    assert tuple(rows[0]) == COLUMNS
    assert len(rows) == 4
    assert rows[1][1:] == ["Q013", "字串與數字", "55", "對", "是", "10", "15"]
    assert rows[2][1:] == ["Q016", "range 和 for", wrong, "錯", "是", "0", ""]
    assert rows[3][4:7] == ["對", "否", "0"]

    text = out.read_text(encoding="utf-8-sig")
    assert "小明" not in text and s.player_id not in text  # 不含暱稱和玩家代號（NFR S2）
    assert s.get_xp() == xp_before  # 匯出不改任何資料
    s.close()


def test_m01_reminder_texts_rotate():
    assert [reminder_text(i) for i in range(4)] == [*REMINDER_TEXTS, REMINDER_TEXTS[0]]
