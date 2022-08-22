import copy
import importlib
import json
import sys

import UIFrames.universe_configure
import UIFrames.plugin_info
import properties
import os
import logging

import functions.base
from functions.hook import hook_target
from abc import *
from PyQt5.QtWidgets import QWidget

path_root = 'functions.plugins.'

effects = {}
actions = {}
triggers = {}
cfg_views = {}


class PluginAPI:
    def __init__(self):
        """
        插件API
        """
        pass

    def get_self_module(self):
        """
        获得当前插件的模块对象

        :return: 插件对象
        """
        pass

    def get_plugin_module(self, plugin_id):
        """
        获得指定插件的模块对象

        :param plugin_id: 插件id
        :return: 插件对象
        """
        pass

    def toast(self, parent, text, timeout=5):
        """
        显示Toast
        """
        pass

    def hook(self):
        """
        对指定函数上钩
        """
        pass


class Plugin:
    @hook_target(path_root + 'Plugin.__init__')
    def __init__(self, app, module_path):
        import wcdapp
        self.app: wcdapp.WDesktopCD = app
        self.module_path = module_path
        self.module = None
        self.plugin_config_ui = None
        self.plugin_info_ui = None
        self.plugin_default_cfg = {}
        self.plugin_config = {}

        self.plugin_id = ''
        self.plugin_name = ''
        self.description = ''
        self.author = ''
        self.website = ''
        self.plugin_actions = []

        self.provided_effects = {}
        self.provided_triggers = {}
        self.provided_actions = {}
        self. provided_views = {}
        self.tray_actions = {}
        self.pm_actions = {}

    @hook_target(path_root + 'Plugin.load_plugin')
    def load_plugin(self):
        logging.info('loading plugin as py package: %s', self.module_path
                     )
        self.module = importlib.import_module(self.module_path)
        self.plugin_id = self.module.plugin_id
        self.plugin_name = self.module.plugin_name
        logging.info('Loading plugin %s', self.plugin_id)
        if 'plugin_default_config' in dir(self.module):
            self.plugin_default_cfg = self.module.plugin_default_config
        if self.plugin_id not in self.app.app_cfg.cfg['plugins']:
            self.app.app_cfg.cfg['plugins'][self.plugin_id] = {}
        self.plugin_config = functions.base.rich_default_pass(self.plugin_default_cfg,
                                                              self.app.app_cfg.cfg['plugins'][self.plugin_id])
        if 'plugin_configure_ui' in dir(self.module) and self.module.plugin_configure_ui is not None:
            self.plugin_config_ui = self.module.plugin_configure_ui
        else:
            if self.plugin_default_cfg:
                self.plugin_config_ui = UIFrames.universe_configure.UniverseConfigureEXP(self.plugin_config,
                                                                                         self.plugin_default_cfg)
            else:
                self.plugin_config_ui = None

        if 'plugin_author' in dir(self.module):
            self.author = self.module.plugin_author
        if 'plugin_description' in dir(self.module):
            self.description = self.module.plugin_description
        if 'plugin_website' in dir(self.module):
            self.website = self.module.plugin_website
        if 'plugin_actions' in dir(self.module):
            self.plugin_actions = self.module.plugin_actions

        if 'provided_effects' in dir(self.module):
            for effect in self.module.provided_effects:
                effects[effect.effect_id] = effect
                self.provided_effects[effect.effect_id] = effect
                logging.info('Loaded effect %s', effect.effect_id)
        if 'provided_actions' in dir(self.module):
            for action in self.module.provided_actions:
                actions[action.action_id] = action
                self.provided_actions[action.action_id] = action
                logging.info('Loaded action %s', action.action_id)
        if 'provided_triggers' in dir(self.module):
            for trigger in self.module.provided_triggers:
                triggers[trigger.trigger_id] = trigger
                self.provided_triggers[trigger.trigger_id] = trigger
                logging.info('Loaded trigger %s', trigger.trigger_id)
        if 'provided_cfg_views' in dir(self.module):
            for view in self.module.provided_cfg_views:
                cfg_views[view.view_id] = view
                self.provided_views[view.view_id] = view
                logging.info('Loaded cfg view %s', view.view_id)

        self.module.on_load(self.plugin_config, self.app)

        logging.info('Loaded plugin: %s', self.plugin_id)

    @hook_target(path_root + 'Plugin.load_v2')
    def load_v2(self):
        if 'countdownmgr_toolbar_actions' in dir(self.module):
            self.app.profile_mgr_ui.ui.toolBar.addActions(self.module.countdownmgr_toolbar_actions)
            self.pm_actions = self.module.countdownmgr_toolbar_actions
        if 'app_menu_actions' in dir(self.module):
            self.app.tray.menu.addActions(self.module.app_menu_actions)
            self.tray_actions = self.module.app_menu_actions

        logging.info('v2 loading plugin %s', self.plugin_id)
        self.plugin_info_ui = UIFrames.plugin_info.PluginInfo(self)
        if 'on_appinit_p2' in dir(self.module):
            self.module.on_appinit_p2(self.app)
        logging.info('completed v2 load for plugin %s', self.plugin_id)

    def on_countdown_created(self, countdown):
        if 'on_countdown_created' in dir(self.module):
            self.module.on_countdown_created(self.app, countdown)

    def on_countdown_removed(self, countdown):
        if 'on_countdown_removed' in dir(self.module):
            self.module.on_countdown_removed(self.app, countdown)

    def on_countdown_state_changed(self, countdown, enabled):
        if 'on_countdown_state_changed' in dir(self.module):
            self.module.on_countdown_state_changed(self.app, countdown, enabled)

    def on_app_quit(self):
        if 'on_app_quit' in dir(self.module):
            self.module.on_app_quit(self.app)


