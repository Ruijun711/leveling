"""作答畫面（AC-1～AC-3、AC-6～AC-8、AC-10、AC-14；NFR L1、X1、X2）。

- 對錯同時用文字和符號表示，不只靠顏色（X1）。
- 只用鍵盤：1～4 或 A～D 選答案，Enter 送出，再按 Enter 下一題（X2）。
- 經驗值一律先在本機算、存、顯示，畫面畫完才記「花了幾毫秒」（L1；AnswerLatency）。
"""
import random
import time
from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import QStandardPaths, Qt
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from .. import __version__, messages
from ..export import export_csv
from ..progress import InvalidChoiceError, NoChoiceError, SaveError, submit_answer
from ..rules import MAX_LEVEL, XP_PER_LEVEL, level_from_xp, pick_question
from .reminder import Sprite

LETTERS = "ABCD"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MainWindow(QWidget):
    def __init__(self, store, rng: random.Random | None = None, now_fn=utcnow):
        super().__init__()
        self.store = store
        self.rng = rng or random.Random()
        self.now_fn = now_fn
        self.question = None
        self.answered = False      # 這題已經送出（下一個 Enter 是「下一題」）
        self.hide_on_close = False  # 有系統匣時，按 X 只是縮到系統匣（Owner 決定 2026-11-09，3A）

        self.setWindowTitle(f"學習精靈 {__version__}")
        self.resize(560, 600)

        self.progress_label = QLabel()
        self.progress_label.setFont(QFont("Microsoft JhengHei UI", 13, QFont.Bold))

        self.qid_label = QLabel()
        self.qid_label.setStyleSheet("color: #666;")

        self.code_view = QPlainTextEdit()
        self.code_view.setReadOnly(True)
        self.code_view.setFocusPolicy(Qt.NoFocus)  # 不搶鍵盤，Enter 和 1～4 才有作用
        self.code_view.setFont(QFont("Consolas", 12))
        self.code_view.setFixedHeight(150)

        self.prompt_label = QLabel()
        self.prompt_label.setWordWrap(True)

        self.choice_group = QButtonGroup(self)
        self.choice_buttons = []
        choices_box = QVBoxLayout()
        for i in range(4):
            b = QRadioButton()
            self.choice_group.addButton(b, i)
            self.choice_buttons.append(b)
            choices_box.addWidget(b)

        self.submit_button = QPushButton()
        self.submit_button.clicked.connect(self.on_enter)

        self.result_label = QLabel()
        self.result_label.setWordWrap(True)
        self.result_label.setFont(QFont("Microsoft JhengHei UI", 12, QFont.Bold))

        self.explain_label = QLabel()
        self.explain_label.setWordWrap(True)
        self.explain_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.explain_label.setStyleSheet(
            "background: #fff8e1; border: 1px solid #f0c36d; border-radius: 6px; padding: 8px;")

        hint = QLabel("鍵盤：1～4 或 A～D 選答案，Enter 送出／下一題")
        hint.setStyleSheet("color: #888; font-size: 11px;")

        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #888; font-size: 11px;")
        self.export_button = QPushButton("匯出作答紀錄")
        self.export_button.setFocusPolicy(Qt.NoFocus)
        self.export_button.clicked.connect(self.export_records)

        bottom = QHBoxLayout()
        bottom.addWidget(self.status_label, 1)
        bottom.addWidget(self.export_button)

        # 小精靈：答對開心、答錯難過但打氣、升級冒星星（Owner 決定 2026-11-09，2C）
        self.sprite = Sprite(size=88)
        header_text = QVBoxLayout()
        header_text.addWidget(self.progress_label)
        header_text.addWidget(self.qid_label)
        header_text.addStretch(1)
        header = QHBoxLayout()
        header.addWidget(self.sprite)
        header.addLayout(header_text, 1)

        layout = QVBoxLayout(self)
        layout.addLayout(header)
        layout.addWidget(self.code_view)
        layout.addWidget(self.prompt_label)
        layout.addLayout(choices_box)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.result_label)
        layout.addWidget(self.explain_label)
        layout.addStretch(1)
        layout.addWidget(hint)
        layout.addLayout(bottom)

        for i in range(4):
            for key in (str(i + 1), LETTERS[i]):
                QShortcut(QKeySequence(key), self, activated=lambda i=i: self.select(i))
        for key in (Qt.Key_Return, Qt.Key_Enter):
            QShortcut(QKeySequence(key), self, activated=self.on_enter)

        self.update_progress()

    # ---------- 顯示 ----------

    def update_progress(self) -> None:
        xp = self.store.get_xp()
        level = level_from_xp(xp)
        if level < MAX_LEVEL:
            need = level * XP_PER_LEVEL - xp
            extra = f"（再 {need} 點升級）"
        else:
            extra = f"（已達目前最高 {MAX_LEVEL} 級，經驗值繼續累積）"
        self.progress_label.setText(f"等級 {level}　經驗值 {xp} 點　{extra}")

    def set_status(self, text: str) -> None:
        self.status_label.setText(text)

    def show_message(self, text: str) -> None:
        self.result_label.setStyleSheet("color: #444;")
        self.result_label.setText(text)

    def load_next(self) -> None:
        self.question = pick_question(self.store.active_questions(), self.store.answered_question_ids(), self.rng)
        self.answered = False
        self.sprite.set_mood("normal")
        self.result_label.clear()
        self.explain_label.hide()
        self.choice_group.setExclusive(False)
        for b in self.choice_buttons:
            b.setChecked(False)
            b.setEnabled(True)
        self.choice_group.setExclusive(True)

        q = self.question
        if q is None:
            self.qid_label.setText("")
            self.code_view.setPlainText("")
            self.prompt_label.setText("目前沒有題目。")
            for b in self.choice_buttons:
                b.hide()
            self.submit_button.setEnabled(False)
            return

        self.qid_label.setText(f"題號 {q.id}")
        self.code_view.setPlainText(q.code)
        self.prompt_label.setText(q.prompt)
        for i, b in enumerate(self.choice_buttons):
            if i < len(q.choices):
                b.setText(f"({LETTERS[i]}) {q.choices[i]}")
                b.show()
            else:
                b.hide()
        self.submit_button.setEnabled(True)
        self.submit_button.setText("送出（Enter）")

    def select(self, index: int) -> None:
        if not self.answered and self.question and index < len(self.question.choices):
            self.choice_buttons[index].setChecked(True)

    # ---------- 作答 ----------

    def on_enter(self) -> None:
        if self.answered:
            self.load_next()
        else:
            self.submit()

    def selected_choice(self) -> str | None:
        i = self.choice_group.checkedId()
        return self.question.choices[i] if i >= 0 else None

    def submit(self) -> None:
        q = self.question
        if q is None:
            return
        started = time.perf_counter()
        now = self.now_fn()
        try:
            result = submit_answer(self.store, q, self.selected_choice(), now)
        except NoChoiceError:
            self.show_message(messages.NO_CHOICE)  # AC-7：不用掉第一次作答
            return
        except InvalidChoiceError:
            self.show_message(messages.invalid_choice(q.id))
            self.finish_question()
            return
        except SaveError:
            self.show_message(messages.SAVE_FAILED)  # AC-10：答案留在畫面上，可以再送一次
            return

        self.update_progress()
        if result.is_correct:
            text = "✔ 答對！"
            text += f"經驗值 +{result.xp_gained}" if result.xp_gained else "（這題之前做過，不加經驗值）"
            self.result_label.setStyleSheet("color: #1b7a2e;")
        else:
            text = "✘ 答錯"
            self.result_label.setStyleSheet("color: #b3261e;")
            letter = LETTERS[q.choices.index(q.answer)]
            self.explain_label.setText(
                f"考的觀念：{q.concept}\n正確答案：({letter}) {q.answer}\n\n{q.explanation}")
            self.explain_label.show()
        if result.leveled_up:
            text += f"\n⬆ 升級！現在是 {result.level} 級"
        self.sprite.set_mood("levelup" if result.leveled_up else "happy" if result.is_correct else "sad")
        self.result_label.setText(text)
        self.finish_question()

        self.repaint()  # 先把畫面畫完，再停止計時（NFR L1）
        update_ms = round((time.perf_counter() - started) * 1000)
        if result.answer_id:
            self.store.record_latency(result.answer_id, update_ms, now)

    def finish_question(self) -> None:
        self.answered = True
        for b in self.choice_buttons:
            b.setEnabled(False)
        self.submit_button.setText("下一題（Enter）")

    # ---------- 其他 ----------

    def export_records(self) -> None:
        # 預設存到「文件」資料夾，不存到程式所在的資料夾（2026-11-09 Avi 決定 D2）
        docs = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        default = str(Path(docs) / "學習精靈作答紀錄.csv")
        path, _ = QFileDialog.getSaveFileName(self, "匯出作答紀錄", default, "CSV 檔 (*.csv)")
        if not path:
            return
        try:
            n = export_csv(self.store, path)
        except OSError as e:
            QMessageBox.warning(self, "學習精靈", f"匯出失敗：{e}")
            return
        QMessageBox.information(self, "學習精靈", f"已匯出 {n} 筆作答紀錄。\n程式不會自動傳出這個檔案。")

    def show_and_raise(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event) -> None:
        if self.hide_on_close:
            event.ignore()
            self.hide()
        else:
            event.accept()
