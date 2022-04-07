import logging
import os
import sys
import functions.base

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt

import traceback
import platform
import functions
import properties
from UIFrames.ui_crash_handle import Ui_CrashHandle


class CrashHandle(QWidget):
    def __init__(self, exctype, value, tb):
        QWidget.__init__(self)
        self.ui = Ui_CrashHandle()
        self.ui.setupUi(self)
        # print(exctype, value, tb)
        report = '''
Traceback (most recent call last):
{}{}: {}

System Information:
    OS: {}
    Platform: {}
    Python: Python {}

APP version: {}
        '''.format(''.join(traceback.format_tb(tb, limit=None)),
                   exctype.__name__, value,
                   platform.platform(),
                   platform.processor(),
                   platform.python_version(),
                   properties.version
                   )
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowTitleHint, False)
        logging.critical('#------ Application Crashed! ------#\n%s', report)
        self.ui.tb_crash_info.setText(report)


    def on_btn_feedback_released(self):
        functions.base.call_browser('https://github.com/HelloWRC/W-DesktopCountdown/issues')

    def on_btn_exit_released(self):
        sys.exit(1)

    def on_btn_ignore_released(self):
        r = QMessageBox.warning(self, '警告！', '如果您选择忽略这个问题，应用可能会在不稳定的状态下继续运行！这可能会导致一些严重问题。除非您知道您在做什么，请您重启或关闭应用。\n您真的要忽略问题而继续吗？',
                                buttons=QMessageBox.Yes | QMessageBox.No, defaultButton=QMessageBox.No)
        if r == QMessageBox.Yes:
            self.close()

    def on_btn_show_log_released(self):
        os.startfile('latest.log')