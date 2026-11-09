"""桌面提醒（AC-4；NFR A3）和小精靈。

小精靈用程式畫（Owner 決定 2026-11-09，1A）：尖帽子、尖耳朵、翅膀、綠衣服（2B，原本只是圓形笑臉）。
提醒時和文字泡泡一起出現在桌面右下角；作答畫面也有一隻，答對、答錯、升級會換表情（2C）。
階段 2 有職業角色後，再換成玩家自己的角色。
"""
import math
from datetime import datetime, timedelta, timezone

from PySide6.QtCore import QObject, QPoint, QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from .. import messages
from ..rules import FIRST_REMINDER_AFTER, REMINDER_INTERVAL, reminder_due

MOODS = ("normal", "happy", "sad", "levelup")

OUTLINE = QColor("#14532d")
SKIN = QColor("#ffe0bd")
TUNIC = QColor("#4ade80")
HAT = QColor("#16a34a")
WING = QColor(186, 230, 253, 200)  # 半透明淺藍
EYE = QColor("#1f2937")
CHEEK = QColor(251, 113, 133, 140)
STAR = QColor("#facc15")


def draw_sprite(p: QPainter, rect: QRectF, mood: str = "normal") -> None:
    """畫小精靈。座標都用 0～1 的比例，換算到 rect；系統匣圖示也用同一個。

    mood：normal 微笑、happy 開心（答對）、sad 難過但還在打氣（答錯）、levelup 開心＋星星（升級）。
    """
    x0, y0, w, h = rect.x(), rect.y(), rect.width(), rect.height()

    def pt(x, y):
        return QPointF(x0 + w * x, y0 + h * y)

    def box(x1, y1, x2, y2):
        return QRectF(pt(x1, y1), pt(x2, y2))

    def poly(*xy):
        return QPolygonF([pt(xy[i], xy[i + 1]) for i in range(0, len(xy), 2)])

    p.save()
    p.setRenderHint(QPainter.Antialiasing)
    pen = QPen(OUTLINE, max(1.0, w / 45))
    p.setPen(pen)

    # 翅膀（在身體後面）
    p.setBrush(WING)
    p.drawEllipse(box(0.04, 0.50, 0.36, 0.74))
    p.drawEllipse(box(0.64, 0.50, 0.96, 0.74))
    # 身體
    p.setBrush(TUNIC)
    p.drawEllipse(box(0.33, 0.60, 0.67, 0.98))
    # 尖耳朵
    p.setBrush(SKIN)
    p.drawPolygon(poly(0.33, 0.38, 0.13, 0.27, 0.33, 0.50))
    p.drawPolygon(poly(0.67, 0.38, 0.87, 0.27, 0.67, 0.50))
    # 頭
    p.drawEllipse(box(0.29, 0.25, 0.71, 0.65))
    # 尖帽子
    p.setBrush(HAT)
    p.drawPolygon(poly(0.29, 0.33, 0.71, 0.33, 0.60, 0.02))
    p.drawEllipse(box(0.26, 0.28, 0.74, 0.37))
    p.setBrush(STAR)
    p.drawEllipse(box(0.56, 0.0, 0.65, 0.07))  # 帽尖的小球

    # 臉
    p.setPen(Qt.NoPen)
    p.setBrush(CHEEK)
    if mood in ("happy", "levelup"):
        p.drawEllipse(box(0.33, 0.49, 0.41, 0.54))
        p.drawEllipse(box(0.59, 0.49, 0.67, 0.54))
    p.setBrush(EYE)
    face_pen = QPen(EYE, max(1.0, w / 40))
    if mood in ("happy", "levelup"):
        # 開心：眼睛瞇成 ^ ^
        p.setPen(face_pen)
        p.setBrush(Qt.NoBrush)
        p.drawArc(box(0.38, 0.42, 0.46, 0.49), 0, 180 * 16)
        p.drawArc(box(0.54, 0.42, 0.62, 0.49), 0, 180 * 16)
    else:
        p.drawEllipse(box(0.39, 0.42, 0.45, 0.49))
        p.drawEllipse(box(0.55, 0.42, 0.61, 0.49))
        p.setPen(face_pen)
    p.setBrush(Qt.NoBrush)
    if mood == "sad":
        # 嘴角往下，眉毛往上：難過但還在打氣
        p.drawArc(box(0.44, 0.54, 0.56, 0.61), 30 * 16, 120 * 16)
        p.drawLine(pt(0.37, 0.40), pt(0.45, 0.35))
        p.drawLine(pt(0.63, 0.40), pt(0.55, 0.35))
    elif mood in ("happy", "levelup"):
        p.setBrush(QColor("#be123c"))
        p.drawChord(box(0.42, 0.47, 0.58, 0.60), 180 * 16, 180 * 16)  # 張嘴笑
    else:
        p.drawArc(box(0.43, 0.48, 0.57, 0.58), 200 * 16, 140 * 16)

    if mood == "levelup":
        p.setPen(QPen(OUTLINE, max(1.0, w / 60)))
        p.setBrush(STAR)
        for cx, cy, r in ((0.12, 0.14, 0.07), (0.88, 0.16, 0.06), (0.86, 0.86, 0.05)):
            star = []
            for i in range(10):
                a = math.pi / 2 + i * math.pi / 5
                rr = r if i % 2 == 0 else r * 0.45
                star += [cx + rr * math.cos(a), cy - rr * math.sin(a)]
            p.drawPolygon(poly(*star))
    p.restore()


