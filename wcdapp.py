import os.path
import shutil
import subprocess
import sys

from PyQt5.Qt import QApplication
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QIcon
import qt_material

import UIFrames.splash
import functions.appearance
import functions.base
import functions.countdown
import functions.plugins
import properties
import time
from UIFrames.countdown import CountdownWin
from UIFrames.settings import Settings
from UIFrames.tray import SystemTray
from UIFrames.profilemgr import ProfileMgrUI
from functions.hook import hook_target
import resources_rc as res
import logging
import threading as thd

QEventLoopInit_Type = QEvent.registerEventType()
ProfileUpdatedEvent: int = QEvent.registerEventType()
ProfileFileEvent = QEvent.registerEventType()


class WDesktopCD(QApplication):
    sig_phase2_triggered = pyqtSignal()

    @hook_target('wdcd_app.init_v1')
    def __init__(self, argv, logger: logging.Logger, arg):
        # 程序开始，初始化基本套件
        super().__init__(argv)
        logging.info('----------# INIT PHASE 1 #----------')
        self.splash = UIFrames.splash.Splash(self)
        self.splash.show()
        self.splash.update_status(10, '初始化…')
        self.processEvents()
        self.full_mode = True

        # Enter update
        if arg.update_overwrite is not None:
            self.full_mode = False
            self.install_update(arg.update_overwrite, arg.update_last_version)
            if os.path.exists(arg.update_overwrite):
                sub = subprocess.Popen('{} -u2 {} -ulv {}'.format(arg.update_overwrite, sys.argv[0], arg.update_last_version))
            sys.exit(0)
        if arg.update_remove is not None:
            self.finish_update(arg.update_remove, arg.update_last_version)

        self.arg = arg
        self.starttime = time.time()
        self.app_cfg = functions.base.ConfigFileMgr('settings.json', properties.default_config)
        self.app_cfg.load()
        self.update_mgr = functions.base.UpdateMgr(self, self.app_cfg.cfg['update'])

        if not os.path.exists(properties.cache_prefix):
            os.mkdir(properties.cache_prefix)
        self.profile_mgr_ui = None
        self.profile_mgr: functions.countdown.ProfileMgr
        self.cdtest: CountdownWin
        self.tray: QSystemTrayIcon
        self.countdown_win_cls = CountdownWin
        self.logger = logger
        self.installEventFilter(self)
        res.qInitResources()
        self.sig_phase2_triggered.connect(self.init_phase2)
        self.setQuitOnLastWindowClosed(False)
        self.plugin_mgr = functions.plugins.PluginMgr(self)
        self.p1_time = time.time() - self.starttime
        # self.splash.update_status(30, '第一阶段初始化完成')


    @hook_target('wdcd_app.init_v2')
    def init_phase2(self):
        # Qt事件处理器启动完毕，开始初始化qt套件
        self.logger.info('----------# INIT PHASE 2 #----------')
        self.splash.update_status(30, '加载主题…')
        QIcon.setThemeSearchPaths(QIcon.themeSearchPaths() + [':/resources/icons'])
        self.update_theme()
        self.splash.update_status(50, '加载内置页面')
        self.settings_ui: Settings = Settings(self.app_cfg, self)
        self.profile_mgr = functions.countdown.ProfileMgr(self)
        self.profile_mgr_ui = ProfileMgrUI(self)
        self.tray = SystemTray(self)
        self.tray.show()
        self.profile_mgr.init_countdown()
        if self.app_cfg.cfg['update']['auto_update']['auto_check']:
            self.settings_ui.on_btn_check_update_released()
            if self.update_mgr.status == functions.base.UpdateMgr.UpdateAvailable:
                self.tray.showMessage('检测到更新', '转到应用设置页面查看详细。')
        if len(self.profile_mgr.profiles) <= 1:
            self.tray.showMessage('W-DesktopCountdown正在后台运行。', '双击系统托盘图标以显示本应用。')
        if self.arg.update_remove is not None:
            self.tray.showMessage('W-DesktopCountdown更新完成。', '已更新到最新版本{}。'.format(properties.version))
        self.plugin_mgr.load_v2()
        # self.cdtest = CountdownWin(self, 'style.qss', function.ConfigFileMgr('config.json',
        #                                                                      CountdownWin.countdown_config_default))
        self.p2_time = time.time() - self.starttime - self.p1_time
        self.final_time = time.time() - self.starttime
        # print('加载时间：{}s，p1：{}s，p2：{}s'.format(self.final_time, self.p1_time, self.p2_time))
        self.splash.update_status(100, '完成')
        self.splash.close()
        self.logger.info('----------# INIT DONE #----------')

    def install_update(self, update_overwrite, update_last_version):
        if not os.path.exists(update_overwrite):
            logging.error('Raw file not exists: %s', update_overwrite)
            QMessageBox.critical(None, '更新失败', '找不到要替换的文件，更新没有进行。')
            return

        logging.info('Installing update...(raw file: %s) (%s -> %s)', update_overwrite, update_last_version,
                     properties.version_id)

        logging.info('Copying file: %s -> %s', sys.argv[0], update_overwrite)
        self.splash.update_status(15, '正在复制文件…')
        while True:
            try:
                shutil.copy(sys.argv[0], update_overwrite)
                break
            except:
                pass
        self.splash.update_status(80, '正在完成更新')

    def finish_update(self, update_remove, update_last_version):
        logging.info('Finishing updating...')
        self.splash.update_status(20, '正在完成更新…')
        if not os.path.exists(update_remove):
            logging.warning('Update file not exists: %s', update_remove)
            return
        os.remove(update_remove)
        
    def on_tray_clicked(self, reason):
        logging.debug('tray clicked, reason: %s', reason)

    @hook_target('wdcd_app.update_theme')
    def update_theme(self, config=None):
        if self.arg.no_theme:
            return

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
            functions.appearance.gen_custom_theme(properties.cache_prefix + 'custom-theme.xml', accent_color, dark_mode)
            theme_name = properties.cache_prefix + 'custom-theme.xml'
        qt_material.apply_stylesheet(self,
                                     theme=theme_name,
                                     invert_secondary=use_sc,
                                     extra=properties.extra_ui_cfg)
        QIcon.setThemeName('breeze-{}'.format(properties.ld_themes[config['appearance']['ld_style']]))

    @hook_target('wdcd_app.quit')
    def quit(self, stat=None) -> None:
        logging.info('Stopping!')
        if self.full_mode:
            logging.info('Closing opened windows')
            for i in (self.profile_mgr_ui, self.settings_ui):
                i.close()

            self.plugin_mgr.on_app_quit()
            self.profile_mgr.unload_all()
            logging.info('Writing config')
            self.update_mgr.save_config()
            self.app_cfg.write()
            self.update_mgr.update_progress()
        super(WDesktopCD, self).quit()
