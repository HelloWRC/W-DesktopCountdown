import logging
from datetime import datetime

import function
import time
import datetime
import threading
from UIFrames.ui_countdown import Ui_Countdown
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QEvent, QObject, Qt
from PyQt5.Qt import QApplication

window_update_event = QEvent.registerEventType()


class CountdownWin(QWidget):
    countdown_config_default = {
        'window': {
            'width': 300,
            'height': 100,
            'window_mode': 0,
            'pos_x': 0,
            'pos_y': 0,
            'show_title_bar': True,

        },
        'countdown': {
            'start': 0,
            'end': 0,
            'title': 'countdown'
        },
        'display': {
            'target_format': '%Y/%m/%d %H:%M:%S',
            'countdown_format': '%Y/%m/%d %H:%M:%S',
            'show_progress_bar': True,
            'end_text': '计时结束',
            'start_text': '计时未开始',
            'qss_priority': 1
        },
        'enabled': True
    }

    def __init__(self, app, qss_path: str, config: function.ConfigFileMgr):
        self.app = app
        super(CountdownWin, self).__init__()
        self.setStyleSheet(function.get_qss(qss_path))
        self.stopped: bool = False
        self.win_mode = 0
        self.title_visible = True
        self.cfg = config
        self.app.logger.info('created countdown window')
        self.ui = Ui_Countdown()
        self.ui.setupUi(self)
        self.load_config()
        self.update_thread = threading.Thread(target=self.keep_update,
                                              name='{} UpdateThread'.format(self.cfg.cfg['countdown']['title']))
        self.update_thread.start()
        self.installEventFilter(self)
        self.show()

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
        self.ui.progressBar.setMaximum(self.cfg.cfg['countdown']['end'] - self.cfg.cfg['countdown']['start'])
        if time.time() > self.cfg.cfg['countdown']['end']:
            self.ui.progressBar.setValue(self.ui.progressBar.maximum())
        else:
            self.ui.progressBar.setValue(time.time() - self.cfg.cfg['countdown']['start'])

    def keep_update(self):
        past = int(time.time())
        while True:
            if int(time.time()) - past >= 1:
                past = int(time.time())
                self.update_content()
            if self.stopped:
                logging.info('stop update thread')
                return

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self and event.type() == event.Close:
            self.write_config()
            self.stopped = True
            while self.update_thread.is_alive():
                pass
            logging.info('countdown window %s closed', self.cfg.cfg['countdown']['title'])
            return True
        elif watched == self and event.type() == event.MouseButtonDblClick:
            self.set_window_title_visible(not self.title_visible)
        return super(CountdownWin, self).eventFilter(watched, event)

    def set_win_mode(self, level: int):
        """
        @level: 窗口层级
         0: 正常
         -1: 置底
         1:置顶
        """
        if level != self.win_mode:
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
