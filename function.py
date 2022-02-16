from PyQt5.QtCore import QEvent, QObject
import os
import json
import logging
from string import Template
import UIFrames.countdown
import UIFrames.new_countdown
import UIFrames.profile_config_ui
import wcdapp

QEventLoopInit_Type = QEvent.registerEventType()  # 注册事件

version = '0.2.1 alpha'
log_styles = '[%(asctime)s] [%(threadName)s/%(module)s.%(funcName)s(%(lineno)s)/%(levelname)s] %(message)s'
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
            logging.warning('file %s not found! creating as default...', self.filename)
        if default:
            self.cfg = default_pass(self.cfg, self.mapping)
        self.write()

    def write(self):
        with open(self.filename, 'w') as cf:
            json.dump(self.cfg, cf)
            logging.info('successfully saved to %s', self.filename)

    def remove(self):
        os.remove(self.filename)

    def copy_to(self, path):
        self.filename = path
        self.write()


class ProfileMgr(QObject):

    def __init__(self, app):
        import wcdapp
        self.countdown_cfg_default = UIFrames.countdown.CountdownWin.countdown_config_default

        super().__init__(app)
        self.app: wcdapp.WDesktopCD = app
        self.profiles: list = []
        self.countdowns_win: dict = {}
        self.config_mgr: dict = {}
        self.config_ui: dict = {}

        if not os.path.exists(profile_prefix):
            os.mkdir(profile_prefix)
        self.load_profiles_list()
        for i in self.profiles:
            self.config_mgr[i] = ConfigFileMgr(profile_prefix + i, self.countdown_cfg_default)
            self.countdowns_win[i] = UIFrames.countdown.CountdownWin(self.app, 'style.qss', self.config_mgr[i])
            self.config_ui[i] = self.countdowns_win[i].config_ui

    def load_profiles_list(self):
        self.profiles = os.listdir(profile_prefix)
        logging.info('loaded configs: %s', self.profiles)

    def spawn_countdown_win(self, name: str):
        self.config_mgr[name] = ConfigFileMgr(profile_prefix +
                                              name, self.countdown_cfg_default)
        self.countdowns_win[name] = UIFrames.countdown.CountdownWin(self.app, qss_prefix + name, self.config_mgr[name])
        self.config_ui[name] = self.countdowns_win[name].config_ui
        logging.info('spawned window: %s', name)

    def close_countdown_win(self, name: str):
        self.countdowns_win[name].close()

    def create_profile(self, name: str, start_time=0, end_time=0):
        logging.info('creating new profile: %s', name)
        self.profiles.append(name)
        self.config_mgr[name] = ConfigFileMgr(profile_prefix + name, self.countdown_cfg_default)
        self.config_mgr[name].load()
        self.config_mgr[name].cfg['countdown']['title'] = name
        self.config_mgr[name].cfg['countdown']['start'] = start_time
        self.config_mgr[name].cfg['countdown']['end'] = end_time
        self.config_mgr[name].write()
        self.countdowns_win[name] = UIFrames.countdown.CountdownWin(self.app, 'style.qss', self.config_mgr[name])
        self.config_ui[name] = self.countdowns_win[name].config_ui
        self.config_ui[name].show()
        self.app.postEvent(self.app.profile_mgr_ui, QEvent(wcdapp.ProfileFileEvent))

    def import_profile(self, path):
        logging.info('importing profile %s', path)
        cfm = ConfigFileMgr(path, self.countdown_cfg_default)
        cfm.load()
        name = cfm.cfg['countdown']['title']
        self.profiles.append(name)
        self.config_mgr[name] = cfm
        self.config_mgr[name].copy_to(profile_prefix + filename_chk(name))
        self.countdowns_win[name] = UIFrames.countdown.CountdownWin(self.app, 'style.qss', self.config_mgr[name])
        self.config_ui[name] = self.countdowns_win[name].config_ui
        self.config_ui[name].show()
        self.app.postEvent(self.app.profile_mgr_ui, QEvent(wcdapp.ProfileFileEvent))

    def remove_profile(self, name: str):
        logging.info('removing new profile: %s', name)
        self.config_mgr[name].write()
        self.countdowns_win[name].close()
        self.config_ui[name].close()
        self.config_mgr[name].remove()
        del self.config_mgr[name]
        del self.countdowns_win[name]
        del self.config_ui[name]
        self.profiles.remove(name)
        self.app.postEvent(self.app.profile_mgr_ui, QEvent(wcdapp.ProfileFileEvent))


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


def filename_chk(name):
    import function
    if name == '':
        name = 'countdown'
    if os.path.exists(function.profile_prefix + name):
        name = name + '_'
    return name