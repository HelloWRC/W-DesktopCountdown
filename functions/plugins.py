import importlib
import sys

import UIFrames.universe_configure
import UIFrames.plugin_info
import properties
import os
import logging

import functions.base

effects = {}
actions = {}
triggers = {}
hooks = {}


class Plugin:
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

    def load_v2(self):
        if 'countdownmgr_toolbar_actions' in dir(self.module):
            self.app.profile_mgr_ui.ui.toolBar.addActions(self.module.countdownmgr_toolbar_actions)
            self.pm_actions = self.module.countdownmgr_toolbar_actions
        if 'app_menu_actions' in dir(self.module):
            self.app.tray.menu.addActions(self.module.app_menu_actions)
            self.tray_actions = self.module.app_menu_actions

        self.plugin_info_ui = UIFrames.plugin_info.PluginInfo(self)
        logging.info('completed v2 load for plugin %s', self.plugin_id)


class PluginMgr:
    plugin_module_prefix = 'plugins.'

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

    def load_v2(self):
        for i in self.plugins:
            i.load_v2()


class Hook:
    def __init__(self, target, hook_type, source, catch_return):
        self.target = target
        self.hook_type = hook_type
        self.source = source
        self.catch_return = catch_return


def hook(source, target: str, hook_type: int, catch_return: bool = False) -> Hook:
    """
    注入对应的模块，使在执行对应模块的前后执行特定的函数。详细请见插件开发文档。

    :param source: function 要注入的函数
    :param target: str 注入目标路径
    :param hook_type: int 注入方式（0：原函数之前执行，1：原函数之后执行，2：覆盖原函数）
    :param catch_return: bool 是否劫持原函数的返回值。如果劫持，原函数的返回值会以最后一个形参传入，并以注入的函数的返回值作为原函数的返回值
    :return: Hook 返回钩子
    """
    if target not in hooks:
        hooks[target] = {
            'before': [],
            'overwrite': None,
            'after': []
        }
    root = hooks[target]
    content = Hook(target, hook_type, source, catch_return)
    if hook_type == 0:
        root['before'].append(content)
    elif hook_type == 1:
        root['after'].append(content)
    elif hook_type == 2:
        if root['overwrite'] is not None:
            raise RuntimeError('不能对一个已经被覆写过的函数再次覆写。')
        root['overwrite'] = content
    else:
        raise ValueError('未知的注入方式。')
    return content


def unhook(content: Hook):
    """
    将钩子脱钩。

    :param content: Hook 钩子
    :return: None
    """
    try:
        root = hooks[content.target]
        if content.hook_type == 0:
            root['before'].remove(content)
        elif content.hook_type == 1:
            root['after'].remove(content)
        else:
            root['overwrite'] = None
    except ValueError:
        raise ValueError('钩子不存在或者已经脱钩。')


def hook_target(path):
    def wrapper(func):
        def run(*args, **kwargs):
            if path in hooks:
                last_return = None
                root = hooks[path]
                for i in root['before']:  # hooks before
                    if i.catch_return:
                        last_return = i.source(*args, **kwargs, last_return=last_return)
                    else:
                        i.source(*args, **kwargs)

                if root['overwrite'] is None:  # overwrite hook
                    last_return = func(*args, **kwargs)
                else:
                    if root['overwrite'].catch_return:
                        last_return = root['overwrite'].source(*args, **kwargs, last_return=last_return)
                    else:
                        root['overwrite'].source(*args, **kwargs)

                for i in root['after']:  # hooks after
                    if i.catch_return:
                        last_return = i.source(*args, **kwargs, last_return=last_return)
                    else:
                        i.source(*args, **kwargs)
                return last_return
            else:
                return func(*args, **kwargs)

        return run

    return wrapper
