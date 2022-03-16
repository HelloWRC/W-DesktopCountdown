import importlib
import sys

import UIFrames.universe_configure
import UIFrames.plugin_info
import properties
import os
import logging

import functions.base
from functions.hook import hook_target

path_root = 'functions.plugins.'

effects = {}
actions = {}
triggers = {}


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
        self.tray_actions = {}
        self.pm_actions = {}

    @hook_target(path_root + 'Plugin.load_plugin')
    def load_plugin(self):
        logging.info('loading plugin as py package: %s', self.module_path
                     )
        self.module = importlib.import_module(self.module_path)
        self.plugin_id = self.module.plugin_id
        self.plugin_name = self.module.plugin_name
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
                self.plugin_config_ui = UIFrames.universe_configure.UniverseConfigure(self.plugin_config,
                                                                                      self.plugin_default_cfg)
            else:
                self.plugin_config_ui = None

        if 'plugin_author' in dir(self.module):
            self.author = self.module.plugin_author
        if 'plugin_description' in dir(self.module):
            self.description = self.module.plugin_description
        if 'plugin_website' in dir(self.module):
            self.website = self.module.plugin_website

        if 'provided_effects' in dir(self.module):
            for effect in self.module.provided_effects:
                effects[effect.effect_id] = effect
                self.provided_effects[effect.effect_id] = effect
        if 'provided_actions' in dir(self.module):
            for action in self.module.provided_actions:
                actions[action.action_id] = action
                self.provided_actions[action.action_id] = action
        if 'provided_triggers' in dir(self.module):
            for trigger in self.module.provided_triggers:
                triggers[trigger.trigger_id] = trigger
                self.provided_triggers[trigger.trigger_id] = trigger

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


class PluginMgr:
    plugin_module_prefix = 'plugins.'

    @hook_target(path_root + 'PluginMgr.__init__')
    def __init__(self, app):
        self.app = app
        if not os.path.exists(properties.plugins_prefix):
            os.mkdir(properties.plugins_prefix)
        sys.path.append(os.getcwd())

        self.plugins = [Plugin(self.app, 'data')]
        for i in os.listdir(properties.plugins_prefix):
            if os.path.isdir(properties.plugins_prefix + i):
                self.plugins.append(Plugin(self.app, self.plugin_module_prefix + i))
            else:
                logging.info('skipped invalid plugin: %s', i)

        for i in self.plugins:
            i.load_plugin()

    @hook_target(path_root + 'PluginMgr.load_v2')
    def load_v2(self):
        for i in self.plugins:
            i.load_v2()

    def on_countdown_created(self, countdown):
        for i in self.plugins:
            i.on_countdown_created(countdown)

    def on_countdown_removed(self, countdown):
        for i in self.plugins:
            i.on_countdown_removed(countdown)

    def on_countdown_state_changed(self, countdown, enabled):
        for i in self.plugins:
            i.on_countdown_state_changed(countdown, enabled)
