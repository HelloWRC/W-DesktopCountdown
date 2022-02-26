import re

from PyQt5.QtCore import QEvent, QObject
import os
import json
import logging
import copy
from string import Template
import UIFrames.countdown
import UIFrames.new_countdown
import UIFrames.profile_config_ui
import properties
import wcdapp
import platform
from properties import *

QEventLoopInit_Type = QEvent.registerEventType()  # 注册事件


def call_browser(link: str):
    if platform.system() == 'Windows':
        os.system('start {}'.format(link))
    elif platform.system() == 'Linux':
        os.system('call-browser {} &'.format(link))


def rgb2hex(r, g, b):
    hexc = []
    for i in (r, g, b):
        s = str(hex(i))[2:]
        if len(s) < 2:
            s = '0' + s
        hexc.append(s)
    return '#{}{}{}'.format(hexc[0], hexc[1], hexc[2])


def gen_custom_theme(filename, accent_color, is_dark_theme):
    if is_dark_theme:
        temple = properties.DARK_THEME_TEMPLE
    else:
        temple = properties.LIGHT_THEME_TEMPLE
    temple = temple.format(accent_color, accent_color)
    with open(filename, 'w') as theme:
        theme.write(temple)


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

    def set_default(self):
        self.cfg = default_pass({}, self.mapping)
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
        # self.default_cfg = ConfigFileMgr(profile_prefix + default_profile_name, self.countdown_cfg_default)

        if not os.path.exists(profile_prefix):
            os.mkdir(profile_prefix)
        self.load_profiles_list()
        if default_profile_name in self.profiles:
            self.profiles.remove(default_profile_name)
        self.profiles.insert(0, default_profile_name)
        self.config_mgr[default_profile_name] = ConfigFileMgr(profile_prefix + default_profile_name, self.countdown_cfg_default)
        self.config_mgr[default_profile_name].load()
        self.config_ui[default_profile_name] = UIFrames.profile_config_ui.ProfileConfigUI(self.app,
                                                                                          default_profile_name,
                                                                                          self.config_mgr[default_profile_name],
                                                                                          default_cfg=True)
        for i in self.profiles:
            if i == default_profile_name:
                continue
            self.config_mgr[i] = ConfigFileMgr(profile_prefix + i, self.config_mgr[default_profile_name].cfg)
            self.countdowns_win[i] = UIFrames.countdown.CountdownWin(self.app, i, self.config_mgr[i])
            self.config_ui[i] = self.countdowns_win[i].config_ui

    def load_profiles_list(self):
        self.profiles = os.listdir(profile_prefix)
        logging.info('loaded configs: %s', self.profiles)

    def spawn_countdown_win(self, name: str):
        self.config_mgr[name] = ConfigFileMgr(profile_prefix +
                                              name, self.countdown_cfg_default)
        self.countdowns_win[name] = UIFrames.countdown.CountdownWin(self.app, qss_prefix + name, )
        self.config_ui[name] = self.countdowns_win[name].config_ui
        logging.info('spawned window: %s', name)

    def close_countdown_win(self, name: str):
        self.countdowns_win[name].close()

    def create_profile(self, name: str, start_time=0, end_time=0):
        logging.info('creating new profile: %s', name)
        self.profiles.append(name)
        self.config_mgr[name] = ConfigFileMgr(profile_prefix + name, self.config_mgr[default_profile_name].cfg)
        self.config_mgr[name].load()
        self.config_mgr[name].cfg['countdown']['title'] = name
        self.config_mgr[name].cfg['countdown']['start'] = start_time
        self.config_mgr[name].cfg['countdown']['end'] = end_time
        self.config_mgr[name].write()
        self.countdowns_win[name] = UIFrames.countdown.CountdownWin(self.app, name, self.config_mgr[name])
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
        self.countdowns_win[name] = UIFrames.countdown.CountdownWin(self.app, name, self.config_mgr[name])
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

    def reset_profile(self, name):
        title = self.config_mgr[name].cfg['countdown']['title']
        start = self.config_mgr[name].cfg['countdown']['start']
        end = self.config_mgr[name].cfg['countdown']['end']

        self.config_mgr[name].set_default()
        self.config_mgr[name].cfg['countdown']['title'] = title
        self.config_mgr[name].cfg['countdown']['start'] = start
        self.config_mgr[name].cfg['countdown']['end'] = end

        self.update_all_defaults()

    def set_as_default(self, name):
        self.config_mgr[default_profile_name].cfg = copy.deepcopy(self.config_mgr[name].cfg)
        self.update_all_defaults()

    def update_all_defaults(self):
        for i in self.profiles:
            if i == default_profile_name:
                continue
            self.config_mgr[i].mapping = self.config_mgr[default_profile_name].cfg


def get_qss(path: str):
    with open(path, 'r') as qss:
        return qss.read()


def mk_qss(style: dict, states: dict):
    result = []
    for i in style:
        main_section = []
        for k in style[i]:
            if states[i][k]:
                main_section.append('  {}: {}'.format(k, style[i][k]))
        result.append('#' + i + '{\n' + ';\n'.join(main_section) + '}')
    return '\n'.join(result)


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
    if name == '':
        name = 'countdown'
    for i in ('*', '?', '/', '\\', '|', ':', '<', '>'):
        if i in name:
            name = 'countdown'
    if os.path.exists(properties.profile_prefix + name):
        name = name + '_'
    return name


def hexcnv(color: int):
    t1 = re.search(r'(?<=0x[0-f]{2})([0-f]{6})', str(hex(color))).groups()[0]
    # print(t1)
    t2 = t1[4:6] + t1[2:4] + t1[0:2]
    return '#{}'.format(t2)


if 'Windows' in platform.system():
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize') as key:
        properties.ld_themes[2] = properties.ld_themes[1-winreg.QueryValueEx(key, 'AppsUseLightTheme')[0]]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\DWM') as key:
        properties.system_color = hexcnv(winreg.QueryValueEx(key, 'AccentColor')[0])
