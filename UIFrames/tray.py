from PyQt5.QtWidgets import QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.Qt import QAction
from UIFrames.new_countdown import NewCountdownWin
import resources_rc as res
import time
import logging
import function


class SystemTray(QSystemTrayIcon):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.setObjectName('SystemTray')
        self.setToolTip('W-DesktopCountdown')
        self.setIcon(QIcon('://resources/icons/colorful/logo.svg'))
        self.menu = QMenu('W-DesktopCountdown {}'.format(function.version))

        self.menu_title = QAction('W-DesktopCountdown {}'.format(function.version))
        self.menu_title.setEnabled(False)
        self.menu.addAction(self.menu_title)

        self.add_profile = QAction('添加倒计时', triggered=self.new_countdown)
        self.menu.addAction(self.add_profile)

        self.setContextMenu(self.menu)
        self.show()

    def on_SystemTray_activated(self, reason):
        logging.debug('tray clicked, reason: %s', reason)

    def new_countdown(self):
        self.ncd = NewCountdownWin(self.app)
        # time.sleep(0.001)