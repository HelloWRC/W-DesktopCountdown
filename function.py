from PyQt5.QtCore import QEvent, QObject
import os
import json
import logging
from string import Template
import UIFrames.countdown
import UIFrames.new_countdown

QEventLoopInit_Type = QEvent.registerEventType()  # 注册事件

version = 'develop'
log_styles = '[%(asctime)s] [%(module)s(%(lineno)s)/%(threadName)s/%(funcName)s] [%(levelname)s] %(message)s'
datefmt = '%Y/%m/%d %H:%M:%S'

work_root = './'
profile_prefix = work_root + 'profiles/'
qss_prefix = work_root + 'qss-styles/'


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    d["H"], rem = divmod(tdelta.seconds, 3600)
    d["M"], d["S"] = divmod(rem, 60)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)


def default_pass(raw: dict, default_val: dict):
    # print(default_val)
    for i in default_val.keys():
        logging.debug('now is %s', i)
        if i not in raw.keys():
            raw[i] = default_val[i]
            logging.warning('%s not exists, set value as default %s', i, default_val[i])
        if type(default_val[i]) == type(raw[i]) == dict:
            raw[i] = default_pass(raw[i], default_val[i])
            logging.debug('go into %s', i)
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


class ProfileMgr(QObject):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.profiles: list = []
        self.countdowns_win: dict = {}
        self.config_mgr: dict = {}

        if not os.path.exists(profile_prefix):
            os.mkdir(profile_prefix)

    def load_profiles_list(self):
        self.profiles = os.listdir(profile_prefix)
        logging.info('loaded configs: %s', self.profiles)

    def spawn_countdown_win(self, name: str):
        self.config_mgr[name] = ConfigFileMgr(profile_prefix +
                                              name, UIFrames.countdown.CountdownWin.countdown_config_default)
        self.countdowns_win[name] = UIFrames.countdown.CountdownWin(self.app, qss_prefix + name, self.config_mgr[name])

    def close_countdown_win(self, name: str):
        self.countdowns_win[name].close()

    def create_profile(self, name: str):
        pass

    def remove_profile(self, name: str):
        pass


def get_qss(path: str):
    with open(path, 'r') as qss:
        return qss.read()


# ========== TEST ==========
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format=log_styles,
                        datefmt=datefmt)
    mapping = {
        'foo': 1,
        'hello': {
            'test': 1
        }
    }
    # assert default_pass({}, mapping) == mapping
    # assert default_pass({'foo': 11}, mapping) == {
    #     'foo': 11,
    #     'hello': {
    #         'test': 1
    #     }
    # }
    assert default_pass({'foo': 11, 'hello': {'k': 233}}, mapping) == {
        'foo': 11,
        'hello': {
            'test': 1,
            'k': 233
        }
    }
