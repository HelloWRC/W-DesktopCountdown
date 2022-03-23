import logging
import time
import datetime

import functions.base
import properties
from UIFrames.ui_splash import Ui_Form
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from functions.hook import hook_target

path_root = 'UIFrames.splash.'


class Splash(QWidget):
    @hook_target('Splash.__init__')
    def __init__(self, app):
        super(Splash, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.app = app
        self.ui.lb_version.setText(self.ui.lb_version.text().format(properties.version))
        self.ui.logo.setScaledContents(True)
        self.ui.logo.setFixedSize(150, 150)
        self.ui.logo.setPixmap(QPixmap(":/resources/icons/colorful/logo.svg"))
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

    @hook_target('Splash.update_status')
    def update_status(self, process: int, text: str = None):
        self.ui.progress.setValue(int(process))
        if text is not None:
            self.ui.lb_stat.setText(text)
        self.app.processEvents()


