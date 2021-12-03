from PyQt5.Qt import QApplication
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtGui import QIcon
from UIFrames.countdown import CountdownWin
from UIFrames.tray import SystemTray
import resources_rc as res
import function
import logging
import qt_material
import threading as thd


class WDesktopCD(QApplication):
    def __init__(self, argv, logger: logging.Logger):
        # 程序开始，初始化基本套件
        super().__init__(argv)
        self.cdtest: CountdownWin
        self.tray: QSystemTrayIcon = SystemTray(self)
        self.countdown_win_cls = CountdownWin
        self.logger = logger
        self.logger.info('init phase 1')
        qt_material.apply_stylesheet(self, 'dark_blue.xml')
        res.qInitResources()

    def init_phase2(self):
        # Qt事件处理器启动完毕，开始初始化qt套件
        self.logger.info('init phase 2')
        self.cdtest = CountdownWin(self, 'style.qss', function.ConfigFileMgr('config.json',
                                                                             CountdownWin.countdown_config_default))

    def event(self, event: QEvent) -> bool:
        if event.type() == function.QEventLoopInit_Type:
            self.init_phase2()
            return True
        else:
            return QApplication.event(self, event)

