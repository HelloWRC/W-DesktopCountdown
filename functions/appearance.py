import copy
import logging
import re

import UIFrames.countdown
import functions.plugins
from data import effects
import properties
import wcdapp
from functions.base import ConfigFileMgr


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


class EffectManager:
    def __init__(self, countdown, app, config):
        self.countdown: UIFrames.countdown.CountdownWin = countdown
        self.app: wcdapp.WDesktopCD = app
        self.config: ConfigFileMgr = config
        self.effects = {}

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
            for k in functions.plugins.effects[i].default_config:
                if functions.plugins.effects[i].default_config[k]['type'] == 'label':
                    continue
                if k not in config[i]:
                    config[i][k] = functions.plugins.effects[i].default_config[k]['default']
            self.effects[i] = functions.plugins.effects[i](self.app, self.countdown, config[i])
            self.effects[i].set_enabled()
            logging.info('enabled effect: %s', i)
        for i in changed_effects:
            for k in functions.plugins.effects[i].default_config:
                if functions.plugins.effects[i].default_config[k]['type'] == 'label':
                    continue
                if k not in config[i]:
                    config[i][k] = functions.plugins.effects[i].default_config[k]['default']
            self.effects[i].update_config(config[i])
            logging.info('updated effects: %s', i)


def mk_qss(style: dict, states: dict):
    result = []
    for i in style:
        main_section = []
        for k in style[i]:
            if states[i][k]:
                main_section.append('  {}: {}'.format(k, style[i][k]))
        result.append('#' + i + '{\n' + ';\n'.join(main_section) + '}')
    return '\n'.join(result) + '#Countdown{background: rgba(0, 0, 0, 0)}'


def hexcnv(color: int):
    t1 = re.search(r'(?<=0x[0-f]{2})([0-f]{6})', str(hex(color))).groups()[0]
    # print(t1)
    t2 = t1[4:6] + t1[2:4] + t1[0:2]
    return '#{}'.format(t2)