import importlib
import properties
import os
import logging

import functions.base

effects = {}
actions = {}
triggers = {}


class Plugin:
    def __init__(self, app, module_path):
        import wcdapp
        self.app: wcdapp.WDesktopCD = app
        self.module_path = module_path
        self.module = None
        self.plugin_config_ui = None
        self.plugin_default_cfg = {}
        self.plugin_config = {}

        self.plugin_id = ''
        self.plugin_name = ''
        self.description = ''
        self.author = ''
        self.website = ''
        self.plugin_actions = []

    def load_plugin(self):
        self.module = importlib.import_module(self.module_path)
        self.plugin_id = self.module.plugin_id
        self.plugin_name = self.module.plugin_name
        self.plugin_config = {}  # reversed
        if 'plugin_author' in dir(self.module):
            self.author = self.module.plugin_author
        if 'plugin_description' in dir(self.module):
            self.description = self.module.plugin_description
        if 'plugin_website' in dir(self.module):
            self.website = self.module.plugin_website

        if 'provided_effects' in dir(self.module):
            for effect in self.module.provided_effects:
                effects[effect.effect_id] = effect
        if 'provided_actions' in dir(self.module):
            for action in self.module.provided_actions:
                actions[action.action_id] = action
        if 'provided_triggers' in dir(self.module):
            for trigger in self.module.provided_triggers:
                triggers[trigger.trigger_id] = trigger

        self.module.on_load(self.plugin_config, self.app)

        logging.info('Loaded plugin: %s', self.plugin_id)

    def load_v2(self):
        if 'countdownmgr_toolbar_actions' in dir(self.module):
            self.app.profile_mgr_ui.ui.toolBar.addActions(self.module.countdownmgr_toolbar_actions)
        if 'app_menu_actions' in dir(self.module):
            self.app.tray.menu.addActions(self.module.app_menu_actions)

        logging.info('completed v2 load for plugin %s', self.plugin_id)

class PluginMgr:
    plugin_module_prefix = 'plugins.'

    def __init__(self, app):
        self.app = app
        if not os.path.exists(properties.plugins_prefix):
            os.mkdir(properties.plugins_prefix)

        self.plugins = [Plugin(self.app, 'data')]
        for i in os.listdir(properties.plugins_prefix):
            self.plugins.append(Plugin(self.app, self.plugin_module_prefix + i))

        for i in self.plugins:
            i.load_plugin()

    def load_v2(self):
        for i in self.plugins:
            i.load_v2()
