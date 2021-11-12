from PyQt5.Qt import QApplication
import threading as thd


class WDesktopCD(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

