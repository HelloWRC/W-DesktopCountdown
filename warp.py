# This Python file uses the following encoding: utf-8
import sys

import properties
import wcdapp as wdcd_app
import logging
from PyQt5.QtCore import QEvent

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format=properties.log_styles,
                        datefmt=properties.datefmt,
                        filemode='w',
                        filename='latest.log')
    logger = logging.getLogger(__name__)
    logger.info('Welcome to W-DesktopCountdown %s.', properties.version)
    app = wdcd_app.WDesktopCD([], logger)
    app.sig_phase2_triggered.emit()
    exit_code = app.exec_()  # 启动事件循环
    logging.info('bye! (return code is %s)', exit_code)
    sys.exit(exit_code)
