import logging

effects = {}


class SampleEffect:
    effect_id = 'wdcd.sample_effect'
    effect_friendly_name = '测试效果'
    effect_description = '这是一个用于测试的特效。'
    default_config = {
        'string': {
            'type': 'string',
            'name': '这是一个字符串',
            'default': '默认值',
            'description': '在这里输入一个字符串。',  # 可选
            'placeholder': '占位符'  # 可选
        },
        'int': {
            'type': 'int',
            'name': '这是一个整数',
            'default': 0,
            'min': 0,
            'max': 10,
            # 可选选项
            'description': '在这里输入一个整数',
            'step': 1,
            'prefix': '',
            'suffix': ''
        },
        'float': {
            'type': 'float',
            'name': '这是一个浮点数',
            'default': 11.4514,
            'min': 0,
            'max': 100,
            # 可选选项
            'description': '在这里输入一个浮点数',
            'step': 0.1,
            'prefix': '',
            'suffix': ''
        },
        'bool': {
            'type': 'bool',
            'name': '这是一个布尔值',
            'default': False,
            # 可选选项
            'description': '在这里输入一个浮点数'
        },
        'combo_box': {
            'type': 'combo_box',
            'name': '这是一个下拉框',
            'items': [
                'item1', 'item2', 'item3'
            ],
            'default': 0,  # 索引值
            # 可选选项
            'description': '在这里选择一个颜色'
        }
    }

    def __init__(self, app, countdown, config):
        logging.info('effect init')

    def set_enabled(self):
        logging.info('effect enabled')

    def update_config(self, config):
        logging.info('effect reload')

    def unload(self):
        logging.info('effect unload')


class SampleEffect2:
    effect_id = 'wdcd.sample_effect2'
    effect_friendly_name = '测试效果2'
    effect_description = '这是一个用于测试的特效。'
    default_config = {
    }

    def __init__(self, app, countdown, config):
        pass

    def set_enabled(self):
        pass

    def update_config(self, config):
        pass

    def unload(self):
        pass


def add_effect(effect):
    effects[effect.effect_id] = effect


for i in (SampleEffect, ):
    add_effect(i)
