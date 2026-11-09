"""假的記憶體版 ProgressStore（unit-test-stage1.md §4 Mocking Strategy）。

真的 SQLite 版在第三批做，「全部成功才算數」要另外用真的資料庫檔做整合測試（unit-test R2）。
"""
from leveling.progress import AnswerRecord, SaveError


class InMemoryStore:
    def __init__(self, xp=0, records=None):
        self.xp = xp
        self.records: list[AnswerRecord] = list(records or [])
        self.fail_next_save = False  # 設成 True：下一次存檔丟出 SaveError（模擬磁碟已滿）

    def get_xp(self) -> int:
        return self.xp

    def has_answered(self, question_id: str) -> bool:
        return any(r.question_id == question_id for r in self.records)

    def save_answer(self, record: AnswerRecord, new_total_xp: int) -> str:
        if self.fail_next_save:
            self.fail_next_save = False
            raise SaveError("模擬寫入失敗")
        # 作答紀錄和經驗值一起寫入（真的版本用同一個 transaction）
        self.records.append(record)
        self.xp = new_total_xp
        return f"fake-{len(self.records)}"
