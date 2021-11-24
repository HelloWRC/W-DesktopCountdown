from PyQt5.QtCore import QEvent
import time
import json


QEventLoopInit_Type = QEvent.registerEventType()  # 注册事件

version = 'develop'


def default_pass(raw: dict, mapping: dict):
    for i in mapping.keys():
        if i in raw.keys():
            continue
        else:
            raw[i] = mapping[i]
    return raw


class QEventLoopInit(QEvent):
    def __init__(self):
        super().__init__(QEventLoopInit_Type)


class ConfigFileMgr:
    def __init__(self, filename, mapping):
        self.filename = filename
        self.mapping = mapping
        self.cfg = {}

    def load(self, default=True):
        with open(self.filename, 'r') as cf:
            self.cfg = json.load(cf)
        if default:
            self.cfg = default_pass(self.cfg, self.mapping)
        self.write()

    def write(self):
        with open(self.filename, 'w') as cf:
            json.dump(self.cfg, cf)


def get_qss(path: str):
    with open(path, 'r') as qss:
        return qss.read()
