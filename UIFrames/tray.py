from PyQt5.QtWidgets import QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.Qt import QAction
from UIFrames.new_countdown import NewCountdownWin
from UIFrames.profilemgr import ProfileMgrUI
import resources_rc as res
import time
import logging
import function


class SystemTray(QSystemTrayIcon):
    def __init__(self, app):
        import wcdapp
        super().__init__(app)
        self.app: wcdapp.WDesktopCD = app
        self.setObjectName('SystemTray')
        self.setToolTip('W-DesktopCountdown')
        self.setIcon(QIcon('://resources/icons/colorful/logo.svg'))
        self.menu = QMenu('W-DesktopCountdown {}'.format(function.version))

        self.menu_title = QAction('W-DesktopCountdown {}'.format(function.version))
        self.menu_title.setEnabled(False)
        self.menu.addAction(self.menu_title)

        self.show_pmui = QAction('显示', triggered=self.open_pmui)
        self.menu.addAction(self.show_pmui)

        self.add_profile = QAction('添加倒计时', triggered=self.new_countdown)
        self.menu.addAction(self.add_profile)

        self.exit = QAction('退出', triggered=self.app.exit)
        self.menu.addAction(self.exit)

        self.setContextMenu(self.menu)
        self.show()

    def on_SystemTray_activated(self, reason):
        logging.debug('tray clicked, reason: %s', reason)

    def new_countdown(self):
        self.ncd = NewCountdownWin(self.app)
        # time.sleep(0.001)

    def open_pmui(self):
        self.app.profile_mgr_ui.show()