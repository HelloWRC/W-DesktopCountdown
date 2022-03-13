import copy
import logging
import os
from string import Template

from PyQt5.QtCore import QEvent, QObject

import UIFrames.countdown
import UIFrames.profile_config_ui
import wcdapp
from functions.base import ConfigFileMgr, filename_chk
from properties import profile_prefix, default_profile_name, qss_prefix

QEventLoopInit_Type = QEvent.registerEventType()  # 注册事件


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    d["H"], rem = divmod(tdelta.seconds, 3600)
    d["M"], d["S"] = divmod(rem, 60)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)


class QEventLoopInit(QEvent):
    def __init__(self):
        super().__init__(QEventLoopInit_Type)


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