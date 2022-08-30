import copy
import logging
import platform
import re

import UIFrames.countdown
import functions.plugins
from data import effects
import properties
import wcdapp
from functions.base import ConfigFileMgr
from functions.hook import hook_target

path_root = 'functions.appearance.'


@hook_target(path_root + 'rgb2hex')
def rgb2hex(r, g, b):
    hexc = []
    for i in (r, g, b):
        s = str(hex(i))[2:]
        if len(s) < 2:
            s = '0' + s
        hexc.append(s)
    return '#{}{}{}'.format(hexc[0], hexc[1], hexc[2])


@hook_target(path_root + 'gen_custom_theme')
def gen_custom_theme(filename, accent_color, is_dark_theme):
    if is_dark_theme:
        temple = properties.DARK_THEME_TEMPLE
    else:
        temple = properties.LIGHT_THEME_TEMPLE
    temple = temple.format(accent_color, accent_color)
    with open(filename, 'w') as theme:
        theme.write(temple)


class EffectManager:
    @hook_target(path_root + 'EffectManager.__init__')
    def __init__(self, countdown, app, config):
        self.countdown: UIFrames.countdown.CountdownWin = countdown
        self.app: wcdapp.WDesktopCD = app
        self.config: ConfigFileMgr = config
        self.effects = {}

    @hook_target(path_root + 'EffectManager.load_config')
    def load_config(self, config=None):
        if config is None:
            config = self.config
        else:
            self.config = copy.deepcopy(config)
        new_effects = []
        rm_effects = []
        changed_effects = []
        for i in config:
            if i not in functions.plugins.effects:
                continue
            if i not in self.effects:
                new_effects.append(i)
        for i in self.effects:
            if i not in functions.plugins.effects:
                continue
            if i not in config:
                rm_effects.append(i)
        for i in config:
            if i not in functions.plugins.effects:
                continue
            if i in new_effects:
                continue
            changed_effects.append(i)

        for i in rm_effects:
            self.effects[i].unload()
            self.effects.pop(i)
            logging.info('unloaded effects: %s', i)
        for i in new_effects:
            functions.base.rich_default_pass(functions.plugins.effects[i].default_config, config[i])
            effect = functions.plugins.effects[i]
            self.effects[i] = effect(effect.plugin_api__, self.countdown, config[i])
            self.effects[i].set_enabled()
            logging.info('enabled effect: %s', i)
        for i in changed_effects:
            for k in functions.plugins.effects[i].default_config:
                if not functions.plugins.cfg_views[functions.plugins.effects[i].default_config[k]['view']].can_store:
                    continue
                if k not in config[i]:
                    config[i][k] = functions.plugins.effects[i].default_config[k]['default']
            self.effects[i].update_config(config[i])
            logging.info('updated effects: %s', i)

    @hook_target(path_root + 'EffectManager.on_event')
    def on_event(self, watched, event):
        for effect in self.effects.values():
            if 'on_event' in dir(effect):
                effect.on_event(watched, event)

    @hook_target(path_root + 'EffectManager.on_state_changed')
    def on_state_changed(self, stat):
        for effect in self.effects.values():
            if 'on_state_changed' in dir(effect):
                effect.on_state_changed(stat)

    def unload_all(self):
        for i in self.effects:
            self.effects[i].unload()
            logging.info('unloaded effects: %s', i)


@hook_target(path_root + 'mk_qss')
def mk_qss(style: dict, states: dict):
    result = []
    for i in style:
        main_section = []
        for k in style[i]:
            if states[i][k]:
                main_section.append('  {}: {}'.format(k, style[i][k]))
        result.append('#' + i + '{\n' + ';\n'.join(main_section) + '}')
    return '\n'.join(result) + '#Countdown{background: rgba(0, 0, 0, 0)}'


@hook_target(path_root + 'hexcnv')
def hexcnv(color: int):
    t1 = re.search(r'(?<=0x[0-f]{2})([0-f]{6})', str(hex(color))).groups()[0]
    # print(t1)
    t2 = t1[4:6] + t1[2:4] + t1[0:2]
    return '#{}'.format(t2)


def read_system_settings():
    if 'Windows' in platform.system():
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\DWM') as key:
                properties.system_color = hexcnv(winreg.QueryValueEx(key, 'AccentColor')[0])
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize') as key:
                properties.ld_themes[2] = properties.ld_themes[1 - winreg.QueryValueEx(key, 'AppsUseLightTheme')[0]]
        except:
            pass
    logging.info('Loaded system settings.')
