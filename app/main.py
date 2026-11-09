"""學習精靈 · 階段 1

執行（在 app 資料夾）：
    .venv\\Scripts\\python main.py

開發用的環境變數：
    LEVELING_DATA_DIR       資料放在別的資料夾（預設 %APPDATA%\\學習精靈），試用時不會弄亂正式資料
    LEVELING_REMINDER_TEST  設成 1：提醒的 24 小時改成 2 分鐘、12 小時改成 1 分鐘，每 5 秒檢查（NFR A3）
    LEVELING_OFFLINE        設成 1：不下載題庫，模擬沒網路（AC-12）

還沒做（第四批）：打包成安裝檔、開機自動執行（AC-9）、只允許開一個學習精靈。
"""
import os
import sys
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PySide6.QtCore import QObject, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from leveling import messages
from leveling.bank_sync import OfflineError, SyncStatus, load_bundled_bank, should_check, sync_bank
from leveling.storage import SqliteStore
from leveling.ui.main_window import MainWindow
from leveling.ui.reminder import ReminderBubble, ReminderScheduler, draw_sprite

APP_DIR = Path(__file__).resolve().parent


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def data_dir() -> Path:
    if os.environ.get("LEVELING_DATA_DIR"):
        return Path(os.environ["LEVELING_DATA_DIR"])
    return Path(os.environ.get("APPDATA", Path.home())) / "學習精靈"


def make_icon() -> QIcon:
    pix = QPixmap(64, 64)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    draw_sprite(p, QRectF(4, 4, 56, 56))
    p.end()
    return QIcon(pix)


class BankSyncer(QObject):
    """在背景下載題庫，不讓畫面等（c4-diagram R2）。背景用自己的資料庫連線。"""
    finished = Signal(object, int)  # (SyncStatus, 目前題數)

    def __init__(self, db_path: Path):
        super().__init__()
        self.db_path = db_path
        self.running = False

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self) -> None:
        status, count = SyncStatus.DOWNLOAD_FAILED, 0
        try:
            store = SqliteStore(self.db_path, utcnow())
            try:
                if os.environ.get("LEVELING_OFFLINE") == "1":
                    def fetch(_url):
                        raise OfflineError("LEVELING_OFFLINE=1")
                    status = sync_bank(store, utcnow(), fetch)
                else:
                    status = sync_bank(store, utcnow())
                count = len(store.active_questions())
            finally:
                store.close()
        except Exception:  # 下載題庫出任何問題都不能讓程式當掉；本機題庫照常能用
            status = SyncStatus.DOWNLOAD_FAILED
        finally:
            self.running = False
        self.finished.emit(status, count)


STATUS_TEXT = {
    SyncStatus.UP_TO_DATE: lambda n: messages.STATUS_UP_TO_DATE,
    SyncStatus.UPDATED: messages.status_updated,
    SyncStatus.OFFLINE: lambda n: messages.STATUS_OFFLINE,
    SyncStatus.DOWNLOAD_FAILED: lambda n: messages.STATUS_DOWNLOAD_FAILED,
    SyncStatus.INVALID: lambda n: messages.BANK_INVALID,
}


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("學習精靈")
    app.setQuitOnLastWindowClosed(False)  # 視窗關掉後程式繼續在系統匣跑，才收得到提醒
    icon = make_icon()
    app.setWindowIcon(icon)

    db_path = data_dir() / "leveling.db"
    store = SqliteStore(db_path, utcnow())
    load_bundled_bank(store, APP_DIR / "data", utcnow())  # 安裝檔附的基本題庫（AC-12）

    window = MainWindow(store)
    window.set_status("檢查新題目中…")

    # 系統匣（Owner 決定 2026-11-09，3A：按 X 縮到這裡，按右鍵「結束」才真的關掉）
    tray = QSystemTrayIcon(icon)
    tray.setToolTip("學習精靈")
    def quit_app() -> None:
        # Qt 6 的 quit() 會先關所有視窗；作答視窗按 X 只會縮到系統匣（會擋下關閉），
        # 所以要先把這個設定關掉，不然按「結束」關不掉（2026-11-09 Avi 回報）
        window.hide_on_close = False
        app.quit()

    menu = QMenu()
    open_action = QAction("開啟學習精靈", menu, triggered=window.show_and_raise)
    export_action = QAction("匯出作答紀錄", menu, triggered=window.export_records)
    quit_action = QAction("結束", menu, triggered=quit_app)
    menu.addActions([open_action, export_action])
    menu.addSeparator()
    menu.addAction(quit_action)
    tray.setContextMenu(menu)
    tray.activated.connect(
        lambda reason: window.show_and_raise() if reason == QSystemTrayIcon.Trigger else None)
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray.show()
        window.hide_on_close = True

    # 提醒
    bubble = ReminderBubble()
    bubble.practice_clicked.connect(window.show_and_raise)
    if os.environ.get("LEVELING_REMINDER_TEST") == "1":
        scheduler = ReminderScheduler(store, bubble, timedelta(minutes=2), timedelta(minutes=1), check_ms=5_000)
    else:
        scheduler = ReminderScheduler(store, bubble)
    scheduler.start()

    # 題庫：開機時檢查一次，之後每小時看一下是不是滿 24 小時了（1C）
    syncer = BankSyncer(db_path)
    syncer.finished.connect(lambda status, n: window.set_status(STATUS_TEXT[status](n)))
    syncer.start()
    sync_timer = QTimer()
    sync_timer.setInterval(60 * 60 * 1000)
    sync_timer.timeout.connect(
        lambda: syncer.start() if should_check(store.last_checked_at(), utcnow(), at_startup=False) else None)
    sync_timer.start()

    window.load_next()
    window.show()
    code = app.exec()
    store.close()
    return code


if __name__ == "__main__":
    sys.exit(main())