class PluginMgr:
    plugin_module_prefix = 'plugins.'

    @hook_target(path_root + 'PluginMgr.__init__')
    def __init__(self, app):
        self.app = app
        if not os.path.exists(properties.plugins_prefix):
            os.mkdir(properties.plugins_prefix)
        sys.path.append(os.getcwd())

        self.plugin_metas = {}
        self.preloaded_plugins = []
        self.loading_tree = {}
        # Preloading plugins
        logging.info('Preloading plugins...')
        for i in os.listdir(properties.plugins_prefix):
            meta_path = properties.plugins_prefix + i + '/metadata.json'
            metadata = {}
            if not os.path.exists(meta_path):
                logging.error('Invalid plugin: %s', i)
                continue
            with open(meta_path, 'r') as meta:
                metadata = json.load(meta)
                self.plugin_metas[i] = metadata
                self.preloaded_plugins.append(metadata['id'])
                logging.info('Found plugin: %s', metadata['id'])
                self.loading_tree[metadata['id']] = {
                    'in': [], 'out': [], 'id': metadata['id'], 'path': i
                }

        # Check dependency and build dependency tree
        logging.info('Checking plugin dependency...')
        for i in self.plugin_metas:
            for k in self.plugin_metas[i]['depends']:
                plugin_id = self.plugin_metas[i]['id']
                if k not in self.preloaded_plugins:
                    logging.critical('Plugin %s dependency %s not met', plugin_id, k)
                    raise RuntimeError('Dependency error.')
                self.loading_tree[plugin_id]['in'].append(k)
                self.loading_tree[k]['out'].append(plugin_id)
        logging.info('No dependency errors found.')

        # Build loading order
        self.loading_order = []
        loading_queue = []
        loading_tree = copy.deepcopy(self.loading_tree)
        for i in self.loading_tree:
            if len(loading_tree[i]['in']) == 0:
                loading_queue.append(i)
        while len(loading_queue):
            req_remove = []
            req_add = []
            for i in loading_queue:
                root = loading_tree[i]
                if len(root['in']) == 0:
                    # All depends loaded
                    self.loading_order.append(i)
                    req_remove.append(i)
                    for k in root['out']:
                        req_add.append(k)
                        loading_tree[k]['in'].remove(i)
            for i in req_add:
                loading_queue.append(i)
            for i in req_remove:
                loading_queue.remove(i)

        # Full loading plugins
        if self.app.arg.no_plugins:
            self.plugins = []
            return
        self.plugins = [Plugin(self.app, 'data')]
        status = 10
        if (len(os.listdir(properties.plugins_prefix)) - 1) > 0:
            step = 20 / (len(os.listdir(properties.plugins_prefix)) - 1)
        else:
            step = 20
        for i in os.listdir(properties.plugins_prefix):
            status += step
            self.app.splash.update_status(status, '正在初始化插件：{}'.format(i))
            if os.path.isdir(properties.plugins_prefix + i):
                self.plugins.append(Plugin(self.app, self.plugin_module_prefix + i))
            else:
                logging.info('skipped invalid plugin: %s', i)

        for i in self.plugins:
            i.load_plugin()

    @hook_target(path_root + 'PluginMgr.load_v2')
    def load_v2(self):
        status = 85
        if len(self.plugins) == 0:
            return
        step = 15 / len(self.plugins)
        for i in self.plugins:
            self.app.splash.update_status(status, '正在第二阶段加载插件：{}'.format(i.plugin_id))
            i.load_v2()
            status += step

    def on_countdown_created(self, countdown):
        for i in self.plugins:
            i.on_countdown_created(countdown)

    def on_countdown_removed(self, countdown):
        for i in self.plugins:
            i.on_countdown_removed(countdown)

    def on_countdown_state_changed(self, countdown, enabled):
        for i in self.plugins:
            i.on_countdown_state_changed(countdown, enabled)

    def on_app_quit(self):
        for i in self.plugins:
            i.on_app_quit()


class ConfigureView(ABC):
    # 组件id
    view_id = ''

    # 组件名称
    view_name = ''

    # 是否存储数据。默认为True
    can_store = True

    # 是否由universe_configure放置组件。如果为否，那么需要组件自己进行放置。默认为True
    auto_construct = True

    @abstractmethod
    def __init__(self, config, container):
        """
        初始化
        """
        pass

    @abstractmethod
    def generate_widget(self):
        """
        构造组件

        :return: 如果auto_construct为True，那么需要返回一个组件或一个包含一对组件的元组
        """
        pass

    @abstractmethod
    def load_val(self, value):
        """
        将数据加载到组件中

        :param value: 值
        """
        pass

    @abstractmethod
    def save_val(self):
        """
        返回组件中的数值

        :return: 数值
        """
        pass
