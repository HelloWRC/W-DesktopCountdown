import logging
import time
import datetime

import functions.base
from UIFrames.ui_automate_cfg import Ui_AutomateConfigure
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox


class AutomateConfigure(QWidget):
    def __init__(self, app):
        super(AutomateConfigure, self).__init__()
        self.app = app
        self.ui = Ui_AutomateConfigure()
        self.ui.setupUi(self)
        self.show()