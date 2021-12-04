import logging
import function
from UIFrames.ui_profile_config_ui import Ui_ProfileConfigUI
from PyQt5.QtWidgets import QWidget


class ProfileConfigUI(QWidget):
    def __init__(self, app):
        self.app = app
        super(ProfileConfigUI, self).__init__()
        self.ui = Ui_ProfileConfigUI()
        self.ui.setupUi(self)
        self.show()
