from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtWidgets import QInputDialog
from PyQt5.Qt import pyqtSignal

import functions.appearance
import functions.base
from UIFrames.license import LicenseRead
from UIFrames.plugin_info import PluginInfo

import json
import os
import platform
import properties
import qt_material
from UIFrames.ui_settings import Ui_Form


class Settings(QWidget):
    def __init__(self, config_mgr: functions.base.ConfigFileMgr, app):
        self.description = None
        import wcdapp
        QWidget.__init__(self)
        self.__finished_init = False
        self.app: wcdapp.WDesktopCD = app
        self.cm = config_mgr
        self.cfg = config_mgr.cfg
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.plug_func_menu = QMenu()
        self.ui.btn_plug_func.setMenu(self.plug_func_menu)
        self.ui.lb_version.setText(self.ui.lb_version.text().format(properties.version, properties.version_id))
        self.ui.lb_platform.setText(self.ui.lb_platform.text().format('Python {} on {}'.format(
            platform.python_version(),
            platform.platform())))
        for i in properties.default_colors:
            self.ui.cb_colortheme.addItem(i)
        self.ui.tb_thanks.setSource(QUrl('qrc://resources/doc/contributors.md'), 4)
        self.ui.cb_custom_font.setFont(QFont(self.cfg['appearance']['custom_font']))
        self.load_val()
        self.click_count = 0
        self.ui.lb_logo.eventFilter = self.eventFilter
        self.ui.lb_logo.installEventFilter(self.ui.lb_logo)
        self.ui.lb_logo.setScaledContents(True)
        self.ui.lb_logo.setFixedSize(64, 64)
        self.ui.lb_logo.setPixmap(QPixmap(":/resources/icons/colorful/logo.svg"))
        if not self.app.arg.dev:
            self.ui.tabWidget.removeTab(5)
        self.__finished_init = True

    def on_btn_opensource_released(self):
        self.license = LicenseRead(self)
        self.license.show()

    def on_btn_selcolor_released(self):
        self.colr_sel = QColorDialog.getColor(initial=QColor(self.ui.btn_selcolor.text()), title='选择主题色')
        rgb = self.colr_sel.getRgb()
        self.ui.btn_selcolor.setText(functions.appearance.rgb2hex(rgb[0], rgb[1], rgb[2]))

    def on_btn_close_released(self):
        self.close()

    def on_btn_plugin_folder_released(self):
        os.startfile(os.getcwd() + properties.plugins_prefix)

    def on_lst_plugins_currentRowChanged(self, row):
        if self.ui.lst_plugins.count() <= 0:
            return
        plugin = self.app.plugin_mgr.plugins[row]
        if plugin.plugin_config_ui is None:
            self.ui.btn_configure_plug.setEnabled(False)
        else:
            self.ui.btn_configure_plug.setEnabled(True)
        self.plug_func_menu.clear()
        self.description = QAction('以下动作由插件“{}”提供'.format(plugin.plugin_name))
        self.description.setEnabled(False)
        self.plug_func_menu.addAction(self.description)
        self.plug_func_menu.addSeparator()
        if plugin.plugin_actions:
            self.ui.btn_plug_func.setEnabled(True)
            self.plug_func_menu.addActions(plugin.plugin_actions)
        else:
            self.ui.btn_plug_func.setEnabled(False)
        # print(self.app.plugin_mgr.plugins[row].plugin_actions)


    def on_btn_configure_plug_released(self):
        self.app.plugin_mgr.plugins[self.ui.lst_plugins.currentRow()].plugin_config_ui.show()

    def on_btn_plug_info_released(self):
        self.app.plugin_mgr.plugins[self.ui.lst_plugins.currentRow()].plugin_info_ui.show()

    def on_btn_log_released(self):
        os.startfile(os.getcwd() + '/' + properties.latest_log_file_fmt)

    def on_btn_log_folder_released(self):
        os.startfile(os.getcwd() + '/' + properties.log_root)

    def on_btn_crash_report_released(self):
        os.startfile(os.getcwd() + '/' + properties.log_root + 'crash.txt')

    def on_btn_install_local_update_released(self):
        self.app.update_mgr.restart_to_update = QInputDialog.getText(self, '自定义更新文件', '输入自定义更新文件的文件名（需要文件后缀）。完成后应用会马上重启并更新。')[0]
        self.app.quit()

    def update_theme(self):
        if not self.__finished_init:
            return
        self.save_val()
        self.app.update_theme()

    def closeEvent(self, a0):
        self.save_val()
        self.cm.write()
        self.update_theme()
        super(Settings, self).closeEvent(a0)

    def show(self) -> None:
        self.load_val()
        super(Settings, self).show()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        # print(watched, event)
        if watched == self.ui.lb_logo and event.type() == event.MouseButtonRelease:
            self.click_count += 1
            # print(self.click_count)
            if self.click_count == 15:
                self.ui.lb_version.setText('本程序没有特殊选项')
            elif self.click_count == 25:
                self.ui.lb_version.setText('别点了别点了')
            elif self.click_count == 30:
                self.ui.lb_version.setText('再点也没用的')
            elif self.click_count == 40:
                self.ui.lb_version.setText('你真的就这么好奇吗？')
            elif 50 <= self.click_count < 60:
                self.ui.lb_version.setText('最后{}次'.format(60-self.click_count))
            elif self.click_count == 60:
                self.ui.lb_version.setText('(╯‵□′)╯︵┻━┻')
                while True:
                    pass
        return False

    def load_val(self):
        # basic
        self.ui.cb_run_on_start.setChecked(self.cfg['basic']['auto_start'])
        self.ui.cb_splash.setChecked(self.cfg['basic']['splash'])
        # appearance
        self.ui.cb_colortheme.setCurrentIndex(self.cfg['appearance']['color_theme']['theme'])
        self.ui.cb_ldstyle.setCurrentIndex(self.cfg['appearance']['ld_style'])
        self.ui.rb_default.setChecked(self.cfg['appearance']['color_theme']['type'] == 0)
        self.ui.rb_syscolor.setChecked(self.cfg['appearance']['color_theme']['type'] == 1)
        self.ui.rb_customcolor.setChecked(self.cfg['appearance']['color_theme']['type'] == 2)
        self.ui.btn_selcolor.setText(self.cfg['appearance']['color_theme']['color'])
        self.ui.cb_custom_font.setCurrentFont(QFont(self.cfg['appearance']['custom_font']))
        # plugins
        self.ui.lst_plugins.clear()
        for i in self.app.plugin_mgr.plugins:
            item = QListWidgetItem(i.plugin_name)
            item.setToolTip(i.description)
            self.ui.lst_plugins.addItem(item)
        # crash
        self.ui.btn_crash_report.setEnabled(os.path.exists(properties.log_root + 'crash.txt'))

    def save_val(self):
        # basic
        self.cfg['basic']['auto_start'] = self.ui.cb_run_on_start.isChecked()
        self.cfg['basic']['splash'] = self.ui.cb_splash.isChecked()

        # appearance
        self.cfg['appearance']['color_theme']['theme'] = self.ui.cb_colortheme.currentIndex()
        self.cfg['appearance']['ld_style'] = self.ui.cb_ldstyle.currentIndex()
        for i in range(3):
            if (self.ui.rb_default, self.ui.rb_syscolor, self.ui.rb_customcolor)[i].isChecked():
                self.cfg['appearance']['color_theme']['type'] = i
        self.cfg['appearance']['color_theme']['color'] = self.ui.btn_selcolor.text()
        self.cfg['appearance']['custom_font'] = self.ui.cb_custom_font.currentFont().family()

    def on_btn_crash_released(self):
        raise RuntimeError
