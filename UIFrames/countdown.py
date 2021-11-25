import logging
from datetime import datetime

import function
import time
import datetime
import threading
from UIFrames.ui_countdown import Ui_Countdown
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QEvent
from PyQt5.Qt import QApplication


window_update_event = QEvent.registerEventType()


class CountdownWin(QWidget):
    countdown_config_default = {
        'window': {
            'width': 300,
            'height': 100,
            'window_mode': 0,
            'pos_x': 0,
            'pos_y': 0
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
            'end_text': '计时结束'
        }
    }

    def __init__(self, app, qss_path: str, config_path: str):
        self.app = app
        super(CountdownWin, self).__init__()
        self.setStyleSheet(function.get_qss(qss_path))
        self.config_path = config_path
        self.cfg = function.ConfigFileMgr(self.config_path, self.countdown_config_default)
        self.app.logger.info('created countdown window')
        self.ui = Ui_Countdown()
        self.ui.setupUi(self)
        self.load_config()
        self.update_thread = threading.Thread(target=self.keep_update,
                                              name='{} UpdateThread'.format(self.cfg.cfg['countdown']['title']))
        self.update_thread.start()

    def load_config(self):
        self.cfg.load()
        self.setWindowTitle(self.cfg.cfg['countdown']['title'])
        self.ui.lb_event.setText(self.cfg.cfg['countdown']['title'])
        self.update_content()
        self.write_config()

    def write_config(self):
        self.cfg.write()

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
        self.ui.progressBar.setValue(time.time() - self.cfg.cfg['countdown']['start'])

    def keep_update(self):
        past = int(time.time())
        while True:
            if int(time.time()) - past >= 1:
                past = int(time.time())
                self.update_content()


