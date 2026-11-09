"""開機自動執行的開關（A 開頭，第四批）。

用測試專用的登錄機碼 HKCU\\Software\\學習精靈-pytest-…，不碰真正的開機執行設定（...\\Run）。
"""
import uuid
import winreg

import pytest

from leveling import autostart


@pytest.fixture
def key():
    k = rf"Software\學習精靈-pytest-{uuid.uuid4().hex[:8]}"
    yield k
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, k)
    except FileNotFoundError:
        pass


def test_a01_enable_disable_round_trip(key):
    assert autostart.is_enabled(key) is False
    autostart.enable('"C:\\a\\學習精靈.exe"', key)
    assert autostart.is_enabled(key) is True
    assert autostart.get_command(key) == '"C:\\a\\學習精靈.exe"'
    autostart.disable(key)
    assert autostart.is_enabled(key) is False
    autostart.disable(key)  # 已經關掉再關一次也不會出錯


def test_a02_refresh_updates_path_only_when_enabled(key):
    autostart.refresh('"C:\\new\\學習精靈.exe"', key)
    assert autostart.is_enabled(key) is False  # 使用者關掉的不會被開回來

    autostart.enable('"C:\\old\\學習精靈.exe"', key)
    autostart.refresh('"C:\\new\\學習精靈.exe"', key)
    assert autostart.get_command(key) == '"C:\\new\\學習精靈.exe"'


def test_a03_dev_command_uses_pythonw(tmp_path):
    cmd = autostart.launch_command(tmp_path / "main.py")
    assert "pythonw.exe" in cmd and cmd.endswith('main.py"')


def test_a04_default_key_is_current_user_run():
    assert autostart.RUN_KEY == r"Software\Microsoft\Windows\CurrentVersion\Run"