class Sprite(QWidget):
    def __init__(self, size=96, mood="normal"):
        super().__init__()
        self.mood = mood
        self.setFixedSize(size, size)

    def set_mood(self, mood: str) -> None:
        self.mood = mood
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        draw_sprite(p, QRectF(2, 2, self.width() - 4, self.height() - 4), self.mood)
        p.end()


class ReminderBubble(QWidget):
    practice_clicked = Signal()

    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setFixedWidth(230)
        self.text_label.setStyleSheet("color: #222; font-size: 14px;")

        go = QPushButton("去練習")
        later = QPushButton("等一下")
        go.clicked.connect(self._go)
        later.clicked.connect(self.hide)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(later)
        buttons.addWidget(go)

        bubble = QFrame()
        bubble.setObjectName("bubble")
        bubble.setStyleSheet("#bubble { background: white; border: 2px solid #2563eb; border-radius: 12px; }")
        inner = QVBoxLayout(bubble)
        inner.addWidget(self.text_label)
        inner.addLayout(buttons)

        layout = QHBoxLayout(self)
        layout.addWidget(Sprite(), 0, Qt.AlignBottom)
        layout.addWidget(bubble)

    def show_text(self, text: str) -> None:
        self.text_label.setText(text)
        self.adjustSize()
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(QPoint(screen.right() - self.width() - 16, screen.bottom() - self.height() - 16))
        self.show()
        self.raise_()

    def _go(self) -> None:
        self.hide()
        self.practice_clicked.emit()


class ReminderScheduler(QObject):
    """每隔一段時間檢查一次該不該提醒（正式：每分鐘，在 NFR A3 的 15 分鐘誤差內）。"""

    def __init__(self, store, bubble: ReminderBubble,
                 first_after: timedelta = FIRST_REMINDER_AFTER,
                 interval: timedelta = REMINDER_INTERVAL,
                 check_ms: int = 60_000):
        super().__init__()
        self.store = store
        self.bubble = bubble
        self.first_after = first_after
        self.interval = interval
        self.timer = QTimer(self)
        self.timer.setInterval(check_ms)
        self.timer.timeout.connect(self.check)

    def start(self) -> None:
        self.check()
        self.timer.start()

    def check(self) -> None:
        now = datetime.now(timezone.utc)
        # 還沒作答過：從第一次開啟學習精靈的時間算（AC-4）
        anchor = self.store.last_answered_at() or self.store.player_created_at()
        shown = self.store.reminder_times()
        if reminder_due(now, anchor, shown, self.first_after, self.interval):
            self.bubble.show_text(messages.reminder_text(len(shown)))
            self.store.add_reminder(now)
