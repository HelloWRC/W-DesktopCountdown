import logging
import time
import datetime

from PyQt5.QtCore import Qt

import properties

import functions.base
from UIFrames.toast import Toast
from UIFrames.ui_new_countdown import Ui_NewCountdown
from PyQt5.QtWidgets import QWidget, QPushButton
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
        self.update_enable_state()

        self.ui.dte_starttime.setDateTime(datetime.datetime.now())
        self.ui.dte_endtime.setDateTime(datetime.datetime.now())

        self.ui.dte_endtime.dateTimeChanged.connect(self.update_enable_state)
        self.ui.dte_starttime.dateTimeChanged.connect(self.update_enable_state)
        self.ui.le_input.textEdited.connect(self.update_enable_state)

    def on_btn_cancel_clicked(self):
        logging.info('new countdown window cancled.')
        self.close()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Enter:
            self.on_btn_confirm_released()

    def on_btn_confirm_released(self):
        if not self.ui.btn_confirm.isEnabled():
            return
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
        button = QPushButton('查看')
        button.setFlat(True)
        button.released.connect(self.app.profile_mgr.config_ui[profile_name].show)
        Toast.toast(self.app.profile_mgr_ui, '已创建倒计时。', buttons=[button])
        self.close()

    def update_enable_state(self):
        from functions.base import filename_chk
        self.ui.lb_filename.setText('将被保存为：{}'.format(filename_chk(self.ui.le_input.text())))
        start_time = int(time.mktime(self.ui.dte_starttime.dateTime().toPyDateTime().timetuple()))
        end_time = int(time.mktime(self.ui.dte_endtime.dateTime().toPyDateTime().timetuple()))

        if self.ui.le_input.text() == '' or start_time > end_time:
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
