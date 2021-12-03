import logging

import function
from UIFrames.ui_new_countdown import Ui_NewCountdown
from PyQt5.QtWidgets import QDialog


class NewCountdownWin(QDialog):
    def __init__(self, app):
        super(NewCountdownWin, self).__init__()
        self.app = app
        self.ui = Ui_NewCountdown()
        self.ui.setupUi(self)
        self.show()
        logging.info('new countdown window requested.')

    def on_btn_cancel_clicked(self):
        logging.info('new countdown window cancled.')
        self.close()

