from PyQt5.Qt import QApplication
from PyQt5.QtCore import QEvent
from UIFrames.countdown import CountdownWin
import function
import logging
import threading as thd


class WDesktopCD(QApplication):
    def __init__(self, argv, logger: logging.Logger):
        # 程序开始，初始化基本套件
        super().__init__(argv)
        self.logger = logger
        self.logger.info('init phase 1')

    def init_phase2(self):
        # Qt事件处理器启动完毕，开始初始化qt套件
        self.logger.info('init phase 2')

        self.cdtest = CountdownWin(self)
        self.cdtest.show()

    def event(self, event: QEvent) -> bool:
        if event.type() == function.QEventLoopInit_Type:
            self.init_phase2()
            return True
        else:
            return QApplication.event(self, event)

