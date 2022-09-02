import logging
import os
import time

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QColorDialog
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QTextCharFormat, QColor, QTextImageFormat, QBrush, QFont

import UIFrames.universe_configure
from UIFrames.ui_format_edit import Ui_FormatEdit


def text_formatter(func):
    def warp(self, *args, **kwargs):
        if time.time() - self.last_sel_time <= 0.01:
            return
        cursor = self.ui.te_edit.textCursor()
        text_format = QTextCharFormat()
        func(self, text_format, *args, **kwargs)
        cursor.mergeCharFormat(text_format)
    return warp


class FormatEdit(QWidget):
    sig_update_data = pyqtSignal(str)

    placeholder_line = '<p><a href="{}">{}</a><span> - {}</span></p>'
    cfg_insert_link = {
        'heading': {
            'view': 'wdcd.label',
            'text': '<h1>插入链接</h1>'
        },
        'text': {
            'view': 'wdcd.line_edit',
            'name': '显示文本',
            'default': '链接'
        },
        'link': {
            'view': 'wdcd.line_edit',
            'name': '链接',
            'default': 'https://'
        }
    }
    cfg_insert_img = {
        'heading': {
            'view': 'wdcd.label',
            'text': '<h1>插入图片</h1>'
        },
        'path': {
            'view': 'wdcd.file_dialog',
            'name': '图片位置',
            'sel_type': 0,
            'open_mode': 0,
            'file_types': '图片 (*.BMP *.GIF *.JPG *.JPEG *.PNG *.TIFF *.PBM *.PGM *.PPM *.XBM *.XPM *.ICO *.SVG);;任何文件 (*.*)',
            'default': ''
        },
        'd': {
            'view': 'wdcd.label',
            'text': '可以是指向本地文件的相对路径、绝对路径或资源文件。'
        },
        'line': {
            'view': 'wdcd.line'
        },
        'width': {
            'view': 'wdcd.spin_box',
            'type': 'int',
            'name': '宽',
            'default': 64,
            'min': 1,
            'max': 2048
        },
        'height': {
            'view': 'wdcd.spin_box',
            'type': 'int',
            'name': '高',
            'default': 64,
            'min': 1,
            'max': 2048
        }
    }

    def __init__(self, title, update, placeholders):
        super(FormatEdit, self).__init__()
        self.ui = Ui_FormatEdit()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_AlwaysStackOnTop)
        self.setWindowModality(Qt.ApplicationModal)
        self.sig_update_data.connect(update)
        self.ui.te_edit.selectionChanged.connect(self.update_editor_stat)

        self.setWindowTitle(title)
        self.placeholders = placeholders

        if self.placeholders:
            for i in self.placeholders:
                self.ui.lb_placeholders.setText(self.ui.lb_placeholders.text() +
                                                self.placeholder_line.format(i, i,
                                                                             self.placeholders[i]))
        else:
            self.ui.lb_placeholders.setText('- 空 -')
        self.last_sel_time = 0
        self.color_fg = QColor()
        self.color_bg = QColor()

    def closeEvent(self, event) -> None:
        self.sig_update_data.emit(self.ui.te_edit.toHtml())
    
    def open_edit_window(self, text) -> None:
        self.ui.te_edit.setHtml(text)
        self.ui.te_edit.setStyleSheet('color: {QTMATERIAL_SECONDARYTEXTCOLOR}'.format(**os.environ))
        self.update_editor_stat()
        self.show()

    def update_editor_stat(self):
        self.last_sel_time = time.time()
        cursor = self.ui.te_edit.textCursor()
        text_format = cursor.charFormat()
        self.color_fg = text_format.foreground().color()
        self.color_bg = text_format.background().color()
        self.ui.btn_color.setStyleSheet('color:{}'.format(self.color_fg.name()))
        self.ui.btn_bg_color.setStyleSheet('color:{}'.format(self.color_bg.name()))
        self.ui.cb_font.setCurrentFont(text_format.font())
        self.ui.sb_size.setValue(int(text_format.fontPointSize()))
        self.ui.btn_bold.setChecked(text_format.fontWeight() >= 87.5)
        self.ui.btn_italic.setChecked(text_format.fontItalic())
        self.ui.btn_strike.setChecked(text_format.fontStrikeOut())
        self.ui.btn_underlined.setChecked(text_format.fontUnderline())

    # events
    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()

    # slots
    def on_te_edit_textChanged(self):
        if self.ui.tabWidget_2.currentIndex() == 0:
            self.ui.lb_preview.setText(self.ui.te_edit.toHtml())
            self.ui.te_source.setPlainText(self.ui.te_edit.toHtml())

    def on_te_source_textChanged(self):
        if self.ui.tabWidget_2.currentIndex() == 1:
            self.ui.te_edit.setHtml(self.ui.te_source.toPlainText())
            self.ui.lb_preview.setText(self.ui.te_source.toPlainText())

    def on_lb_placeholders_linkActivated(self, link):
        self.ui.te_edit.textCursor().insertText(link)

    # editor slot
    @text_formatter
    def on_cb_font_currentFontChanged(self, text_format: QTextCharFormat, font: QFont):
        text_format.setFontFamilies([font.family()])

    @text_formatter
    def on_sb_size_valueChanged(self, text_format: QTextCharFormat, size):
        text_format.setFontPointSize(int(size))

    @text_formatter
    def on_btn_bold_toggled(self, text_format: QTextCharFormat, state):
        if state:
            text_format.setFontWeight(88)
        else:
            text_format.setFontWeight(0)

    @text_formatter
    def on_btn_italic_toggled(self, text_format: QTextCharFormat, state):
        text_format.setFontItalic(state)

    @text_formatter
    def on_btn_strike_toggled(self, text_format: QTextCharFormat, state):
        text_format.setFontStrikeOut(state)

    @text_formatter
    def on_btn_underlined_toggled(self, text_format: QTextCharFormat, state):
        text_format.setFontUnderline(state)

    @text_formatter
    def on_btn_color_released(self, text_format: QTextCharFormat):
        inputs = QColorDialog.getColor(self.color_fg, self, '设置文本颜色')
        text_format.setForeground(inputs)
        self.update_editor_stat()

    @text_formatter
    def on_btn_bg_color_released(self, text_format: QTextCharFormat):
        inputs = QColorDialog.getColor(self.color_bg, self, '设置背景颜色')
        text_format.setBackground(inputs)
        self.update_editor_stat()

    @text_formatter
    def on_btn_clear_color_released(self, text_format: QTextCharFormat):
        text_format.setForeground(QBrush())
        text_format.setBackground(QBrush())
        self.update_editor_stat()

    def on_btn_link_released(self):
        config = {}
        self.ucfg_link = UIFrames.universe_configure.UniverseConfigureEXP(config, self.cfg_insert_link, callback=self.callback_link_insert)
        self.ucfg_link.show()

    def callback_link_insert(self, config):
        self.ui.te_edit.textCursor().insertHtml('<a href="{}">{}</a>'.format(config['link'], config['text']))
        self.update_editor_stat()

    def on_btn_image_released(self):
        config = {}
        self.ucfg_image = UIFrames.universe_configure.UniverseConfigureEXP(config, self.cfg_insert_img, callback=self.callback_image_insert)
        self.ucfg_image.show()

    def callback_image_insert(self, config):
        image = QTextImageFormat()
        image.setName(config['path'])
        image.setWidth(config['width'])
        image.setHeight(config['height'])
        self.ui.te_edit.textCursor().insertImage(image)
        self.update_editor_stat()
