import json
import logging
import os
import platform

import properties

def call_browser(link: str):
    if platform.system() == 'Windows':
        os.system('start {}'.format(link))
    elif platform.system() == 'Linux':
        os.system('call-browser {} &'.format(link))


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


def filename_chk(name):
    if name == '':
        name = 'countdown'
    for i in ('*', '?', '/', '\\', '|', ':', '<', '>'):
        if i in name:
            name = 'countdown'
    if os.path.exists(properties.profile_prefix + name):
        name = name + '_'
    return name