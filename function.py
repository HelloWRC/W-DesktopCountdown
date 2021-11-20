from PyQt5.QtCore import QEvent
import time
import json


QEventLoopInit_Type = QEvent.registerEventType()  # 注册事件

version = 'develop'


class QEventLoopInit(QEvent):
    def __init__(self):
        super().__init__(QEventLoopInit_Type)


class ConfigMgr:
    def __init__(self, file_path: str, target_class, mapping: dict):
        self.file_path = file_path
        self.mapping = mapping
        self.target_class = target_class
        self.parsed_cfg: dict

    def load_config(self):
        pass

    def write_config(self):
        pass


def get_qss(path: str):
    with open(path, 'r') as qss:
        return qss.read()