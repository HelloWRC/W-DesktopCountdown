import logging
import time

import requests
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
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.Qt import pyqtSignal

from PyQt5.uic import loadUi

import UIFrames.format_edit
import UIFrames.universe_configure
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
        self.page_basic = UIFrames.universe_configure.UniverseConfigure(self.cfg['basic'],
                                                                        properties.default_basic_config,
                                                                        True)
        self.ui.tab_gernel.layout().addWidget(self.page_basic)

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
        self.app.update_mgr.update_thread.sig_status.connect(self.update_download_status)
        self.app.update_mgr.update_thread.sig_error.connect(self.error_status)
        if not self.app.arg.dev:
            self.ui.tabWidget.removeTab(5)

        self.format_edit = UIFrames.format_edit.FormatEdit('????????????', self.ui.le_text_dev.setText, {
            '%a': '?????????1',
            '%b': '?????????2'
        })
        self.__finished_init = True

    def on_btn_opensource_released(self):
        self.license = LicenseRead(self)
        self.license.show()

    def on_btn_selcolor_released(self):
        self.colr_sel = QColorDialog.getColor(initial=QColor(self.ui.btn_selcolor.text()), title='???????????????')
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
        self.description = QAction('????????????????????????{}?????????'.format(plugin.plugin_name))
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

    def on_btn_force_update_released(self):
        try:
            self.save_val()
            self.app.update_mgr.refresh_source()
            self.app.update_mgr.check_update(True)
            self.load_val()
        except requests.RequestException as exp:
            logging.error('Could not refresh update metadata. %s', exp)
            QMessageBox.critical(self, '????????????????????????', '?????????????????????????????????????????????{}'.format(exp))

    def on_btn_stop_update_released(self):
        self.app.update_mgr.update_thread.stop()

    def on_btn_install_local_update_released(self):
        self.app.update_mgr.restart_to_update = QInputDialog.getText(self, '?????????????????????', '????????????????????????????????????????????????????????????????????????????????????????????????????????????')[0]
        self.app.quit()

    def on_btn_dbg_download_update_released(self):
        download_target = QInputDialog.getText(self, '??????????????????', '???????????????')[0]
        self.app.update_mgr.download_target = download_target
        self.app.update_mgr.update_thread.launch(1)

    def on_btn_check_ui_released(self):
        try:
            form_name = QInputDialog.getText(self, '????????????', '?????????????????????????????????.ui???')[0]
            self.__du = loadUi('./UISource/' + form_name)
            self.__du.show()
        except Exception as exp:
            QMessageBox.critical(self, '?????????????????????', str(exp))

    def update_download_status(self, progress, text):
        if progress == -1:
            self.load_val()
            self.ui.update_progress.setVisible(False)
            for i in (self.ui.btn_check_update, self.ui.btn_update_now, self.ui.btn_force_update):
                i.setEnabled(True)
            self.ui.btn_stop_update.setEnabled(False)
            self.save_val()
            self.load_val()
            return
        if progress == -2:
            self.ui.update_progress.setRange(0, 0)
            self.ui.update_progress.setValue(0)
        else:
            self.ui.update_progress.setRange(0, 100)
            self.ui.update_progress.setValue(progress)
        for i in (self.ui.btn_check_update, self.ui.btn_update_now, self.ui.btn_force_update):
            i.setEnabled(False)
        self.ui.btn_stop_update.setEnabled(True)
        self.ui.update_progress.setVisible(True)
        self.ui.lb_update_info.setText(text)
        self.app.processEvents()

    def error_status(self, text):
        QMessageBox.critical(self, '??????', text)

    def on_btn_check_update_released(self):
        try:
            self.save_val()
            self.app.update_mgr.refresh_source()
            self.app.update_mgr.check_update()
            self.load_val()
        except requests.RequestException as exp:
            logging.error('Could not refresh update metadata. %s', exp)
            QMessageBox.critical(self, '????????????????????????', '?????????????????????????????????????????????{}'.format(exp))

    def on_btn_update_now_released(self):
        self.save_val()
        self.load_val()
        self.app.update_mgr.update_thread.launch(2)

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
                self.ui.lb_version.setText('???????????????????????????')
            elif self.click_count == 25:
                self.ui.lb_version.setText('??????????????????')
            elif self.click_count == 30:
                self.ui.lb_version.setText('??????????????????')
            elif self.click_count == 40:
                self.ui.lb_version.setText('??????????????????????????????')
            elif 50 <= self.click_count < 60:
                self.ui.lb_version.setText('??????{}???'.format(60-self.click_count))
            elif self.click_count == 60:
                self.ui.lb_version.setText('(????????????)???????????????')
                while True:
                    pass
        return False

    def load_val(self):
        self.app.update_mgr.save_config()
        # basic
        self.page_basic.load_val()
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
        # update
        self.ui.cb_update_branch.clear()
        self.ui.cb_update_channel.clear()
        for i in self.app.update_mgr.source['branches']:
            self.ui.cb_update_branch.addItem(i)
        if self.cfg['update']['download']['branch'] == '' and len(self.app.update_mgr.source['branches']):
            self.cfg['update']['download']['branch'] = list(self.app.update_mgr.source['branches'].keys())[0]
        if self.cfg['update']['download']['branch'] in self.app.update_mgr.source['branches']:
            for i in self.app.update_mgr.source['branches'][self.cfg['update']['download']['branch']]['channels']:
                self.ui.cb_update_channel.addItem(i)
            if self.cfg['update']['download']['channel'] in self.app.update_mgr.source['branches'][self.cfg['update']['download']['branch']]['channels']:
                root = self.app.update_mgr.source['branches'][self.cfg['update']['download']['branch']]['channels'][self.cfg['update']['download']['channel']]
                download_version = root['version']
                if download_version is not None:
                    self.ui.lb_changelog.setText(self.app.update_mgr.source['versions'][download_version]['change_log'])
        if self.app.update_mgr.status == functions.base.UpdateMgr.UpToDate:
            self.ui.lb_changelog.setText('# ???????????????????????????')
        if self.app.update_mgr.status == functions.base.UpdateMgr.UnChecked:
            self.ui.lb_changelog.setText('# ????????????????????????????????????????????????')

        self.ui.cb_update_branch.setCurrentText(self.cfg['update']['download']['branch'])
        self.ui.cb_update_channel.setCurrentText(self.cfg['update']['download']['channel'])
        self.ui.cb_auto_check_update.setChecked(self.cfg['update']['auto_update']['auto_check'])

        self.ui.lb_update_status.setText('<html><head/><body><p><span style=" font-size:20pt; font-weight:700;">{}</span></p></body></html>'.format(properties.update_status[self.app.update_mgr.status + 1]))
        if self.app.update_mgr.status >= 2:
            self.ui.lb_update_info.setText('{} -> {}'.format(properties.version, self.app.update_mgr.latest_version))
            self.ui.btn_update_now.setEnabled(True)
        elif self.app.update_mgr.status == functions.base.UpdateMgr.UpToDate:
            self.ui.lb_update_info.setText('?????????????????????{}'.format(time.asctime(time.localtime(self.app.update_mgr.last_checked))))
            self.ui.btn_update_now.setEnabled(False)
        # elif self.app.update_mgr.status == functions.base.UpdateMgr.UnSupport:
        #     self.ui.lb_update_info.setText('?????????????????????????????????????????????')
        else:
            self.ui.lb_update_info.setText('')

        # crash
        self.ui.btn_crash_report.setEnabled(os.path.exists(properties.log_root + 'crash.txt'))

        self.ui.update_progress.setVisible(False)

    def save_val(self):
        # basic
        self.page_basic.save_val()
        # appearance
        self.cfg['appearance']['color_theme']['theme'] = self.ui.cb_colortheme.currentIndex()
        self.cfg['appearance']['ld_style'] = self.ui.cb_ldstyle.currentIndex()
        for i in range(3):
            if (self.ui.rb_default, self.ui.rb_syscolor, self.ui.rb_customcolor)[i].isChecked():
                self.cfg['appearance']['color_theme']['type'] = i
        self.cfg['appearance']['color_theme']['color'] = self.ui.btn_selcolor.text()
        self.cfg['appearance']['custom_font'] = self.ui.cb_custom_font.currentFont().family()
        # update
        self.cfg['update']['download']['branch'] = self.ui.cb_update_branch.currentText()
        self.cfg['update']['download']['channel'] = self.ui.cb_update_channel.currentText()
        self.cfg['update']['auto_update']['auto_check'] = self.ui.cb_auto_check_update.isChecked()

        self.app.update_mgr.load_config(self.cfg['update'])

    def on_btn_crash_released(self):
        raise RuntimeError

    def on_le_text_dev_textChanged(self, text):
        self.ui.lb_text_dev_show.setText(text)

    def on_btn_text_dev_edit_released(self):
        self.format_edit.open_edit_window(self.ui.le_text_dev.text())