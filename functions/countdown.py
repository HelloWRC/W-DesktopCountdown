import copy
import logging
import os
from string import Template

from PyQt5.QtCore import QEvent, QObject

import UIFrames.countdown
import UIFrames.profile_config_ui
import functions.plugins
import properties
import wcdapp
from functions.base import ConfigFileMgr, filename_chk
from properties import profile_prefix, default_profile_name, qss_prefix
from functions.hook import hook_target

path_root = 'functions.countdown.'

QEventLoopInit_Type = QEvent.registerEventType()  # 注册事件


class DeltaTemplate(Template):
    delimiter = "%"


@hook_target(path_root + 'strfdelta')
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
    @hook_target(path_root + 'ProfileMgr.__init__')
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
                                                                                          self.config_mgr[
                                                                                              default_profile_name],
                                                                                          default_cfg=True)
        status = 50
        if (len(self.profiles)-1) > 0:
            step = 35 / (len(self.profiles)-1)
        else:
            step = 35
        for i in self.profiles:
            status += step
            self.app.splash.update_status(status, '正在加载倒计时：{}'.format(i))
            if i == default_profile_name:
                continue
            self.config_mgr[i] = ConfigFileMgr(profile_prefix + i, self.config_mgr[default_profile_name].cfg)
            self.countdowns_win[i] = UIFrames.countdown.CountdownWin(self.app, i, self.config_mgr[i])
            self.config_ui[i] = self.countdowns_win[i].config_ui

    @hook_target(path_root + 'ProfileMgr.load_profiles_list')
    def load_profiles_list(self):
        self.profiles = os.listdir(profile_prefix)
        logging.info('loaded configs: %s', self.profiles)

    @hook_target(path_root + 'ProfileMgr.spawn_countdown_win')
    def spawn_countdown_win(self, name: str):
        self.config_mgr[name] = ConfigFileMgr(profile_prefix +
                                              name, self.countdown_cfg_default)
        self.countdowns_win[name] = UIFrames.countdown.CountdownWin(self.app, qss_prefix + name, )
        self.config_ui[name] = self.countdowns_win[name].config_ui
        logging.info('spawned window: %s', name)

    @hook_target(path_root + 'ProfileMgr.close_countdown_win')
    def close_countdown_win(self, name: str):
        self.countdowns_win[name].close()

    @hook_target(path_root + 'ProfileMgr.create_profile')
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
        self.app.plugin_mgr.on_countdown_created(self.countdowns_win[name])

    @hook_target(path_root + 'ProfileMgr.import_profile')
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

    @hook_target(path_root + 'ProfileMgr.remove_profile')
    def remove_profile(self, name: str):
        logging.info('removing profile: %s', name)
        self.app.plugin_mgr.on_countdown_removed(self.countdowns_win[name])
        self.config_mgr[name].write()
        self.countdowns_win[name].close()
        self.config_ui[name].close()
        self.config_mgr[name].remove()
        del self.config_mgr[name]
        del self.countdowns_win[name]
        del self.config_ui[name]
        self.profiles.remove(name)
        self.app.postEvent(self.app.profile_mgr_ui, QEvent(wcdapp.ProfileFileEvent))

    @hook_target(path_root + 'ProfileMgr.reset_profile')
    def reset_profile(self, name):
        title = self.config_mgr[name].cfg['countdown']['title']
        start = self.config_mgr[name].cfg['countdown']['start']
        end = self.config_mgr[name].cfg['countdown']['end']

        self.config_mgr[name].set_default()
        self.config_mgr[name].cfg['countdown']['title'] = title
        self.config_mgr[name].cfg['countdown']['start'] = start
        self.config_mgr[name].cfg['countdown']['end'] = end

        self.update_all_defaults()

    @hook_target(path_root + 'ProfileMgr.set_as_default')
    def set_as_default(self, name):
        self.config_mgr[default_profile_name].cfg = copy.deepcopy(self.config_mgr[name].cfg)
        self.config_mgr[default_profile_name].cfg['automate'].clear()
        self.update_all_defaults()

    @hook_target(path_root + 'ProfileMgr.update_all_defaults')
    def update_all_defaults(self):
        for i in self.profiles:
            if i == default_profile_name:
                continue
            self.config_mgr[i].mapping = self.config_mgr[default_profile_name].cfg


class Automate:
    def __init__(self, app, countdown, config):
        self.app = app
        self.countdown = countdown
        self.triggers = []
        self.actions = []
        self.config = functions.base.default_pass(config, properties.default_automate_section)
        self.trigger_type = 0

        for i in self.config['triggers']:
            if i['id'] in functions.plugins.triggers:
                self.triggers.append(functions.plugins.triggers[i['id']](self.app, self.countdown,
                                                                         functions.base.rich_default_pass(
                                                                             functions.plugins.triggers[i['id']].default_config,
                                                                             i['config'])))
            else:
                logging.error('Trigger %s not found! skipped.', i)
        for i in self.config['actions']:
            if i['id'] in functions.plugins.actions:
                self.actions.append(functions.plugins.actions[i['id']](self.app, self.countdown,
                                                                       functions.base.rich_default_pass(
                                                                           functions.plugins.actions[i['id']].default_config,
                                                                       i['config'])))
            else:
                logging.error('Action %s not found! skipped.', i)
        self.trigger_type = config['trigger_type']

    def update(self):
        passed = False
        for trigger in self.triggers:
            if trigger.check() and self.trigger_type == 0:
                passed = True
                break
            if not trigger.check() and self.trigger_type == 1:
                break
        if not passed:
            return

        for action in self.actions:
            action.run()

    def __del__(self):
        pass


class AutomateMgr:
    @hook_target(path_root + 'AutomateMgr.__init__')
    def __init__(self, app, countdown):
        self.app = app
        self.countdown: UIFrames.countdown.CountdownWin = countdown
        self.config = []
        self.autos = []
        logging.info('loaded automate manager of %s.', self.countdown.name)

    @hook_target(path_root + 'AutomateMgr.load_config')
    def load_config(self, config):
        self.autos.clear()
        self.config = config
        for auto in self.config:
            self.autos.append(Automate(self.app, self.countdown, auto))

    @hook_target(path_root + 'AutomateMgr.update')
    def update(self):
        for auto in self.autos:
            auto.update()


def make_auto_sentence(config):
    triggers = config['triggers']
    actions = config['actions']
    trigger_type = config['trigger_type']
    trigger_paras = []
    action_paras = []

    for trigger in triggers:
        if trigger['id'] not in functions.plugins.triggers:
            trigger_paras.append(trigger['id'])
        else:
            trigger_paras.append(functions.plugins.triggers[trigger['id']].trigger_name)
    for action in actions:
        if action['id'] not in functions.plugins.actions:
            action_paras.append(action['id'])
        else:
            action_paras.append(functions.plugins.actions[action['id']].action_name)

    if trigger_type == 1:
        trigger_sentence = '，并且'.join(trigger_paras)
    else:
        trigger_sentence = '，或者'.join(trigger_paras)
    action_sentence = '，然后'.join(action_paras)
    return '当{}，就{}。'.format(trigger_sentence, action_sentence)
