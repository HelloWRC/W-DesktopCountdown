import importlib
import properties
import os

effects = {}


def add_effect(effect):
    effects[effect.effect_id] = effect


class Plugin:
    def __init__(self, module_path):
        self.module_path = module_path
        self.module = None

    def load_plugin(self):
        self.module = importlib.import_module(self.module_path)


class PluginMgr:
    plugin_module_prefix = 'plugins.'
    def __init__(self):
        if not os.path.exists(properties.plugins_prefix):
            os.mkdir(properties.plugins_prefix)

        self.plugins = [Plugin('data')]
        for i in os.listdir(properties.plugins_prefix):
            self.plugins.append(Plugin(self.plugin_module_prefix + i))

        for i in self.plugins:
            i.load_plugin()
