from PyQt5.QtWidgets import QFrame, QPushButton
from PyQt5.QtGui import QPixmap
from UIFrames.ui_cob_block import Ui_Frame
import os


class CobBlock(QFrame):
    def __init__(self, config):
        super(CobBlock, self).__init__()
        self.ui = Ui_Frame()
        self.ui.setupUi(self)
        self.config = config
        self.ui.lb_icon.setScaledContents(True)
        self.ui.lb_icon.setFixedSize(64, 64)
        self.ui.lb_icon.setPixmap(QPixmap(self.config['icon']))
        self.ui.lb_content.setText(self.config['content'])
        self.ui.lb_title.setText('<h3>{}</h3>'.format(self.config['title']))

        self.links = []
        index = 0
        for i in self.config['links']:
            button = QPushButton()
            button.setText(i['text'])
            button.setFlat(True)
            self.links.append(lambda: os.startfile(i['link']))
            button.released.connect(self.links[index])
            index += 1
            self.ui.lb_links.setText(' '.join(['<a href="{}">{}</a>'.format(i['link'], i['text']) for i in self.config['links']]))
