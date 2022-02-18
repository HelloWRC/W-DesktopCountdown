import datetime
import logging
import os
import time

import properties
from UIFrames.ui_profile_config_ui import Ui_ProfileConfigUI
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import pyqtSignal
from PyQt5.Qt import QApplication


class ProfileConfigUI(QWidget):
    def __init__(self, app, name, cfg, update_trigger=None, default_cfg=False):
        self.desktop = None
        self._final = False
        import function
        import wcdapp
        self.app: wcdapp.WDesktopCD = app
        self.cfg: function.ConfigFileMgr = cfg
        self.update_trigger = update_trigger
        self.default_cfg = default_cfg
        self.name = name
        self.last_style_widget = None
        super(ProfileConfigUI, self).__init__()
        self.ui = Ui_ProfileConfigUI()
        self.ui.setupUi(self)
        self.ui.cb_widgets.clear()
        for i in self.cfg.cfg['style']:
            function.default_pass(self.cfg.cfg['style'][i], properties.default_widget_style)
            function.default_pass(self.cfg.cfg['style_enabled'][i], properties.default_widget_enabled)
            self.ui.cb_widgets.addItem(i)
        self.last_style_widget = self.ui.cb_widgets.currentText()
        self._final = True
        self.ui.cb_widgets.setCurrentIndex(0)
        self.load_val()

    def ghost(self):
        pass

    def show(self) -> None:
        logging.info('showed profile config ui')
        self.load_val()
        super(ProfileConfigUI, self).show()

    def on_btn_confirm_released(self):
        if not self.check_val():
            QMessageBox.critical(self, '错误', '发现错误的参数，请修正。')
            return
        self.save_val()
        self.close()

    def on_btn_apply_released(self):
        if not self.check_val():
            QMessageBox.critical(self, '错误', '发现错误的参数，请修正。')
            return
        self.save_val()

    def on_btn_reset_default_released(self):
        r = QMessageBox.warning(self, '重置'.format(self.cfg.cfg['countdown']['title']),
                                '你真的要重置这个档案吗？这将把除倒计时设置以外的所有设置重置为默认值！',
                                buttons=QMessageBox.Yes | QMessageBox.No,
                                defaultButton=QMessageBox.No)
        if r == QMessageBox.Yes:
            import wcdapp
            self.app.profile_mgr.reset_profile(self.name)
            self.load_val()
            if self.update_trigger is not None:
                self.update_trigger()
            self.app.postEvent(self.app.profile_mgr_ui, QEvent(wcdapp.ProfileUpdatedEvent))

    def on_btn_save_as_default_released(self):
        r = QMessageBox.warning(self, '设为默认'.format(self.cfg.cfg['countdown']['title']),
                                '你真的要将此档案设为用于创建其它倒计时的模板吗？这会将除倒计时设置以外的所有设置覆盖到原有的模板上！',
                                buttons=QMessageBox.Yes | QMessageBox.No,
                                defaultButton=QMessageBox.No)
        if r == QMessageBox.Yes:
            import wcdapp
            self.app.profile_mgr.set_as_default(self.name)
            self.app.postEvent(self.app.profile_mgr_ui, QEvent(wcdapp.ProfileUpdatedEvent))

    def on_btn_open_folder_released(self):
        os.startfile(os.getcwd() + properties.profile_prefix)

    def check_val(self) -> bool:
        import function
        start_time = int(time.mktime(self.ui.dte_starttime.dateTime().toPyDateTime().timetuple()))
        end_time = int(time.mktime(self.ui.dte_endtime.dateTime().toPyDateTime().timetuple()))

        if start_time > end_time:
            return False
        try:
            function.strfdelta(datetime.datetime.now()-datetime.datetime.now(), self.ui.le_countdown_format.text())
        except KeyError:
            return False

        return True

    def load_val(self):
        import function
        self._final = False
        self.desktop = self.app.desktop()
        rect = self.desktop.screenGeometry()
        maxw = rect.width()
        maxh = rect.height()
        self.setWindowTitle(self.windowTitle().format(self.cfg.cfg['countdown']['title']))
        self.ui.lb_gernal_description.setText(self.ui.lb_gernal_description.text().format(self.cfg.filename))

        # countdown
        if self.default_cfg:
            self.ui.tab_countdown.setVisible(False)
            self.ui.tab_countdown.setEnabled(False)
            self.ui.le_event_name.setText('此设置在编辑默认设置时不可用。')
            self.ui.btn_save_as_default.setEnabled(False)
        else:
            self.ui.le_event_name.setText(self.cfg.cfg['countdown']['title'])
            self.ui.dte_starttime.setDateTime(datetime.datetime.fromtimestamp(self.cfg.cfg['countdown']['start']))
            self.ui.dte_endtime.setDateTime(datetime.datetime.fromtimestamp(self.cfg.cfg['countdown']['end']))
        # display
        self.ui.le_target_format.setText(self.cfg.cfg['display']['target_format'])
        self.ui.le_countdown_format.setText(self.cfg.cfg['display']['countdown_format'])
        self.ui.le_start_text.setText(self.cfg.cfg['display']['start_text'])
        self.ui.le_end_text.setText(self.cfg.cfg['display']['end_text'])
        self.ui.cb_show_progressbar.setChecked(self.cfg.cfg['display']['show_progress_bar'])
        self.ui.cb_reverse_progressbar.setChecked(self.cfg.cfg['display']['reverse_progress_bar'])
        # window
        self.ui.winpos_x.setMaximum(maxw)
        self.ui.winpos_y.setMaximum(maxh)
        self.ui.winsize_h.setMaximum(maxh)
        self.ui.winsize_w.setMaximum(maxw)
        self.ui.winpos_x.setValue(self.cfg.cfg['window']['pos_x'])
        self.ui.winpos_y.setValue(self.cfg.cfg['window']['pos_y'])
        self.ui.winsize_h.setValue(self.cfg.cfg['window']['height'])
        self.ui.winsize_w.setValue(self.cfg.cfg['window']['width'])
        self.ui.cbl_win_mode.setCurrentIndex(self.cfg.cfg['window']['window_mode'] + 1)
        self.ui.cb_titlebar.setChecked(self.cfg.cfg['window']['show_title_bar'])
        # style

        self._final = True

    def save_val(self):
        import wcdapp
        # countdown
        if not self.default_cfg:
            self.cfg.cfg['countdown']['title'] = self.ui.le_event_name.text()
            self.cfg.cfg['countdown']['start'] = int(time.mktime(self.ui.dte_starttime.dateTime().toPyDateTime().timetuple()))
            self.cfg.cfg['countdown']['end'] = int(time.mktime(self.ui.dte_endtime.dateTime().toPyDateTime().timetuple()))
        # display
        self.cfg.cfg['display']['target_format'] = self.ui.le_target_format.text()
        self.cfg.cfg['display']['countdown_format'] = self.ui.le_countdown_format.text()
        self.cfg.cfg['display']['start_text'] = self.ui.le_start_text.text()
        self.cfg.cfg['display']['end_text'] = self.ui.le_end_text.text()
        self.cfg.cfg['display']['show_progress_bar'] = self.ui.cb_show_progressbar.isChecked()
        self.cfg.cfg['display']['reverse_progress_bar'] = self.ui.cb_reverse_progressbar.isChecked()
        # window
        self.cfg.cfg['window']['pos_x'] = self.ui.winpos_x.value()
        self.cfg.cfg['window']['pos_y'] = self.ui.winpos_y.value()
        self.cfg.cfg['window']['height'] = self.ui.winsize_h.value()
        self.cfg.cfg['window']['width'] = self.ui.winsize_w.value()
        self.cfg.cfg['window']['window_mode'] = self.ui.cbl_win_mode.currentIndex() - 1
        self.cfg.cfg['window']['show_title_bar'] = self.ui.cb_titlebar.isChecked()

        self.cfg.write()
        if self.update_trigger is not None:
            self.update_trigger()
        self.app.postEvent(self.app.profile_mgr_ui, QEvent(wcdapp.ProfileUpdatedEvent))

    def on_cb_widgets_currentTextChanged(self, text):
        if not self._final:
            return
        self.load_widget_style(text)

    def load_widget_style(self, widget):
        style_root = self.cfg.cfg['style'][widget]
        self.ui.btn_bgcolor.setText(style_root['background-color'])
        self.ui.le_bgpic.setText(style_root['background-image'])
