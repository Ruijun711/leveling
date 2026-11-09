"""防止同時開兩個（I 開頭，第四批）。

「第二個」用另一個真的程式（subprocess）來開，和實際情況一樣；
兩個放在同一個程式裡會互相卡住，測不出來。
"""
import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication

from leveling.single_instance import SingleInstance, instance_key

APP_DIR = Path(__file__).resolve().parents[1]
CLIENT = (
    "import sys; sys.path.insert(0, sys.argv[2]);"
    "from PySide6.QtCore import QCoreApplication; app = QCoreApplication([]);"
    "from leveling.single_instance import SingleInstance;"
    "sys.exit(0 if SingleInstance(sys.argv[1]).notify_running_instance() else 3)"
)


def _launch_second(key: str) -> subprocess.Popen:
    return subprocess.Popen([sys.executable, "-c", CLIENT, key, str(APP_DIR)])


@pytest.fixture(scope="module")
def qapp():
    return QCoreApplication.instance() or QCoreApplication([])


def _wait(qapp, cond, seconds=3.0):
    end = time.time() + seconds
    while time.time() < end and not cond():
        qapp.processEvents()
        time.sleep(0.01)
    return cond()


def test_i01_second_launch_notifies_first(qapp):
    key = f"leveling-pytest-{uuid.uuid4().hex[:8]}"
    first = SingleInstance(key)
    assert first.notify_running_instance() is False  # 還沒有人在跑
    assert first.start_server() is True

    shown = []
    first.activated.connect(lambda: shown.append(True))

    second = _launch_second(key)
    assert _wait(qapp, lambda: shown, seconds=10), "第一個沒有收到「叫出視窗」"
    assert _wait(qapp, lambda: second.poll() is not None, seconds=10)
    assert second.returncode == 0  # 第二個知道已經有一個在跑，要結束
    first.server.close()


def test_i02_after_first_closes_a_new_one_can_start(qapp):
    key = f"leveling-pytest-{uuid.uuid4().hex[:8]}"
    first = SingleInstance(key)
    first.start_server()
    first.server.close()

    again = SingleInstance(key)
    assert again.notify_running_instance() is False
    assert again.start_server() is True
    again.server.close()


def test_i03_key_differs_by_data_dir(tmp_path):
    assert instance_key(tmp_path / "a") != instance_key(tmp_path / "b")
    assert instance_key(tmp_path / "a") == instance_key(tmp_path / "a")
