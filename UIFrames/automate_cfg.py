import logging
import time
import datetime

import functions.base
import functions.countdown
from UIFrames.ui_automate_cfg import Ui_AutomateConfigure
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox


class AutomateConfigure(QWidget):
    def __init__(self, config, profile_cfg_ui):
        super(AutomateConfigure, self).__init__()
        self.cfg = config
        self.profile_cfg_ui = profile_cfg_ui
        self.ui = Ui_AutomateConfigure()
        self.ui.setupUi(self)

    def load_val(self):
        self.ui.le_name.setPlaceholderText(functions.countdown.make_auto_sentence(self.cfg))
        self.ui.le_name.setText(self.cfg['name'])

    def save_val(self):
        self.cfg['name'] = self.ui.le_name.text()

    def show(self) -> None:
        self.load_val()
        super(AutomateConfigure, self).show()

    def close(self) -> bool:
        self.save_val()
        super(AutomateConfigure, self).close()
        self.profile_cfg_ui.refresh_automate_ui()
