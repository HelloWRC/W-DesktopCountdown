import os.path

import functions.base
import functions.plugins

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QMessageBox

import properties
from .ui_plugin_info import Ui_PluginInfo


class PluginInfo(QWidget):
    def __init__(self, plugin):
        super(PluginInfo, self).__init__()
        self.plugin: functions.plugins.Plugin = plugin
        self.ui = Ui_PluginInfo()
        self.ui.setupUi(self)

        self.setWindowTitle(self.windowTitle().format(self.plugin.plugin_name))
        self.ui.lb_plugin_info.setText(self.ui.lb_plugin_info.text().format(
            self.plugin.plugin_id,
            self.plugin.plugin_name,
            self.plugin.description,
            self.plugin.author,
            self.plugin.website,
            self.plugin.module_path
        ))

        lists = (self.ui.lst_effects, self.ui.lst_actions, self.ui.lst_triggers,
                 self.ui.lst_pm_actions, self.ui.lst_tray_actions, self.ui.lst_ucfg_views)
        sources = (self.plugin.provided_effects, self.plugin.provided_actions, self.plugin.provided_triggers,
                   self.plugin.pm_actions, self.plugin.tray_actions, self.plugin.provided_views)
        for i in range(0, 3):
            lists[i].addItems(sources[i])
        for i in range(3, 5):
            for k in sources[i]:
                item = QListWidgetItem(k.text())
                item.setIcon(k.icon())
                lists[i].addItem(item)
        lists[5].addItems(sources[5])


    def showEvent(self, event):
        self.ui.btn_browse_plugin.setEnabled(os.path.exists(properties.work_root + '/'.join(self.plugin.module_path.split('.'))))
        super(PluginInfo, self).showEvent(event)

    def on_btn_browse_plugin_released(self):
        try:
            os.startfile(os.getcwd() + '/' + '/'.join(self.plugin.module_path.split('.')))
        except Exception as exp:
            QMessageBox.critical(self, '错误', '无法打开指定的文件：{}'.format(exp))
