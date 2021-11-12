# This Python file uses the following encoding: utf-8
import sys
import app as wdcd_app
from PyQt5.Qt import QApplication


if __name__ == "__main__":
    app = wdcd_app.WDesktopCD([])
    sys.exit(app.exec())
