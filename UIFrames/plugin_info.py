import functions.base
import functions.plugins

from PyQt5.QtWidgets import QWidget
from .ui_plugin_info import Ui_PluginInfo


class PluginInfo(QWidget):
    def __init__(self, plugin):
        super(PluginInfo, self).__init__()
        self.plugin: functions.plugins.Plugin = plugin
        self.ui = Ui_PluginInfo()
        self.ui.setupUi(self)

        self.ui.lb_plugin_info.setText(self.ui.lb_plugin_info.text().format(
            self.plugin.plugin_id,
            self.plugin.plugin_name,
            self.plugin.description,
            self.plugin.author,
            self.plugin.website,
            self.plugin.module_path
        ))
