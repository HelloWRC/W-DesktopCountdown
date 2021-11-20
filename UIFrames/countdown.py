import function
import wcdapp
from UIFrames.ui_countdown import Ui_Countdown
from PyQt5.QtWidgets import QWidget


class CountdownWin(QWidget):
    def __init__(self, app):
        super(CountdownWin, self).__init__()
        self.app = app
        self.app.logger.info('created countdown window')
        self.ui = Ui_Countdown()
        self.ui.setupUi(self)
