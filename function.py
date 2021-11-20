from PyQt5.QtCore import QEvent


QEventLoopInit_Type = QEvent.registerEventType()  # 注册事件

version = 'develop'


class QEventLoopInit(QEvent):
    def __init__(self):
        super().__init__(QEventLoopInit_Type)

