# This Python file uses the following encoding: utf-8
import sys
import wcdapp as wdcd_app
import function, logging
from PyQt5.QtCore import QEvent

if __name__ == "__main__":
    logging.basicConfig(filename='log-cast.log', level=logging.DEBUG,
                        format='[%(asctime)s] [%(module)s(%(lineno)s)/%(threadName)s/%(funcName)s] [%(levelname)s] %(message)s',
                        filemode='w',
                        datefmt='%Y/%m/%d %H:%M:%S')
    logger = logging.getLogger(__name__)
    logger.info('Welcome to W-DesktopCountdown %s.', function.version)
    app = wdcd_app.WDesktopCD([], logger)
    app.postEvent(app, function.QEventLoopInit())
    sys.exit(app.exec())  # 启动事件循环
