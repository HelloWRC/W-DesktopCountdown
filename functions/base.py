import json
import logging
import os
import platform
import copy
import subprocess
import sys
import time
import zipfile

import requests

import properties
import wcdapp
from functions.hook import hook_target

from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal

path_root = 'functions.base.'


@hook_target(path_root + 'call_browser')
def call_browser(link: str):
    logging.info('Opening link in browser: %s', link)
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


class UpdateMgr(QObject):
    # status
    UnSupport = -1
    UnChecked = 0
    UpToDate = 1
    UpdateAvailable = 2
    UpdateDownloaded = 3

    # slots
    update_status = pyqtSignal(str)
    
    def __init__(self, app, config):
        super(UpdateMgr, self).__init__()
        self.app: wcdapp.WDesktopCD = app
        self.cfg = config
        self.source_co = ConfigFileMgr(properties.update_meta, properties.update_meta_default)
        self.source_co.load()
        self.source = self.source_co.cfg
        self.status = self.UnChecked
        self.latest_version = None
        self.download_target = ''
        self.downloading = False
        self.update_thread = UpdateThread(self)
        self.update_thread.sig_start_download.connect(self.download_update)
        self.update_thread.sig_restart.connect(self.post_restart_to_update)

        self.restart_to_update = None

    def install_update(self):
        pass

    def check_update(self):
        logging.info('Checking updates...')
        branch = self.cfg['download']['branch']
        channel = self.cfg['download']['channel']
        version = self.source['branches'][branch]['channels'][channel]['version']

        if version is None:
            self.status = self.UpToDate
            self.latest_version = None
            logging.info('No version in current channel.')
            return

        if self.source['versions'][version]['version_id'] > properties.version_id:
            self.status = self.UpdateAvailable
            self.latest_version = self.source['versions'][version]['version_name']
            logging.info('Found update (%s -> %s)', properties.version_id, self.source['versions'][version]['version_id'])
        else:
            self.status = self.UpToDate
            self.latest_version = None
            logging.info('Already up to date.')

    def refresh_source(self):
        logging.info('Refreshing sources from %s', properties.update_source)
        re = requests.get(properties.update_source)
        re.raise_for_status()
        self.source = re.json()
        self.source_co.cfg = self.source
        self.source_co.write()
        logging.info('Successfully refreshed sources.')

    def load_config(self, config):
        self.cfg = config
        branch = self.cfg['download']['branch']
        channel = self.cfg['download']['channel']
        if branch != '' and channel != '':
            version = self.source['branches'][branch]['channels'][channel]['version']
            self.download_target = self.source['versions'][version]['download']
        else:
            self.download_target = ''

        if self.can_update():
            self.status = self.cfg['status']
        else:
            self.status = self.UnSupport

    def save_config(self):
        self.cfg['status'] = self.status

    def post_restart_to_update(self, path=None):
        self.restart_to_update = path
        self.app.quit()

    def update_progress(self):
        if self.restart_to_update is not None:
            subprocess.Popen('{} -u1 {} -ulv {}'.format(self.restart_to_update, sys.argv[0], properties.version_id))

    def download_update(self, target):
        pass

    def can_update(self):
        if sys.argv[0][-3] == '.py' or sys.argv[0][-4] == '.pyw':
            return False
        return True


class UpdateThread(QThread):
    action_download = 1
    action_install = 2

    sig_status = pyqtSignal(int, str)
    sig_restart = pyqtSignal(str)
    sig_start_download = pyqtSignal()
    sig_start_install = pyqtSignal()

    def __init__(self, update_mgr):
        super(UpdateThread, self).__init__()
        self.update_mgr: UpdateMgr = update_mgr
        self.action_type = -1
        self.setObjectName('UpdateThread')
        self.stopped = False

    def launch(self, action):
        self.action_type = action
        self.stopped = False
        self.start(QThread.LowestPriority)

    def run(self) -> None:
        try:
            self.sig_status.emit(-2, '正在准备从{}下载……'.format(self.update_mgr.download_target))
            rq = requests.get(self.update_mgr.download_target, stream=True, timeout=5000)
            size = int(rq.headers.get('Content-Length'))
            logging.info('Download size: %s', size)

            if rq.status_code != 200:
                return

            downloaded = 0
            last_updated = time.time()
            if self.stopped:
                self.finish()
                return
            with open('update.exe', 'wb') as upd:
                for i in rq.iter_content(32):
                    progress = int(downloaded / size * 100)
                    downloaded += upd.write(i)
                    if time.time() - last_updated >= 0.1:
                        self.sig_status.emit(progress, '已下载：{:.2f}MB/{:.2f}MB'.format(downloaded/(1024 * 1024), size/(1024 * 1024)))
                        last_updated = time.time()
                    if self.stopped:
                        self.finish()
                        return

            self.finish()
            logging.info('Download completed.')

            if self.action_type == self.action_install:
                self.sig_status.emit(0, '正在重启应用…')
                self.sig_restart.emit('update.exe')
        except Exception as exp:
            self.sig_status.emit(0, '无法下载更新：{}'.format(exp))

    def stop(self):
        self.stopped = True

    def finish(self):
        self.sig_status.emit(-1, '')
        try:
            os.remove('update.exe')
        except:
            pass

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
