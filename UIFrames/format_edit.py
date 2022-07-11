import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from UIFrames.ui_format_edit import Ui_FormatEdit


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

        self.setWindowTitle(title)
        self.placeholders = placeholders

        if self.placeholders:
            for i in self.placeholders:
                self.ui.lb_placeholders.setText(self.ui.lb_placeholders.text() +
                                                self.placeholder_line.format(i, i,
                                                                             self.placeholders[i]))
        else:
            self.ui.lb_placeholders.setText('- 空 -')

    def closeEvent(self, event) -> None:
        self.sig_update_data.emit(self.ui.te_edit.toPlainText())
    
    def open_edit_window(self, text) -> None:
        self.ui.te_edit.setPlainText(text)
        self.show()

    def on_te_edit_textChanged(self):
        self.ui.lb_preview.setText(self.ui.te_edit.toPlainText())

    def on_lb_placeholders_linkActivated(self, link):
        self.ui.te_edit.textCursor().insertText(link)
