"""開機自動執行（AC-9；prd §6 Platform；Owner 決定 2026-11-07，5B）。

用 Windows 的「目前使用者開機執行」登錄機碼（HKCU\\...\\Run），不需要管理員權限。
- 打包後的版本第一次執行時自動開啟；之後使用者可以在系統匣選單關掉，關掉後不會再自動開回來。
- 開發時（python main.py）預設不開，避免在開發的電腦上留下設定。
"""
import sys
import winreg
from pathlib import Path

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "學習精靈"


def is_frozen() -> bool:
    """是不是 PyInstaller 打包後的版本。"""
    return bool(getattr(sys, "frozen", False))


def launch_command(main_py: Path) -> str:
    if is_frozen():
        return f'"{sys.executable}"'
    pythonw = Path(sys.executable).with_name("pythonw.exe")  # 開機時不要跳出黑色命令列視窗
    return f'"{pythonw}" "{main_py}"'


def get_command(key: str = RUN_KEY, name: str = VALUE_NAME) -> str | None:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
            value, _ = winreg.QueryValueEx(k, name)
            return value
    except FileNotFoundError:
        return None


def is_enabled(key: str = RUN_KEY, name: str = VALUE_NAME) -> bool:
    return get_command(key, name) is not None


def enable(command: str, key: str = RUN_KEY, name: str = VALUE_NAME) -> None:
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key) as k:
        winreg.SetValueEx(k, name, 0, winreg.REG_SZ, command)


def disable(key: str = RUN_KEY, name: str = VALUE_NAME) -> None:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as k:
            winreg.DeleteValue(k, name)
    except FileNotFoundError:
        pass


def refresh(command: str, key: str = RUN_KEY, name: str = VALUE_NAME) -> None:
    """已經開啟時，把路徑更新成現在這一份程式（同學把資料夾搬到別的地方也能用）。"""
    if is_enabled(key, name) and get_command(key, name) != command:
        enable(command, key, name)
