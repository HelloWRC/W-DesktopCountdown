import logging
import time
import datetime
import properties

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
        self.countdown_mapping = []
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
            QMessageBox.critical(self, '错误', '请填写有效的时间。')
            return

        logging.debug('new profile: %s', profile_name)
        if self.ui.cbx_create_from.isChecked():
            if self.ui.cmb_create_from.count() == 0:
                QMessageBox.critical(self, '错误', '无效的倒计时')
                return
            self.app.profile_mgr.create_profile(profile_name, start_time, end_time,
                                                self.countdown_mapping[self.ui.cmb_create_from.currentIndex()])
        else:
            self.app.profile_mgr.create_profile(profile_name, start_time, end_time, None)
        self.close()

    def on_le_input_textChanged(self, text):
        from functions.base import filename_chk
        self.ui.lb_filename.setText('将被保存为：{}'.format(filename_chk(text)))
        if self.ui.le_input.text() == '':
            self.ui.btn_confirm.setEnabled(False)
        else:
            self.ui.btn_confirm.setEnabled(True)

    def showEvent(self, event) -> None:
        self.ui.cmb_create_from.clear()
        self.countdown_mapping.clear()
        for i in self.app.profile_mgr.config_mgr:
            if i == properties.default_profile_name:
                continue
            self.countdown_mapping.append(i)
            self.ui.cmb_create_from.addItem(self.app.profile_mgr.config_mgr[i].cfg['countdown']['title'])
