import copy
import logging
import time
import datetime

import functions.base
import functions.countdown
import functions.plugins
from UIFrames.ui_automate_cfg import Ui_AutomateConfigure
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction


class ACAction(QAction):
    def __init__(self, text, target, name):
        super(ACAction, self).__init__(text, triggered=lambda: target(name))



class AutomateConfigure(QWidget):
    def __init__(self, config, profile_cfg_ui):
        super(AutomateConfigure, self).__init__()
        self.cfg = config
        self.profile_cfg_ui = profile_cfg_ui
        self.trigger_menu = QMenu()
        self.action_menu = QMenu()
        self.trigger_actions = {}
        self.action_actions = {}
        self.ui = Ui_AutomateConfigure()
        self.ui.setupUi(self)
        self.ui.btn_add_trigger.setMenu(self.trigger_menu)
        self.ui.btn_add_action.setMenu(self.action_menu)

    def load_val(self):
        self.ui.le_name.setText(self.cfg['name'])
        self.ui.cb_trigger_type.setCurrentIndex(self.cfg['trigger_type'])
        for i in functions.plugins.triggers:
            self.trigger_actions[i] = ACAction(functions.plugins.triggers[i].trigger_name, self.add_trigger, i)
            self.trigger_menu.addAction(self.trigger_actions[i])
        for i in functions.plugins.actions:
            self.action_actions[i] = ACAction(functions.plugins.actions[i].action_name, self.add_action, i)
            self.action_menu.addAction(self.action_actions[i])
        self.refresh_ui()

    def save_val(self):
        self.cfg['name'] = self.ui.le_name.text()
        self.cfg['trigger_type'] = self.ui.cb_trigger_type.currentIndex()

    def add_trigger(self, index):
        self.cfg['triggers'][index] = functions.base.rich_default_pass(functions.plugins.triggers[index].default_config, {})
        self.refresh_ui()

    def add_action(self, index):
        self.cfg['actions'][index] = functions.base.rich_default_pass(functions.plugins.actions[index].default_config, {})
        self.refresh_ui()

    def refresh_ui(self):
        self.ui.le_name.setPlaceholderText(functions.countdown.make_auto_sentence(self.cfg))
        self.ui.lst_trigger.clear()
        self.ui.lst_actions.clear()
        for i in self.cfg['triggers']:
            if i in functions.plugins.triggers:
                self.ui.lst_trigger.addItem(functions.plugins.triggers[i].trigger_name)
            else:
                self.ui.lst_trigger.addItem(i)
        for i in self.cfg['actions']:
            if i in functions.plugins.actions:
                self.ui.lst_actions.addItem(functions.plugins.actions[i].action_name)
            else:
                self.ui.lst_actions.addItem(i)

    def show(self) -> None:
        self.load_val()
        super(AutomateConfigure, self).show()

    def close(self) -> bool:
        self.save_val()
        super(AutomateConfigure, self).close()
        self.profile_cfg_ui.refresh_automate_ui()
