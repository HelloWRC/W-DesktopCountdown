import logging
import function
import time
import shutil

import wcdapp
from UIFrames.ui_profilemgr import Ui_ProfileMgr
from UIFrames.ui_countdown_card import Ui_CountdownCard
from UIFrames.new_countdown import NewCountdownWin
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import pyqtSlot


class CountdownCard(QWidget):
    def __init__(self, name, item, cfg, countdown, app):
        from UIFrames.countdown import CountdownWin
        super(CountdownCard, self).__init__()
        self.item: QListWidgetItem = item
        self.name = name
        self.app: wcdapp.WDesktopCD = app
        self.cfg: function.ConfigFileMgr = cfg
        self.countdown: CountdownWin = countdown
        self.ui = Ui_CountdownCard()
        self.ui.setupUi(self)
        self.load_val()

    def load_val(self):
        from UIFrames.countdown import CountdownWin

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
        self.countdown.config_ui.show()

    def on_btn_del_released(self):
        r = QMessageBox.warning(self, '删除{}'.format(self.cfg.cfg['countdown']['title']),
                                '你真的要删除倒计时{}吗？这个操作不可逆转！'.format(self.cfg.cfg['countdown']['title']),
                                buttons=QMessageBox.Yes | QMessageBox.No,
                                defaultButton=QMessageBox.No)
        if r == QMessageBox.Yes:
            self.app.profile_mgr.remove_profile(self.name)

    def on_btn_export_released(self):
        path = QFileDialog.getSaveFileName(self, filter='W-DesktopCountdown配置文件(*.wdcd)')
        if path[0] == '':
            return
        shutil.copy(self.cfg.filename, path[0])
        QMessageBox.information(self, '导出成功', '导出成功')

    def on_cb_enabled_toggled(self, stat):
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
        self.load_val()

    def load_val(self):
        self.ui.countdowns.clear()
        self.cards.clear()
        self.cards_widget.clear()

        for i in self.profile_mgr.profiles:
            self.cards[i] = QListWidgetItem('')
            self.cards[i].setSizeHint(QSize(320, 160))
            self.ui.countdowns.addItem(self.cards[i])
            self.cards_widget[i] = CountdownCard(i, self.cards[i], self.profile_mgr.config_mgr[i],
                                                 self.profile_mgr.countdowns_win[i], self.app)
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
        self.app.profile_mgr.import_profile(path[0])

