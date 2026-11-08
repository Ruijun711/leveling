"""
學習精靈 · ADR-001 小試驗（PySide6）

要試的 4 件事（adr-001-desktop-framework.md §6）：
  1. 哥布林出現在桌面上：透明背景、沒有邊框、蓋在其他視窗上面、會移動
  2. 從按下「送出」到畫面顯示新的經驗值，不超過 3 秒（程式會印出花了幾毫秒）
  3. 做到可以動要花多久（Avi 記錄）
  4. 經驗值存進 SQLite，關掉程式重開後還在（ADR-002）

執行方式：
  .venv\\Scripts\\python main.py
"""

import os
import sqlite3
import sys
import time
from datetime import datetime, timezone

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPolygon
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

# ---------- 規則（prd FR-2） ----------

XP_PER_CORRECT = 10   # 答對得幾點經驗值（試驗：Avi 可以改這個數字看看）
XP_PER_LEVEL = 20
MAX_LEVEL = 9


def level_from_xp(xp: int) -> int:
    """等級 = min(9, 1 + INT(經驗值 / 20))（unit-test-stage1.md TC-001～006）"""
    if xp < 0:
        raise ValueError("經驗值不能是負數")
    return min(MAX_LEVEL, 1 + xp // XP_PER_LEVEL)


# 題目：階段 0 的 A1（practice-questions-stage0.md）
QUESTION = {
    "id": "A1",
    "concept": "字串與數字",
    "code": 'a = "3"\nb = "4"\nprint(a + b)',
    "choices": ["7", "34", "12", "會出現錯誤"],
    "answer": "34",
    "explanation": '"3" 和 "4" 都是字串，+ 是把兩段字串接起來，不是數學相加。',
}


# ---------- 本機資料：SQLite（ADR-002） ----------

DB_DIR = os.path.join(os.environ.get("APPDATA", "."), "學習精靈-試驗")
DB_PATH = os.path.join(DB_DIR, "spike.db")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def open_db() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    if conn.execute("PRAGMA user_version").fetchone()[0] == 0:
        # 欄位依 data-model.md §2（只取試驗用得到的）
        with conn:
            conn.execute(
                """CREATE TABLE player_progress (
                       id INTEGER PRIMARY KEY CHECK (id = 1),
                       xp INTEGER NOT NULL DEFAULT 0 CHECK (xp >= 0),
                       created_at TEXT NOT NULL,
                       updated_at TEXT NOT NULL,
                       version INTEGER NOT NULL DEFAULT 1,
                       deleted_at TEXT)"""
            )
            conn.execute(
                """CREATE TABLE answer_record (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       question_id TEXT NOT NULL,
                       concept TEXT NOT NULL,
                       answered_at TEXT NOT NULL,
                       selected_choice TEXT NOT NULL,
                       is_correct INTEGER NOT NULL,
                       is_first_attempt INTEGER NOT NULL,
                       xp_gained INTEGER NOT NULL,
                       created_at TEXT NOT NULL,
                       updated_at TEXT NOT NULL,
                       version INTEGER NOT NULL DEFAULT 1,
                       deleted_at TEXT)"""
            )
            t = now_utc()
            conn.execute(
                "INSERT INTO player_progress (id, xp, created_at, updated_at) VALUES (1, 0, ?, ?)",
                (t, t),
            )
            conn.execute("PRAGMA user_version = 1")
    return conn


def get_xp(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT xp FROM player_progress WHERE id = 1").fetchone()[0]


def submit_answer(conn: sqlite3.Connection, question: dict, selected: str) -> dict:
    """判斷對錯、算經驗值，作答紀錄和經驗值放在同一個 transaction 寫入（AC-10）。"""
    if not selected:
        raise ValueError("請先選一個答案")  # AC-7
    if selected not in question["choices"]:
        raise ValueError("答案不在選項裡")  # AC-7（Owner 決定 2026-11-08）

    is_correct = selected == question["answer"]
    answered_before = conn.execute(
        "SELECT COUNT(*) FROM answer_record WHERE question_id = ?", (question["id"],)
    ).fetchone()[0]
    is_first = answered_before == 0
    xp_gained = XP_PER_CORRECT if (is_correct and is_first) else 0

    old_xp = get_xp(conn)
    new_xp = old_xp + xp_gained
    t = now_utc()
    with conn:  # 全部成功才算數；中途出錯會自動復原
        conn.execute(
            """INSERT INTO answer_record (question_id, concept, answered_at, selected_choice,
                   is_correct, is_first_attempt, xp_gained, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (question["id"], question["concept"], t, selected,
             int(is_correct), int(is_first), xp_gained, t, t),
        )
        conn.execute(
            "UPDATE player_progress SET xp = ?, updated_at = ?, version = version + 1 WHERE id = 1",
            (new_xp, t),
        )
    return {
        "is_correct": is_correct,
        "is_first_attempt": is_first,
        "xp_gained": xp_gained,
        "total_xp": new_xp,
        "level": level_from_xp(new_xp),
        "leveled_up": level_from_xp(new_xp) > level_from_xp(old_xp),
    }


def reset_progress(conn: sqlite3.Connection) -> None:
    """試驗用：清掉作答紀錄和經驗值，方便重來。"""
    with conn:
        conn.execute("DELETE FROM answer_record")
        conn.execute("UPDATE player_progress SET xp = 0, updated_at = ? WHERE id = 1", (now_utc(),))


# ---------- 桌面哥布林（試驗第 1 項） ----------

class Goblin(QWidget):
    """透明、無邊框、永遠在最上層的小視窗，在桌面上左右走動。按右鍵關掉。"""

    SIZE = 140

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(self.SIZE, self.SIZE)
        self.step = 0
        self.dx = 4
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.walk)

    def appear(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.left() + 50, screen.bottom() - self.SIZE - 20)
        self.show()
        self.timer.start(30)

    def walk(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = self.x() + self.dx
        if x < screen.left() or x + self.SIZE > screen.right():
            self.dx = -self.dx
            x = self.x() + self.dx
        self.step += 1
        bob = 6 if (self.step // 8) % 2 else 0  # 走路時上下晃動
        self.move(x, screen.bottom() - self.SIZE - 20 - bob)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.timer.stop()
            self.hide()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        green = QColor("#5fa83a")
        dark = QColor("#2f5d1c")
        p.setPen(dark)
        # 耳朵
        p.setBrush(green)
        p.drawPolygon(QPolygon([QPoint(22, 45), QPoint(2, 25), QPoint(35, 38)]))
        p.drawPolygon(QPolygon([QPoint(118, 45), QPoint(138, 25), QPoint(105, 38)]))
        # 身體
        p.setBrush(QColor("#7a4b26"))
        p.drawRoundedRect(42, 88, 56, 44, 10, 10)
        # 頭
        p.setBrush(green)
        p.drawEllipse(25, 20, 90, 75)
        # 眼睛（看向走的方向）
        look = 4 if self.dx > 0 else -4
        p.setBrush(QColor("#ffeb3b"))
        p.drawEllipse(45, 45, 18, 14)
        p.drawEllipse(77, 45, 18, 14)
        p.setBrush(Qt.black)
        p.drawEllipse(51 + look, 49, 6, 6)
        p.drawEllipse(83 + look, 49, 6, 6)
        # 嘴巴和牙齒
        p.setBrush(QColor("#3b1f0e"))
        p.drawRoundedRect(52, 70, 36, 12, 5, 5)
        p.setBrush(Qt.white)
        p.drawPolygon(QPolygon([QPoint(57, 70), QPoint(61, 77), QPoint(65, 70)]))
        p.drawPolygon(QPolygon([QPoint(75, 70), QPoint(79, 77), QPoint(83, 70)]))


# ---------- 題目視窗（試驗第 2 項） ----------

class QuizWindow(QWidget):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__()
        self.conn = conn
        self.goblin = Goblin()
        self.setWindowTitle("學習精靈 · PySide6 小試驗")
        self.resize(420, 460)

        layout = QVBoxLayout(self)

        self.status = QLabel()
        self.status.setFont(QFont("Microsoft JhengHei", 14, QFont.Bold))
        layout.addWidget(self.status)

        layout.addWidget(QLabel(f"{QUESTION['id']} · {QUESTION['concept']}　這段程式會印出什麼？"))
        code = QLabel(QUESTION["code"])
        code.setFont(QFont("Consolas", 12))
        code.setStyleSheet("background:#f4f4f4; padding:8px; border:1px solid #ccc;")
        layout.addWidget(code)

        self.group = QButtonGroup(self)
        for i, c in enumerate(QUESTION["choices"]):
            rb = QRadioButton(f"({'ABCD'[i]}) {c}")
            rb.setProperty("choice", c)
            self.group.addButton(rb)
            layout.addWidget(rb)

        buttons = QHBoxLayout()
        submit = QPushButton("送出")
        submit.clicked.connect(self.on_submit)
        buttons.addWidget(submit)
        show_goblin = QPushButton("叫出哥布林")
        show_goblin.clicked.connect(self.goblin.appear)
        buttons.addWidget(show_goblin)
        reset = QPushButton("重設試驗資料")
        reset.clicked.connect(self.on_reset)
        buttons.addWidget(reset)
        layout.addLayout(buttons)

        self.result = QLabel()
        self.result.setWordWrap(True)
        layout.addWidget(self.result)

        self.timing = QLabel()
        self.timing.setStyleSheet("color:#666;")
        layout.addWidget(self.timing)

        layout.addWidget(QLabel(f"資料庫：{DB_PATH}"))
        layout.addStretch()
        self.refresh_status()

    def refresh_status(self):
        xp = get_xp(self.conn)
        self.status.setText(f"經驗值 {xp}　·　等級 {level_from_xp(xp)}")

    def on_submit(self):
        start = time.perf_counter()
        checked = self.group.checkedButton()
        selected = checked.property("choice") if checked else None
        try:
            r = submit_answer(self.conn, QUESTION, selected)
        except ValueError as e:
            self.result.setText(str(e))
            return
        except sqlite3.Error as e:
            # AC-10：存檔失敗，經驗值不變，選的答案留在畫面上
            self.result.setText(f"進度沒有存到，請再送出一次。（{e}）")
            return

        self.refresh_status()
        if r["is_correct"]:
            msg = "答對了！" + QUESTION["explanation"]
        else:
            msg = f"正確答案是「{QUESTION['answer']}」。" + QUESTION["explanation"]
        if not r["is_first_attempt"]:
            msg += "（不是第一次作答，不加經驗值）"
        elif r["xp_gained"]:
            msg += f"　+{r['xp_gained']} 經驗值"
        if r["leveled_up"]:
            msg += f"　升到 {r['level']} 級！"
        self.result.setText(msg)

        # 量「送出 → 畫面更新」：強制重畫後再停止計時（試驗第 2 項，NFR L1）
        self.repaint()
        ms = (time.perf_counter() - start) * 1000
        self.timing.setText(f"送出到畫面更新：{ms:.1f} 毫秒（標準：< 3000 毫秒）")
        print(f"[計時] 送出到畫面更新 {ms:.1f} ms")

        if r["is_correct"]:
            self.goblin.appear()

    def on_reset(self):
        reset_progress(self.conn)
        self.refresh_status()
        self.result.setText("已重設：經驗值 0，作答紀錄清空。")
        self.timing.clear()


def main():
    app = QApplication(sys.argv)
    conn = open_db()
    print(f"[資料庫] {DB_PATH}，目前經驗值 {get_xp(conn)}")
    w = QuizWindow(conn)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
