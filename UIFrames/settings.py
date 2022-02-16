from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QColorDialog
from PyQt5.Qt import pyqtSignal
from UIFrames.license import LicenseRead

import function
import json
import os
import platform
import properties
import qt_material
from UIFrames.ui_settings import Ui_Form


class Settings(QWidget):
    def __init__(self, config_mgr: function.ConfigFileMgr, app):
        import wcdapp
        QWidget.__init__(self)
        self.__finished_init = False
        self.app: wcdapp.WDesktopCD = app
        self.cm = config_mgr
        self.cfg = config_mgr.cfg
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.lb_version.setText(self.ui.lb_version.text().format(properties.version))
        self.ui.lb_platform.setText(self.ui.lb_platform.text().format('Python {} on {}'.format(
            platform.python_version(),
            platform.platform())))
        for i in properties.default_colors:
            self.ui.cb_colortheme.addItem(i)
        self.ui.tb_thanks.setSource(QUrl('qrc:///res/doc/contributors.md'), 4)
        self.ui.cb_custom_font.setFont(QFont(self.cfg['appearance']['custom_font']))
        self.load_val()
        self.click_count = 0
        self.ui.lb_logo.eventFilter = self.eventFilter
        self.ui.lb_logo.installEventFilter(self.ui.lb_logo)
        self.__finished_init = True

    def on_btn_projhome_released(self):
        function.call_browser('https://github.com/HelloWRC/W-DesktopCountdown')

    def on_btn_feedback_released(self):
        function.call_browser('https://github.com/HelloWRC/W-DesktopCountdown/issues')

    def on_btn_opensource_released(self):
        self.license = LicenseRead(self)
        self.license.show()

    def on_btn_selcolor_released(self):
        self.colr_sel = QColorDialog.getColor(initial=QColor(self.ui.btn_selcolor.text()), title='选择主题色')
        rgb = self.colr_sel.getRgb()
        self.ui.btn_selcolor.setText(function.rgb2hex(rgb[0], rgb[1], rgb[2]))

    def on_btn_close_released(self):
        self.close()

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
        # appearance
        self.ui.cb_colortheme.setCurrentIndex(self.cfg['appearance']['color_theme']['theme'])
        self.ui.cb_ldstyle.setCurrentIndex(self.cfg['appearance']['ld_style'])
        self.ui.rb_default.setChecked(self.cfg['appearance']['color_theme']['type'] == 0)
        self.ui.rb_syscolor.setChecked(self.cfg['appearance']['color_theme']['type'] == 1)
        self.ui.rb_customcolor.setChecked(self.cfg['appearance']['color_theme']['type'] == 2)
        self.ui.btn_selcolor.setText(self.cfg['appearance']['color_theme']['color'])
        self.ui.cb_custom_font.setCurrentFont(QFont(self.cfg['appearance']['custom_font']))

    def save_val(self):
        # appearance
        self.cfg['appearance']['color_theme']['theme'] = self.ui.cb_colortheme.currentIndex()
        self.cfg['appearance']['ld_style'] = self.ui.cb_ldstyle.currentIndex()
        for i in range(3):
            if (self.ui.rb_default, self.ui.rb_syscolor, self.ui.rb_customcolor)[i].isChecked():
                self.cfg['appearance']['color_theme']['type'] = i
        self.cfg['appearance']['color_theme']['color'] = self.ui.btn_selcolor.text()
        self.cfg['appearance']['custom_font'] = self.ui.cb_custom_font.currentFont().family()

