import logging

import function
from UIFrames.ui_new_countdown import Ui_NewCountdown
from PyQt5.QtWidgets import QWidget


class NewCountdownWin(QWidget):
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

    def on_btn_confirm_released(self):
        profile_name = self.ui.le_input.text()
        logging.debug('new profile: %s', profile_name)
        if self.check_filename(profile_name):
            logging.debug('passed filename check: %s', profile_name)
        else:
            pass

    def check_filename(self, filename) -> bool:
        pass

