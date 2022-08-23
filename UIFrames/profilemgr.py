import logging
import os
import time
import shutil

import functions.base
import properties
import wcdapp
from UIFrames.ui_profilemgr import Ui_ProfileMgr
from UIFrames.ui_countdown_card import Ui_CountdownCard
from UIFrames.new_countdown import NewCountdownWin
from UIFrames.toast import Toast
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QCoreApplication

tr = QCoreApplication.translate


class CountdownCard(QWidget):
    def __init__(self, name, item, cfg, cfgui, countdown, app,
                 default_cfg=False):
        self.__finished = False
        from UIFrames.countdown import CountdownWin
        super(CountdownCard, self).__init__()
        self.item: QListWidgetItem = item
        self.name = name
        self.cfg_ui = cfgui
        self.app: wcdapp.WDesktopCD = app
        self.cfg: functions.base.ConfigFileMgr = cfg
        self.countdown: CountdownWin = countdown
        self.default_cfg = default_cfg
        self.ui = Ui_CountdownCard()
        self.ui.setupUi(self)
        self.load_val()
        self.__finished = True

    def load_val(self):
        from UIFrames.countdown import CountdownWin

        if self.default_cfg:
            self.ui.lb_time.setText(tr('CountdownCard', '用于创建新倒计时的模板。'))
            self.ui.lb_title.setText(
                tr('CountdownCard', '<html><head/><body><p><span style=" font-size:28pt; font-weight:700;">默认配置</span></p></body></html>'))
            self.ui.cb_enabled.setVisible(False)
            self.ui.btn_del.setVisible(False)
        else:
            self.ui.lb_title.setText('<html><head/><body><p><span style=" font-size:28pt; font-weight:700;">{}</span></p></body></html>'.format(self.cfg.cfg['countdown']['title']))
            self.ui.lb_time.setText('{} - {}'.format(
                time.strftime(CountdownWin.countdown_config_default['display']['target_format'],
                              time.localtime(self.cfg.cfg['countdown']['start'])),
                time.strftime(
                    CountdownWin.countdown_config_default['display'][
                        'target_format'],
                    time.localtime(self.cfg.cfg['countdown']['end']))
                ))
            self.ui.cb_enabled.setChecked(self.cfg.cfg['enabled'])

    def on_btn_edit_released(self):
        self.cfg_ui.show()

    def on_btn_del_released(self):
        r = QMessageBox.warning(self, '删除{}'.format(self.cfg.cfg['countdown']['title']),
                                '你真的要删除倒计时{}吗？这个操作不可逆转！'.format(self.cfg.cfg['countdown']['title']),
                                buttons=QMessageBox.Yes | QMessageBox.No,
                                defaultButton=QMessageBox.No)
        if r == QMessageBox.Yes:
            self.app.profile_mgr.remove_profile(self.name)
            Toast.toast(self.app.profile_mgr_ui, '已删除倒计时。')

    def on_btn_export_released(self):
        path = QFileDialog.getSaveFileName(self, filter='W-DesktopCountdown配置文件(*.wdcd)')
        if path[0] == '':
            return
        shutil.copy(self.cfg.filename, path[0])
        button = QPushButton('查看')
        button.setFlat(True)
        button.released.connect(lambda: os.startfile(os.path.dirname(path[0])))
        Toast.toast(self.app.profile_mgr_ui, '已导出倒计时。', buttons=[button])

    def on_cb_enabled_toggled(self, stat):
        if not self.__finished:
            return
        self.cfg.cfg['enabled'] = stat
        self.cfg.write()
        self.countdown.load_config()


class ProfileMgrUI(QMainWindow):
    def __init__(self, app):
        import wcdapp
        super(ProfileMgrUI, self).__init__()
        self.ui = Ui_ProfileMgr()
        self.ui.setupUi(self)
        self.cards = {}
        self.cards_widget = {}
        self.app: wcdapp.WDesktopCD = app
        self.profile_mgr = self.app.profile_mgr
        self.setWindowTitle(self.windowTitle().format(properties.version))

    def load_val(self):
        self.ui.countdowns.clear()
        self.cards.clear()
        self.cards_widget.clear()

        for i in self.profile_mgr.profiles:
            self.cards[i] = QListWidgetItem('')
            self.cards[i].setSizeHint(QSize(320, 160))
            self.ui.countdowns.addItem(self.cards[i])
            if i == properties.default_profile_name:
                self.cards_widget[i] = CountdownCard(i, self.cards[i], self.profile_mgr.config_mgr[i],
                                                     self.profile_mgr.config_ui[i],
                                                     None, self.app, True)
            else:
                self.cards_widget[i] = CountdownCard(i, self.cards[i], self.profile_mgr.config_mgr[i],
                                                     self. profile_mgr.config_ui[i],
                                                     self.profile_mgr.countdowns_win[i], self.app, False)

            self.ui.countdowns.setItemWidget(self.cards[i], self.cards_widget[i])

    def refresh(self, refresh_type=0) -> None:
        """

        :param refresh_type: 刷新方式（0=软刷新，1=硬刷新）
        :return: 无
        """
        if refresh_type == 0:
            logging.info('requested soft refresh')
            for i in self.cards_widget.items():
                i[1].load_val()
        elif refresh_type == 1:
            logging.info('requested hard refresh')
            self.load_val()

    def event(self, event: QEvent) -> bool:
        if event.type() == wcdapp.ProfileUpdatedEvent:
            logging.debug('profile updated.')
            self.refresh(0)
        elif event.type() == wcdapp.ProfileFileEvent:
            logging.debug('profile file event')
            self.refresh(1)
        return super(ProfileMgrUI, self).event(event)

    @pyqtSlot(bool)
    def on_action_new_profile_triggered(self, triggered):
        self.newcd = NewCountdownWin(self.app)

    @pyqtSlot(bool)
    def on_action_import_countdown_triggered(self, triggered):
        path = QFileDialog.getOpenFileName(self, filter='W-DesktopCountdown配置文件(*.wdcd)')
        if path[0] == '':
            return
        name = self.app.profile_mgr.import_profile(path[0])
        button = QPushButton('查看')
        button.setFlat(True)
        button.released.connect(self.profile_mgr.config_ui[name].show)
        Toast.toast(self, '已导入倒计时。', buttons=[button])

    @pyqtSlot(bool)
    def on_action_settings_triggered(self, triggered):
        self.app.settings_ui.show()

    @pyqtSlot(bool)
    def on_action_help_triggered(self, triggered):
        os.startfile('https://github.com/HelloWRC/W-DesktopCountdown/wiki')

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()
