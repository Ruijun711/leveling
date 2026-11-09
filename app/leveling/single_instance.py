"""防止同時開兩個學習精靈（第四批）。

第二次打開時，連到已經在跑的那個，請它把視窗叫出來，然後自己結束；這樣提醒才不會重複。
用 Qt 的 QLocalServer（Windows 上是 named pipe），只有目前的使用者連得到。
"""
import hashlib
import os
from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket

WAIT_MS = 500


def instance_key(data_dir: Path) -> str:
    """同一個使用者、同一個資料夾只能開一個；開發時用 LEVELING_DATA_DIR 換資料夾就能另外開。"""
    who = os.environ.get("USERNAME", "") + "|" + str(Path(data_dir).resolve()).lower()
    return "leveling-" + hashlib.sha1(who.encode("utf-8")).hexdigest()[:16]


class SingleInstance(QObject):
    activated = Signal()  # 有人又打開了一次 → 主程式把視窗叫出來

    def __init__(self, key: str):
        super().__init__()
        self.key = key
        self.server: QLocalServer | None = None

    def notify_running_instance(self) -> bool:
        """已經有一個在跑：通知它，回傳 True（呼叫的人應該結束）。"""
        sock = QLocalSocket()
        sock.connectToServer(self.key)
        if not sock.waitForConnected(WAIT_MS):
            return False
        sock.write(b"show")
        sock.flush()
        sock.waitForBytesWritten(WAIT_MS)
        sock.disconnectFromServer()
        return True

    def start_server(self) -> bool:
        """成為「第一個」：開始聽其他人的通知。"""
        QLocalServer.removeServer(self.key)  # 上次當掉留下的舊連線名稱
        self.server = QLocalServer(self)
        self.server.setSocketOptions(QLocalServer.UserAccessOption)
        self.server.newConnection.connect(self._on_connection)
        return self.server.listen(self.key)

    def _on_connection(self) -> None:
        while self.server.hasPendingConnections():
            conn = self.server.nextPendingConnection()
            conn.readyRead.connect(lambda c=conn: self._on_ready(c))
            conn.disconnected.connect(conn.deleteLater)
            if conn.bytesAvailable():
                self._on_ready(conn)

    def _on_ready(self, conn) -> None:
        if bytes(conn.readAll()).startswith(b"show"):
            self.activated.emit()
