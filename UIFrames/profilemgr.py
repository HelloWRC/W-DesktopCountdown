import logging
import function
from UIFrames.ui_profilemgr import Ui_ProfileMgr
from PyQt5.QtWidgets import QMainWindow


class ProfileMgrUI(QMainWindow):
    def __init__(self, app):
        super(ProfileMgrUI, self).__init__()
        self.ui = Ui_ProfileMgr()
        self.ui.setupUi(self)
        self.app = app

