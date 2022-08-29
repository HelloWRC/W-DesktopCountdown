import os

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.Qt import QAction

import properties
from UIFrames.new_countdown import NewCountdownWin
from UIFrames.profilemgr import ProfileMgrUI
import resources_rc as res
import time
import logging


class SystemTray(QSystemTrayIcon):
    def __init__(self, app):
        import wcdapp
        super().__init__(app)
        self.app: wcdapp.WDesktopCD = app
        self.setObjectName('SystemTray')
        self.setToolTip('W-DesktopCountdown')
        self.setIcon(QIcon('://resources/icons/colorful/logo.svg'))
        self.menu = QMenu('W-DesktopCountdown {}'.format(properties.version))

        self.menu_title = QAction('W-DesktopCountdown {}'.format(properties.version))
        self.menu_title.setEnabled(False)
        self.menu.addAction(self.menu_title)

        self.show_pmui = QAction('倒计时管理', triggered=self.open_pmui)
        self.menu.addAction(self.show_pmui)

        self.settings = QAction('应用设置', triggered=self.app.settings_ui.show)
        self.menu.addAction(self.settings)

        self.help = QAction('帮助', triggered=lambda: os.startfile('https://github.com/HelloWRC/W-DesktopCountdown/wiki'))
        self.menu.addAction(self.help)

        self.exit = QAction('退出', triggered=self.app.quit)
        self.menu.addAction(self.exit)

        self.setContextMenu(self.menu)
        self.activated.connect(self.on_SystemTray_activated)

    def on_SystemTray_activated(self, reason):
        logging.debug('tray clicked, reason: %s', reason)
        if reason == QSystemTrayIcon.DoubleClick:
            self.open_pmui()

    def new_countdown(self):
        self.ncd = NewCountdownWin(self.app)
        # time.sleep(0.001)

    def open_pmui(self):
        self.app.profile_mgr_ui.show()