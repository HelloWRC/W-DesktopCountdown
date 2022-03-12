import logging
import time
import datetime

import functions.base
from UIFrames.ui_new_countdown import Ui_NewCountdown
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox


class NewCountdownWin(QWidget):
    def __init__(self, app):
        super(NewCountdownWin, self).__init__()
        self.app = app
        self.ui = Ui_NewCountdown()
        self.ui.setupUi(self)
        self.show()
        logging.info('new countdown window requested.')
        self.on_le_input_textChanged('')

        self.ui.dte_starttime.setDateTime(datetime.datetime.now())
        self.ui.dte_endtime.setDateTime(datetime.datetime.now())

    def on_btn_cancel_clicked(self):
        logging.info('new countdown window cancled.')
        self.close()

    def on_btn_confirm_released(self):
        profile_name = functions.base.filename_chk(self.ui.le_input.text())
        start_time = int(time.mktime(self.ui.dte_starttime.dateTime().toPyDateTime().timetuple()))
        end_time = int(time.mktime(self.ui.dte_endtime.dateTime().toPyDateTime().timetuple()))
        if start_time > end_time:
            QMessageBox.error(self, '错误', '请填写有效的时间。')
            return

        logging.debug('new profile: %s', profile_name)
        self.app.profile_mgr.create_profile(profile_name, start_time, end_time)
        self.close()

    def on_le_input_textChanged(self, text):
        from functions.base import filename_chk
        self.ui.lb_filename.setText('将被保存为：{}'.format(filename_chk(text)))
        if self.ui.le_input.text() == '':
            self.ui.btn_confirm.setEnabled(False)
        else:
            self.ui.btn_confirm.setEnabled(True)
