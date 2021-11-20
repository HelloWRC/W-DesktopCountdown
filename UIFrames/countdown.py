import function
import wcdapp
from UIFrames.ui_countdown import Ui_Countdown
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QStyle


class CountdownWin(QWidget):
    def __init__(self, app, qss_path: str):
        super(CountdownWin, self).__init__()
        self.setStyleSheet(function.get_qss(qss_path))
        self.app = app
        self.app.logger.info('created countdown window')
        self.ui = Ui_Countdown()
        self.ui.setupUi(self)
        self.raw_h = 0


