import logging
import time

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QInputDialog
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QTextCharFormat, QColor

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
        self.current_color = QColor()

    def closeEvent(self, event) -> None:
        self.sig_update_data.emit(self.ui.te_edit.toHtml())
    
    def open_edit_window(self, text) -> None:
        self.ui.te_edit.setHtml(text)
        self.show()

    def update_editor_stat(self):
        self.last_sel_time = time.time()
        cursor = self.ui.te_edit.textCursor()
        text_format = cursor.charFormat()
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
