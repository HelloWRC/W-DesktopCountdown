import logging
import time
import datetime

import functions.base
import properties
from UIFrames.ui_splash import Ui_Form
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt


class Splash(QWidget):
    def __init__(self, app):
        super(Splash, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.app = app
        self.ui.lb_version.setText(self.ui.lb_version.text().format(properties.version))
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

    def update_status(self, process: int, text: str = None):
        self.ui.progress.setValue(int(process))
        if text is not None:
            self.ui.lb_stat.setText(text)
        self.app.processEvents()


