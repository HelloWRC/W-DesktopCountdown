import copy
import datetime
import logging
import os
import time

import UIFrames.countdown
import functions.plugins
from data import effects
import functions.appearance
import functions.base
import functions.countdown
import properties
from UIFrames.ui_profile_config_ui import Ui_ProfileConfigUI
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtWidgets import QFontDialog
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QFont
from UIFrames.universe_configure import UniverseConfigure
from UIFrames.automate_cfg import AutomateConfigure


class ProfileConfigUI(QWidget):
    def __init__(self, app, name, cfg, update_trigger=None, default_cfg=False):
        self.last_sel_time = time.time()
        self.desktop = None
        self._final = False
        import wcdapp
        self.app: wcdapp.WDesktopCD = app
        self.cfg: functions.base.ConfigFileMgr = cfg
        self.update_trigger = update_trigger
        self.default_cfg = default_cfg
        self.name = name
        self.enabled_effects = []
        self.disabled_effects = []
        self.local_effect = {}
        self.local_automate = []
        self.auto_cfg = []
        self.last_style_widget = None
        super(ProfileConfigUI, self).__init__()
        self.ui = Ui_ProfileConfigUI()
        self.ui.setupUi(self)
        self.ui.cb_widgets.clear()
        for i in range(len(properties.countdown_widget_id)):
            functions.base.default_pass(self.cfg.cfg['style'][properties.countdown_widget_id[i]], properties.default_widget_style)
            functions.base.default_pass(self.cfg.cfg['style_enabled'][properties.countdown_widget_id[i]], properties.default_widget_enabled)
            self.ui.cb_widgets.addItem(properties.countdown_widget_name[i])
        self.last_style_widget = properties.countdown_widget_id[self.ui.cb_widgets.currentIndex()]
        self._final = True
        self.ui.cb_widgets.setCurrentIndex(0)
        self.load_val()
        self.widgets = (self.ui.window_bg, self.ui.lb_event, self.ui.lb_targetddate, self.ui.lb_text1,
                        self.ui.lb_text2, self.ui.lb_CountDown, self.ui.progressBar)
        for i in self.widgets:
            i.installEventFilter(self)

    def ghost(self):
        pass

    def show(self) -> None:
        logging.info('showed profile config ui')
        self.load_val()
        super(ProfileConfigUI, self).show()

    def eventFilter(self, target, event: QEvent) -> bool:
        if event.type() == event.MouseButtonPress:
            if time.time() - self.last_sel_time >= 0.0001:
                logging.debug('Clicked widget: %s', target)
                for i in range(len(self.widgets)):
                    if self.widgets[i] is target:
                        self.ui.cb_widgets.setCurrentIndex(i)
                self.last_sel_time = time.time()

            event.ignore()
            return True
        return False

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
        start_time = int(time.mktime(self.ui.dte_starttime.dateTime().toPyDateTime().timetuple()))
        end_time = int(time.mktime(self.ui.dte_endtime.dateTime().toPyDateTime().timetuple()))

        if start_time > end_time:
            return False
        try:
            functions.countdown.strfdelta(datetime.datetime.now() - datetime.datetime.now(), self.ui.le_countdown_format.text())
        except KeyError:
            return False

        return True

    def load_val(self):
        self.local_automate = copy.deepcopy(self.cfg.cfg['automate'])
        self.desktop = self.app.desktop()
        rect = self.desktop.screenGeometry()
        maxw = rect.width()
        maxh = rect.height()
        self.setWindowTitle(self.windowTitle().format(self.cfg.cfg['countdown']['title']))
        self.ui.lb_gernal_description.setText(self.ui.lb_gernal_description.text().format(self.cfg.filename))

        if self.cfg.cfg['trusted']:
            self.ui.safe_warn.setVisible(False)
            self.ui.auto_safe_warn.setVisible(False)
            self.ui.cb_auto_enabled.setEnabled(True)
        else:
            self.ui.safe_warn.setVisible(True)
            self.ui.auto_safe_warn.setVisible(True)
            self.ui.cb_auto_enabled.setEnabled(False)

        # countdown
        if self.default_cfg:
            self.ui.tab_countdown.setEnabled(False)
            self.ui.btn_save_as_default.setEnabled(False)
            self.setWindowTitle('默认倒计时配置')
        else:
            self.ui.le_event_name.setText(self.cfg.cfg['countdown']['title'])
            self.ui.dte_starttime.setDateTime(datetime.datetime.fromtimestamp(self.cfg.cfg['countdown']['start']))
            self.ui.dte_endtime.setDateTime(datetime.datetime.fromtimestamp(self.cfg.cfg['countdown']['end']))
            self.ui.lb_defaultcfg_warn.setVisible(False)
            self.setWindowTitle('倒计时配置：{}'.format(self.cfg.cfg['countdown']['title']))
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
        self.ui.cb_skip_taskbar.setChecked(self.cfg.cfg['window']['skip_taskbar'])
        # effects
        self.enabled_effects = list(self.cfg.cfg['effects'].keys())
        self.local_effect = copy.deepcopy(self.cfg.cfg['effects'])
        self.update_effects()
        self.on_lst_enabled_effect_currentRowChanged()
        # auto
        self.ui.cb_auto_enabled.setChecked(self.cfg.cfg['automate_enabled'])
        self.refresh_automate_ui()
        # style
        self.load_widget_style(properties.countdown_widget_id[self.ui.cb_widgets.currentIndex()])
        self.ui.style_preview.setStyleSheet(functions.appearance.mk_qss(self.cfg.cfg['style'], self.cfg.cfg['style_enabled']))

    def refresh_automate_ui(self):
        self.ui.lst_action_list.clear()
        self.auto_cfg.clear()
        for i in self.local_automate:
            self.auto_cfg.append(AutomateConfigure(i, self))
            if i['name']:
                self.ui.lst_action_list.addItem(i['name'])
            else:
                self.ui.lst_action_list.addItem(functions.countdown.make_auto_sentence(i))

    def update_effects(self):
        self.ui.lst_disabled_effect.clear()
        self.ui.lst_enabled_effect.clear()
        self.disabled_effects.clear()
        for i in self.enabled_effects:
            if i in functions.plugins.effects:
                item = QListWidgetItem(functions.plugins.effects[i].effect_friendly_name)
                item.setToolTip(functions.plugins.effects[i].effect_description)
                self.ui.lst_enabled_effect.addItem(item)
            else:
                self.ui.lst_enabled_effect.addItem(i)
        for i in functions.plugins.effects:
            if i in self.enabled_effects:
                continue
            item = QListWidgetItem(functions.plugins.effects[i].effect_friendly_name)
            item.setToolTip(functions.plugins.effects[i].effect_description)
            self.ui.lst_disabled_effect.addItem(item)
            self.disabled_effects.append(i)

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
        self.cfg.cfg['window']['skip_taskbar'] = self.ui.cb_skip_taskbar.isChecked()
        # effects
        self.cfg.cfg['effects'] = copy.deepcopy(self.local_effect)
        # auto
        self.cfg.cfg['automate_enabled'] = self.ui.cb_auto_enabled.isChecked()
        self.cfg.cfg['automate'] = copy.deepcopy(self.local_automate)
        # style
        self.save_widget_style(self.last_style_widget)

        self.cfg.write()
        if self.update_trigger is not None:
            self.update_trigger()
        self.ui.style_preview.setStyleSheet(functions.appearance.mk_qss(self.cfg.cfg['style'], self.cfg.cfg['style_enabled']))
        self.app.postEvent(self.app.profile_mgr_ui, QEvent(wcdapp.ProfileUpdatedEvent))
        self.load_val()

    def on_btn_effect_enable_released(self):
        if len(self.ui.lst_disabled_effect.selectedItems()) <= 0:
            return
        eid = self.disabled_effects[self.ui.lst_disabled_effect.currentIndex().row()]
        self.enabled_effects.append(eid)
        self.local_effect[eid] = {}
        self.update_effects()

    def on_btn_effect_disable_released(self):
        if len(self.ui.lst_enabled_effect.selectedItems()) <= 0:
            return
        eid = self.enabled_effects[self.ui.lst_enabled_effect.currentIndex().row()]
        self.enabled_effects.remove(eid)
        self.local_effect.pop(eid)
        self.update_effects()

    def on_btn_effect_configure_released(self):
        eid = self.enabled_effects[self.ui.lst_enabled_effect.currentIndex().row()]
        self.econfigure = UniverseConfigure(self.local_effect[eid], functions.plugins.effects[eid].default_config)
        self.econfigure.show()

    def on_lst_enabled_effect_currentRowChanged(self):
        if len(self.enabled_effects) <= 0:
            self.ui.btn_effect_configure.setEnabled(False)
            return
        if self.enabled_effects[self.ui.lst_enabled_effect.currentIndex().row()] in functions.plugins.effects:
            self.ui.btn_effect_configure.setEnabled(bool(
                functions.plugins.effects[self.enabled_effects[self.ui.lst_enabled_effect.currentIndex().row()]].default_config))
        else:
            self.ui.btn_effect_configure.setEnabled(False)

    def on_cb_widgets_currentTextChanged(self, text):
        if not self._final:
            return
        self.save_widget_style(self.last_style_widget)
        self.load_widget_style(properties.countdown_widget_id[self.ui.cb_widgets.currentIndex()])
        self.last_style_widget = properties.countdown_widget_id[self.ui.cb_widgets.currentIndex()]

    def on_btn_action_cfg_released(self):
        if self.ui.lst_action_list.count() > 0:
            self.auto_cfg[self.ui.lst_action_list.currentRow()].show()

    def on_btn_new_action_released(self):
        self.local_automate.append(copy.deepcopy(properties.default_automate_section))
        self.refresh_automate_ui()
        self.auto_cfg[len(self.auto_cfg) - 1].show()

    def on_btn_rm_action_released(self):
        if self.ui.lst_action_list.count() > 0:
            del self.local_automate[self.ui.lst_action_list.currentRow()]
            self.refresh_automate_ui()

    def on_btn_trust_released(self):
        r = QMessageBox.warning(self, '信任本倒计时',
                                '你要信任倒计时{}吗？请确保您已经仔细检查过倒计时并确认倒计时没有风险。'.format(self.cfg.cfg['countdown']['title']),
                                buttons=QMessageBox.Yes | QMessageBox.No,
                                defaultButton=QMessageBox.No)
        if r == QMessageBox.Yes:
            self.cfg.cfg['trusted'] = True
            self.on_btn_apply_released()

    def load_widget_style(self, widget):
        style_root = functions.base.default_pass(self.cfg.cfg['style'][widget], properties.default_widget_style)
        state_root = functions.base.default_pass(self.cfg.cfg['style_enabled'][widget], properties.default_widget_enabled)
        # value
        self.ui.btn_bgcolor.setText(style_root['background-color'])
        self.ui.le_bgpic.setText(style_root['background-image'][4:-1])
        if style_root['background-repeat'] == 'repeat':
            self.ui.cb_clip_bg.setChecked(True)
        else:
            self.ui.cb_clip_bg.setChecked(False)
        self.ui.cb_bgpos1.setCurrentText(style_root['background-position'].split(' ')[0])
        self.ui.cb_bgpos2.setCurrentText(style_root['background-position'].split(' ')[1])
        self.ui.btn_font.setText(style_root['font'])
        self.ui.btn_color.setText(style_root['color'])
        self.ui.sb_radius.setValue(style_root['border-radius'])
        self.ui.sb_bordersize.setValue(style_root['border-width'])
        self.ui.btn_bordercolor.setText(style_root['border-color'])
        self.ui.cb_border_style.setCurrentText(style_root['border-style'])

        # state
        att = [i for i in state_root]
        att.remove('background-repeat')
        wid = [self.ui.lb_bgcolor, self.ui.lb_bgpic, self.ui.lb_bgpos, self.ui.lb_font,
               self.ui.lb_color, self.ui.lb_radius, self.ui.lb_border_size, self.ui.lb_border_color,
               self.ui.lb_border_style]
        for i in range(9):
            wid[i].setChecked(state_root[att[i]])

        self.ui.cb_custom_border.setChecked(bool(self.ui.lb_border_style.isChecked() and
                                                 self.ui.lb_border_size.isChecked() and
                                                 self.ui.lb_border_color.isChecked()))

    def save_widget_style(self, widget):
        style_root = self.cfg.cfg['style'][widget]
        state_root = self.cfg.cfg['style_enabled'][widget]

        # value
        style_root['background-color'] = self.ui.btn_bgcolor.text()
        style_root['background-image'] = 'url({})'.format(self.ui.le_bgpic.text())
        if self.ui.cb_clip_bg.isChecked():
            style_root['background-repeat'] = 'repeat'
        else:
            style_root['background-repeat'] = 'no-repeat'
        style_root['background-position'] = ' '.join([i.currentText() for i in [self.ui.cb_bgpos1, self.ui.cb_bgpos2]])
        style_root['font'] = self.ui.btn_font.text()
        style_root['color'] = self.ui.btn_color.text()
        style_root['border-radius'] = self.ui.sb_radius.value()
        style_root['border-width'] = self.ui.sb_bordersize.value()
        style_root['border-color'] = self.ui.btn_bordercolor.text()
        style_root['border-style'] = self.ui.cb_border_style.currentText()

        # state
        att = [i for i in state_root]
        att.remove('background-repeat')
        wid = [self.ui.lb_bgcolor, self.ui.lb_bgpic, self.ui.lb_bgpos, self.ui.lb_font,
               self.ui.lb_color, self.ui.lb_radius, self.ui.lb_border_size, self.ui.lb_border_color,
               self.ui.lb_border_style]
        for i in range(9):
            state_root[att[i]] = wid[i].isChecked()

    def on_btn_bgcolor_released(self):
        colr_sel = QColorDialog.getColor(initial=QColor(self.ui.btn_bgcolor.text()), title='选择背景颜色')
        rgb = colr_sel.getRgb()
        self.ui.btn_bgcolor.setText(functions.appearance.rgb2hex(rgb[0], rgb[1], rgb[2]))

    def on_btn_color_released(self):
        colr_sel = QColorDialog.getColor(initial=QColor(self.ui.btn_color.text()), title='选择颜色')
        rgb = colr_sel.getRgb()
        self.ui.btn_color.setText(functions.appearance.rgb2hex(rgb[0], rgb[1], rgb[2]))

    def on_btn_bordercolor_released(self):
        colr_sel = QColorDialog.getColor(initial=QColor(self.ui.btn_bordercolor.text()), title='选择边框颜色')
        rgb = colr_sel.getRgb()
        self.ui.btn_bordercolor.setText(functions.appearance.rgb2hex(rgb[0], rgb[1], rgb[2]))

    def on_cb_custom_border_stateChanged(self, state):
        for i in (self.ui.lb_border_size, self.ui.lb_border_style, self.ui.lb_border_color):
            i.setChecked(self.ui.cb_custom_border.isChecked())

    def on_btn_browse_bgpic_released(self):
        path = QFileDialog.getOpenFileName(self, '打开图片文件', filter='图片文件(*.png *.svg *.bmp *.jpg *.jpeg *.gif);;所有文件(*.*)')
        if path[0] == '':
            return
        self.ui.le_bgpic.setText(path[0])

    def on_btn_font_released(self):
        font_l = self.ui.btn_font.text().split(' ')
        if len(font_l) == 3:
            font_r = QFont(font_l[2])
            font = QFontDialog.getFont(font_r, self)
        else:
            font = QFontDialog.getFont(self)
        # print(font)
        if font[1]:
            self.ui.btn_font.setText(' '.join([str(i) for i in [font[0].styleName(),
                                                                str(font[0].pointSize()) + 'px', font[0].family()]]))


