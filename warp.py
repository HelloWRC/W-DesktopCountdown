# This Python file uses the following encoding: utf-8
import sys
import wcdapp as wdcd_app
import function, logging
from PyQt5.QtCore import QEvent

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format=function.log_styles,
                        datefmt=function.datefmt)
    logger = logging.getLogger(__name__)
    logger.info('Welcome to W-DesktopCountdown %s.', function.version)
    app = wdcd_app.WDesktopCD([], logger)
    app.sig_phase2_triggered.emit()
    sys.exit(app.exec_())  # 启动事件循环
