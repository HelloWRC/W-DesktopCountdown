from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QUrl

from UIFrames.ui_licenses import Ui_LicenseRead


class LicenseRead(QWidget):
    def __init__(self, father):
        QWidget.__init__(self)
        self.ui = Ui_LicenseRead()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_AlwaysStackOnTop)
        self.setWindowModality(Qt.ApplicationModal)
        self.father = father

        self.ui.textBrowser.setSource(QUrl('qrc:///LICENSE'), 4)
