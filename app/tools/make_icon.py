"""把精靈畫成 .ico，給打包後的 學習精靈.exe 當圖示。用法：python tools/make_icon.py 輸出路徑.ico"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QRectF, Qt  # noqa: E402
from PySide6.QtGui import QGuiApplication, QImage, QPainter  # noqa: E402

from leveling.ui.reminder import draw_sprite  # noqa: E402

app = QGuiApplication([])
img = QImage(256, 256, QImage.Format_ARGB32)
img.fill(Qt.transparent)
p = QPainter(img)
draw_sprite(p, QRectF(8, 8, 240, 240))
p.end()
out = Path(sys.argv[1])
out.parent.mkdir(parents=True, exist_ok=True)
if not img.save(str(out), "ICO"):
    sys.exit(f"存不了圖示：{out}")
print(f"圖示：{out}")
