from PyQt5.Qt import QApplication
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtGui import QIcon

import functions.appearance
import functions.base
import functions.countdown
import functions.plugins
import properties
from UIFrames.countdown import CountdownWin
from UIFrames.settings import Settings
from UIFrames.tray import SystemTray
from UIFrames.profilemgr import ProfileMgrUI
import resources_rc as res
import logging
import qt_material
import threading as thd

QEventLoopInit_Type = QEvent.registerEventType()
ProfileUpdatedEvent = QEvent.registerEventType()
ProfileFileEvent = QEvent.registerEventType()


class WDesktopCD(QApplication):
    sig_phase2_triggered = pyqtSignal()

    def __init__(self, argv, logger: logging.Logger):
        # 程序开始，初始化基本套件
        super().__init__(argv)
        self.plugin_mgr = functions.plugins.PluginMgr()
        self.profile_mgr_ui = None
        self.profile_mgr: functions.countdown.ProfileMgr
        self.cdtest: CountdownWin
        self.app_cfg = functions.base.ConfigFileMgr('settings.json', properties.default_config)
        self.app_cfg.load()
        self.settings_ui: Settings = Settings(self.app_cfg, self)
        self.tray: QSystemTrayIcon
        self.countdown_win_cls = CountdownWin
        self.logger = logger
        self.logger.info('init phase 1')
        self.installEventFilter(self)
        res.qInitResources()
        self.sig_phase2_triggered.connect(self.init_phase2)
        self.setQuitOnLastWindowClosed(False)

    def init_phase2(self):
        # Qt事件处理器启动完毕，开始初始化qt套件
        QIcon.setThemeSearchPaths(QIcon.themeSearchPaths() + [':/resources/icons'])
        self.update_theme()
        self.logger.info('init phase 2')
        self.profile_mgr = functions.countdown.ProfileMgr(self)
        self.profile_mgr_ui = ProfileMgrUI(self)
        self.tray = SystemTray(self)
        self.tray.show()
        if len(self.profile_mgr.profiles) <= 1:
            self.tray.showMessage('W-DesktopCountdown正在后台运行。', '双击系统托盘图标以显示本应用。')
        # self.cdtest = CountdownWin(self, 'style.qss', function.ConfigFileMgr('config.json',
        #                                                                      CountdownWin.countdown_config_default))
        
    def on_tray_clicked(self, reason):
        logging.debug('tray clicked, reason: %s', reason)

    def update_theme(self, config=None):
        logging.info('Updating app theme')
        if config is None:
            config = self.app_cfg.cfg
        properties.extra_ui_cfg['font_family'] = config['appearance']['custom_font']
        if properties.ld_themes[config['appearance']['ld_style']] == 'light':
            use_sc = True
        else:
            use_sc = False
        theme_name = '{}_{}.xml'.format(properties.ld_themes[config['appearance']['ld_style']],
                                        properties.default_colors[config['appearance']['color_theme']['theme']])
        if config['appearance']['color_theme']['type'] != 0:  # 主题值
            if config['appearance']['color_theme']['type'] == 1:
                accent_color = properties.system_color
            elif config['appearance']['color_theme']['type'] == 2:
                accent_color = config['appearance']['color_theme']['color']
            else:
                accent_color = properties.system_color
            if properties.ld_themes[config['appearance']['ld_style']] == 'dark':
                dark_mode = True
            else:
                dark_mode = False
            functions.appearance.gen_custom_theme('custom-theme.xml', accent_color, dark_mode)
            theme_name = 'custom-theme.xml'
        qt_material.apply_stylesheet(self,
                                     theme=theme_name,
                                     invert_secondary=use_sc,
                                     extra=properties.extra_ui_cfg)
        QIcon.setThemeName('breeze-{}'.format(properties.ld_themes[config['appearance']['ld_style']]))

