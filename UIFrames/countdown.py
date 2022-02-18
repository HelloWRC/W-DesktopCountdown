import logging
from datetime import datetime

import function
import time
import datetime
import threading
import ctypes

import properties
from UIFrames.ui_countdown import Ui_Countdown
from UIFrames.profile_config_ui import ProfileConfigUI
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QEvent, QObject, Qt, QThread, pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

window_update_event = QEvent.registerEventType()


class CountdownWin(QWidget):
    countdown_config_default = properties.countdown_config_default
    widget_list = [
        'hl_description', 'lb_event', 'lb_targetdate', 'lb_text1', 'lb_text2', 'lb_CountDown', 'progressBar'
    ]

    def __init__(self, app, name, qss_path: str, config: function.ConfigFileMgr):
        self.app = app
        self.name = name
        super(CountdownWin, self).__init__()
        self.setStyleSheet(function.get_qss(qss_path))
        self.stopped: bool = False
        self.win_mode = 0
        self.drag_flag = False
        self.m_pos = None
        self.title_visible = True
        self.cfg = config
        self.app.logger.info('created countdown window')

        self.update_thread = UpdateThread()
        self.update_thread.setPriority(QThread.IdlePriority)
        self.update_thread.sig_update.connect(self.update_content)
        self.ui = Ui_Countdown()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowTitleHint, False)
        self.enabled = None
        for i in (
            self.ui.action_open_config,
            self.ui.action_save_profile
        ):
            self.addAction(i)

        self.load_config()
        self.config_ui = ProfileConfigUI(self.app, self.name, self.cfg, self.load_config)
        self.installEventFilter(self)

    def show(self) -> None:
        if not self.cfg.cfg['enabled']:
            return
        self.update_thread.start()
        super(CountdownWin, self).show()

    def load_config(self):
        self.cfg.load()
        # 应用配置
        # 窗口
        self.setWindowTitle(self.cfg.cfg['countdown']['title'])
        self.resize(self.cfg.cfg['window']['width'], self.cfg.cfg['window']['height'])
        self.move(self.cfg.cfg['window']['pos_x'], self.cfg.cfg['window']['pos_y'])
        self.ui.lb_event.setText(self.cfg.cfg['countdown']['title'])
        self.set_win_mode(self.cfg.cfg['window']['window_mode'])
        self.set_window_title_visible(self.cfg.cfg['window']['show_title_bar'])
        self.set_countdown_enabled(self.cfg.cfg['enabled'])
        self.update_content()
        self.write_config()
        logging.info('loaded config of %s', self.cfg.filename)

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

    def write_config(self):
        self.cfg.cfg['window']['width'] = self.geometry().width()
        self.cfg.cfg['window']['height'] = self.geometry().height()
        self.cfg.cfg['window']['pos_x'] = self.x()
        self.cfg.cfg['window']['pos_y'] = self.y()
        self.cfg.cfg['window']['window_mode'] = self.win_mode
        self.cfg.cfg['window']['show_title_bar'] = self.title_visible
        self.cfg.write()
        logging.info('saved config of %s', self.cfg.filename)

    def update_content(self):
        self.ui.lb_targetddate.setText(time.strftime(self.cfg.cfg['display']['target_format'],
                                                     time.localtime(self.cfg.cfg['countdown']['end'])))  # target
        if time.time() > self.cfg.cfg['countdown']['end']:  # 计时是否结束
            self.ui.lb_CountDown.setText(self.cfg.cfg['display']['end_text'])  # show end text
        else:
            end_dt = datetime.datetime.fromtimestamp(self.cfg.cfg['countdown']['end'])
            now_dt: datetime = datetime.datetime.now()
            delta = end_dt - now_dt
            self.ui.lb_CountDown.setText(function.strfdelta(delta, self.cfg.cfg['display']['countdown_format']))

        # progressbar
        self.ui.progressBar.setVisible(self.cfg.cfg['display']['show_progress_bar'])
        self.ui.progressBar.setMaximum(self.cfg.cfg['countdown']['end'] - self.cfg.cfg['countdown']['start'])
        if time.time() > self.cfg.cfg['countdown']['end']:
            self.ui.progressBar.setValue(self.ui.progressBar.maximum())
        else:
            if self.cfg.cfg['display']['reverse_progress_bar']:
                self.ui.progressBar.setValue(self.cfg.cfg['countdown']['end'] - time.time())
            else:
                self.ui.progressBar.setValue(time.time() - self.cfg.cfg['countdown']['start'])

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self and event.type() == event.Close:
            self.update_thread.sig_stop.emit()
            logging.info('countdown window %s closed', self.cfg.cfg['countdown']['title'])
            return True
        elif watched == self and event.type() == event.MouseButtonDblClick:
            self.set_window_title_visible(not self.title_visible)
            self.write_config()
        # print(watched, event)
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
    def on_action_save_profile_triggered(self, trigger_type: bool):
        if not trigger_type:
            self.write_config()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.drag_flag = True
        self.m_pos = event.globalPos() - self.pos()
        event.accept()
        self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if Qt.LeftButton and self.drag_flag:
            self.move(event.globalPos() - self.m_pos)
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.drag_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.write_config()


class UpdateThread(QThread):
    sig_update = pyqtSignal()
    sig_stop = pyqtSignal()

    def __init__(self):
        super(UpdateThread, self).__init__()
        self.stopped = False
        self.sig_stop.connect(self.stop)

    def run(self):
        past = int(time.time())
        self.stopped = False
        while True:
            if int(time.time()) - past >= 1:
                past = int(time.time())
                self.sig_update.emit()
            if self.stopped:
                break
            self.sleep(1)

    def stop(self):
        self.stopped = True