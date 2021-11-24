from PyQt5.QtCore import QEvent
import time
import json
import logging

QEventLoopInit_Type = QEvent.registerEventType()  # 注册事件

version = 'develop'


def default_pass(raw: dict, mapping: dict):
    for i in mapping.keys():
        if i in raw.keys():
            continue
        else:
            raw[i] = mapping[i]
            logging.warning('%s not exists, set value as default %s', i, mapping[i])
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
        try:
            with open(self.filename, 'r') as cf:
                self.cfg = json.load(cf)
        except FileNotFoundError:
            logging.warning('file %s not found!', self.filename)
        if default:
            self.cfg = default_pass(self.cfg, self.mapping)
        self.write()

    def write(self):
        with open(self.filename, 'w') as cf:
            json.dump(self.cfg, cf)
            logging.info('successfully saved to %s', self.filename)


def get_qss(path: str):
    with open(path, 'r') as qss:
        return qss.read()


# ========== TEST ==========
if __name__ == '__main__':
    mapping = {
        'foo' : 1,
        'hello' : {
            'test': 1
        }
    }
    assert default_pass({}, mapping) == mapping
    assert default_pass({'foo' : 11}, mapping) == {
        'foo' : 11,
        'hello' : {
            'test': 1
        }
    }
