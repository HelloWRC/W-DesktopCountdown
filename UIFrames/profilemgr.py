import logging
import function
import time
from UIFrames.ui_profilemgr import Ui_ProfileMgr
from UIFrames.ui_countdown_card import Ui_CountdownCard
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtCore import QSize


class CountdownCard(QWidget):
    def __init__(self, item, cfg, countdown):
        from UIFrames.countdown import CountdownWin
        super(CountdownCard, self).__init__()
        self.item: QListWidgetItem = item
        self.cfg: function.ConfigFileMgr = cfg
        self.countdown: CountdownWin = countdown
        self.ui = Ui_CountdownCard()
        self.ui.setupUi(self)
        self.load_val()

    def load_val(self):
        from UIFrames.countdown import CountdownWin

        self.ui.lb_title.setText(self.ui.lb_title.text().format(self.cfg.cfg['countdown']['title']))
        self.ui.lb_time.setText(self.ui.lb_time.text().format(
            time.strftime(CountdownWin.countdown_config_default['display']['target_format'],
                          time.localtime(self.cfg.cfg['countdown']['start'])),
            time.strftime(
                CountdownWin.countdown_config_default['display'][
                    'target_format'],
                time.localtime(self.cfg.cfg['countdown']['end']))
            ))
        self.ui.cb_enabled.setChecked(self.cfg.cfg['enabled'])


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
            self.cards_widget[i] = CountdownCard(self.cards[i], self.profile_mgr.config_mgr[i],
                                                 self.profile_mgr.countdowns_win[i])
            self.ui.countdowns.setItemWidget(self.cards[i], self.cards_widget[i])


