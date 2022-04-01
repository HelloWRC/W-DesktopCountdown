import json
import logging
import os
import platform
import copy

import properties
from functions.hook import hook_target

path_root = 'functions.base.'


@hook_target(path_root + 'call_browser')
def call_browser(link: str):
    if platform.system() == 'Windows':
        os.system('start {}'.format(link))
    elif platform.system() == 'Linux':
        os.system('call-browser {} &'.format(link))


@hook_target(path_root + 'default_pass')
def default_pass(raw: dict, default_val: dict, skipped: list = []):
    # print(default_val)
    for i in default_val.keys():
        logging.debug('now is %s', i)
        if i not in raw.keys():
            raw[i] = copy.deepcopy(default_val[i])
            logging.warning('%s not exists, set value as default %s', i, default_val[i])
        if type(default_val[i]) == type(raw[i]) == dict and i not in skipped:
            raw[i] = default_pass(raw[i], default_val[i])
            logging.debug('go into %s', i)
    return raw


class ConfigFileMgr:
    @hook_target(path_root + 'ConfigFileMgr.__init__')
    def __init__(self, filename, mapping):
        self.filename = filename
        self.mapping = mapping
        self.cfg = {}

    @hook_target(path_root + 'ConfigFileMgr.load')
    def load(self, default=True, skip=None):
        if skip is None:
            skip = []
        try:
            with open(self.filename, 'r') as cf:
                self.cfg = json.load(cf)
        except FileNotFoundError:
            logging.warning('file %s not found! creating as default...', self.filename)
        if default:
            self.cfg = default_pass(self.cfg, self.mapping, skip)
        self.write()

    @hook_target(path_root + 'ConfigFileMgr.write')
    def write(self):
        with open(self.filename, 'w') as cf:
            json.dump(self.cfg, cf)
            logging.info('successfully saved to %s', self.filename)

    @hook_target(path_root + 'ConfigFileMgr.remove')
    def remove(self):
        os.remove(self.filename)

    @hook_target(path_root + 'ConfigFileMgr.copy_to')
    def copy_to(self, path):
        self.filename = path
        self.write()

    @hook_target(path_root + 'ConfigFileMgr.set_default')
    def set_default(self):
        self.cfg = default_pass({}, self.mapping)
        self.write()


@hook_target(path_root + 'filename_chk')
def filename_chk(name):
    if name == '':
        name = 'countdown'
    for i in ('*', '?', '/', '\\', '|', ':', '<', '>'):
        if i in name:
            name = 'countdown'
    if os.path.exists(properties.profile_prefix + name):
        name = name + '_'
    return name


@hook_target(path_root + 'rich_default_pass')
def rich_default_pass(default_config, config):
    for k in default_config:
        if default_config[k]['type'] == 'label':
            continue
        if k not in config:
            config[k] = default_config[k]['default']
    return config
