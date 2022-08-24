import logging
from datetime import datetime

import time
import datetime
import threading
import ctypes

import functions.appearance
import functions.base
import functions.countdown
import properties
from UIFrames.ui_countdown import Ui_Countdown
from UIFrames.profile_config_ui import ProfileConfigUI
from UIFrames.toast import Toast
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import QEvent, QObject, Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QMouseEvent, QKeyEvent
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QPoint
from PyQt5.Qt import QRectF
from PyQt5.QtGui import QCursor

from functions.hook import hook_target, class_hook_target

path_root = 'ui.countdown.'

window_update_event = QEvent.registerEventType()


class CountdownWin(QWidget):
    countdown_config_default = properties.countdown_config_default

    @hook_target(path_root + 'win.__init__')
    def __init__(self, app, name, config: functions.base.ConfigFileMgr):
        import wcdapp
        self.app: wcdapp.WDesktopCD = app
        self.hook_mgr = functions.hook.ClassHookMgr()
        self.name = name
        super(CountdownWin, self).__init__()
        self.stopped: bool = False
        self.win_mode = 0
        self.mouse_tran = False
        self.no_bg = False
        self.drag_flag = False
        self.m_pos = None
        self.title_visible = True
        self.cfg = config
        self.auto_align_enabled_temp = True
        self.app.logger.info('created countdown window')
        # self.windowHandle().screenChanged.connect(self.__onScreenChanged)

        self.ui = Ui_Countdown()
        self.ui.setupUi(self)
        self.update_timer = QTimer()
        self.update_timer.setInterval(50)
        self.update_timer.timeout.connect(self.update_content)
        self.em = functions.appearance.EffectManager(self, self.app, self.cfg)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowTitleHint, False)
        self.enabled = None
        for i in (
            self.ui.action_open_config,
            self.ui.action_info
        ):
            self.addAction(i)

        self.auto_mgr = functions.countdown.AutomateMgr(self.app, self)
        self.load_config()
        self.config_ui = ProfileConfigUI(self.app, self.name, self.cfg, self.load_config)
        self.installEventFilter(self)
        self.show()

    @hook_target(path_root + 'win.show')
    @class_hook_target('show')
    def show(self) -> None:
        if not self.cfg.cfg['enabled']:
            return
        self.update_timer.start()
        super(CountdownWin, self).show()

    @hook_target(path_root + 'win.load_config')
    @class_hook_target('load_config')
    def load_config(self):
        self.cfg.load(True, properties.countdown_skipped)
        self.auto_mgr.load_config(self.cfg.cfg['automate'], bool(self.cfg.cfg['automate_enabled'] and self.cfg.cfg['trusted']))
        self.em.load_config(self.cfg.cfg['effects'])
        # 应用配置
        # 窗口
        self.setWindowTitle(self.cfg.cfg['countdown']['title'])
        self.resize(self.cfg.cfg['window']['width'], self.cfg.cfg['window']['height'])
        self.move(self.cfg.cfg['window']['pos_x'], self.cfg.cfg['window']['pos_y'])
        self.ui.lb_event.setText(self.cfg.cfg['countdown']['title'])
        self.set_win_mode(self.cfg.cfg['window']['window_mode'])
        self.set_window_title_visible(self.cfg.cfg['window']['show_title_bar'])
        self.set_countdown_enabled(self.cfg.cfg['enabled'])
        self.setWindowFlag(Qt.Tool, self.cfg.cfg['window']['skip_taskbar'])

        # self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.update_content()
        self.write_config()
        self.setStyleSheet(functions.appearance.mk_qss(self.cfg.cfg['style'], self.cfg.cfg['style_enabled']))
        self.show()
        logging.info('loaded config of %s', self.cfg.filename)

    @hook_target(path_root + 'win.unload')
    @class_hook_target('unload')
    def unload(self):
        self.close()
        self.em.unload_all()

    def set_window_title_visible(self, stat: bool):
        if stat:
            self.setWindowFlag(Qt.FramelessWindowHint, False)
        else:
            self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.title_visible = stat
        self.show()

    def set_countdown_enabled(self, stat):
        if stat == self.enabled:
            return
        if stat:
            self.show()
        else:
            self.close()
        self.enabled = stat
        self.app.plugin_mgr.on_countdown_state_changed(self, stat)
        self.em.on_state_changed(self.enabled)

    @hook_target(path_root + 'win.write_config')
    @class_hook_target('write_config')
    def write_config(self):
        self.cfg.cfg['window']['width'] = self.geometry().width()
        self.cfg.cfg['window']['height'] = self.geometry().height()
        self.cfg.cfg['window']['pos_x'] = self.pos().x()
        self.cfg.cfg['window']['pos_y'] = self.pos().y()
        self.cfg.cfg['window']['window_mode'] = self.win_mode
        self.cfg.cfg['window']['show_title_bar'] = self.title_visible
        self.cfg.write()
        logging.info('saved config of %s', self.cfg.filename)

    @hook_target(path_root + 'win.update_content')
    @class_hook_target('update_content')
    def update_content(self):
        self.ui.lb_targetddate.setText(time.strftime(self.cfg.cfg['display']['target_format'],
                                                     time.localtime(self.cfg.cfg['countdown']['end'])))  # target
        if time.time() > self.cfg.cfg['countdown']['end']:  # 计时是否结束
            self.ui.lb_CountDown.setText(self.cfg.cfg['display']['end_text'])  # show end text
        elif time.time() < self.cfg.cfg['countdown']['start']:
            self.ui.lb_CountDown.setText(self.cfg.cfg['display']['start_text'])  # show start text
        else:
            end_dt = datetime.datetime.fromtimestamp(self.cfg.cfg['countdown']['end'])
            now_dt: datetime = datetime.datetime.now()
            delta = end_dt - now_dt
            self.ui.lb_CountDown.setText(
                functions.countdown.strfdelta(delta, self.cfg.cfg['display']['countdown_format']))

        # progressbar
        self.ui.progressBar.setVisible(self.cfg.cfg['display']['show_progress_bar'])
        self.ui.progressBar.setMaximum(self.cfg.cfg['countdown']['end'] - self.cfg.cfg['countdown']['start'])
        if time.time() > self.cfg.cfg['countdown']['end']:
            self.ui.progressBar.setValue(self.ui.progressBar.maximum())
        else:
            if self.cfg.cfg['display']['reverse_progress_bar']:
                self.ui.progressBar.setValue(int(self.cfg.cfg['countdown']['end'] - time.time()))
            else:
                self.ui.progressBar.setValue(int(time.time() - self.cfg.cfg['countdown']['start']))
        self.auto_mgr.update()

    @hook_target(path_root + 'win.eventFilter')
    @class_hook_target('eventFilter')
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self and event.type() == event.Close:
            self.update_timer.stop()
            logging.info('countdown window %s closed', self.cfg.cfg['countdown']['title'])
            return True
        elif watched == self and event.type() == event.MouseButtonDblClick:
            self.set_window_title_visible(not self.title_visible)
            self.write_config()
        # print(watched, event)
        self.em.on_event(watched, event)
        return super(CountdownWin, self).eventFilter(watched, event)

    def set_win_mode(self, level: int):
        """
        @level: 窗口层级
         0: 正常
         -1: 置底
         1:置顶
        """

        if level != self.win_mode:
            self.setWindowFlag(Qt.WindowStaysOnBottomHint, False)
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
            if level == -1:
                self.setWindowFlag(Qt.WindowStaysOnBottomHint)
            elif level == 0:
                self.setWindowFlag(Qt.Widget)
            elif level == 1:
                self.setWindowFlag(Qt.WindowStaysOnTopHint)
            else:
                raise ValueError('Values must be -1, 0 or 1')
            self.win_mode = level
            self.show()

    @pyqtSlot(bool)
    def on_action_open_config_triggered(self, trigger_type: bool):
        self.write_config()
        if not trigger_type:
            self.config_ui.show()

    @pyqtSlot(bool)
    def on_action_info_triggered(self, trigger_type: bool):
        if not trigger_type:
            QMessageBox.information(self, '操作说明', '鼠标双击 - 显示/隐藏标题栏\n鼠标右键 - 菜单\n鼠标拖拽可移动倒计时')

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.drag_flag = True
        self.m_pos = event.globalPos() - self.pos()
        event.accept()
        self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if Qt.LeftButton and self.drag_flag:
            target = event.globalPos() - self.m_pos
            if self.app.app_cfg.cfg['basic']['align_enabled'] and self.auto_align_enabled_temp:  # Try to align to other countdowns
                align_target = QPoint(target)
                target_x = target.x()
                target_y = target.y()
                width = self.size().width()
                height = self.size().height()
                align_offset = self.app.app_cfg.cfg['basic']['align_offset']
                # align x
                align_x = -114514
                align_x_2 = -114514
                align_w = list(self.app.profile_mgr.countdowns_win.values())[0].size().width()
                for i in self.app.profile_mgr.countdowns_win.values():  # Find nearset window
                    if i is self:
                        continue
                    if abs(align_x - target_x) > abs(i.frameGeometry().x() - target_x):
                        align_x = i.frameGeometry().x()
                        # print('X near countdown:', i.name)
                    if abs(align_x_2 + width - target_x - width) > abs(i.frameGeometry().x() + i.size().width() - target_x):
                        align_x_2 = i.frameGeometry().x() + i.size().width() - width
                        # print('X w2 near countdown')
                    # print(align_x + i.size().width() - target_x, i.frameGeometry().x() + i.size().width() - target_x)
                if abs(align_x - target_x) < abs(align_x_2 - target_x):
                    if abs(align_x - target_x) <= align_offset:
                        align_target.setX(align_x)
                        # print('aligned to', align_x)
                else:
                    if abs(align_x_2 - target_x) <= align_offset:
                        align_target.setX(align_x_2)
                # align y
                # align_y = list(self.app.profile_mgr.countdowns_win.values())[0].pos().y()
                align_y = -114514
                align_y_2 = -114514
                for i in self.app.profile_mgr.countdowns_win.values():
                    if i is self:
                        continue
                    if abs(align_y - target_y) > abs(i.frameGeometry().y() - target_y):
                        align_y = i.frameGeometry().y()
                        # print('Y near countdown:', i.name)
                    if abs(align_y_2 + height - target_y - width) > abs(i.frameGeometry().y() + i.size().height() - target_y):
                        align_y_2 = i.frameGeometry().y() + i.size().height() - height
                if abs(align_y - target_y) < abs(align_y_2 - target_y):
                    if abs(align_y - target_y) <= align_offset:
                        align_target.setY(align_y)
                else:
                    if abs(align_y_2 - target_y) <= align_offset:
                        align_target.setY(align_y_2)
                # check
                target = align_target
                # print(align_y - y, align_x - x)
                # print('===========================')
            self.move(target)
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.drag_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.write_config()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Alt:
            self.auto_align_enabled_temp = False

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Alt:
            self.auto_align_enabled_temp = True
