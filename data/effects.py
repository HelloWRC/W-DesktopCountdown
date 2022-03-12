import logging
import blur_effects
import properties
from functions.plugins import add_effect


class SampleEffect:
    effect_id = 'wdcd.sample_effect'
    effect_friendly_name = '测试效果'
    effect_description = '这是一个用于测试的特效。'
    default_config = {
        'label': {
            'type': 'label',
            'text': '这是一个标签',
            # 可选
            'word_warp': False,
            'selectable': True
        },
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


class RollingTexts:
    effect_id = 'wdcd.rolling_texts'
    effect_friendly_name = '滚动标语'
    effect_description = '向倒计时页面添加自定义标语，可以从文件读取，随机展示。'
    default_config = {
        'filename': {
            'type': 'string',
            'name': '文件路径',
            'default': '',
            'description': '包含要显示的标语的文本文件，编码为UTF-8，一行一条。'
        },
        'format': {
            'type': 'string',
            'name': '标语格式',
            'default': '{}',
            'description': '标语格式，“{}”将被替换为要显示的标语，可以使用HTML。'
        }
    }

    def __init__(self, app, countdown, config):
        import UIFrames.countdown
        from PyQt5.QtWidgets import QLabel
        self.app = app
        self.countdown: UIFrames.countdown.CountdownWin = countdown
        self.config = config
        self.texts = []
        self.label = QLabel()
        self.countdown.ui.verticalLayout_2.addWidget(self.label)

    def set_enabled(self):
        self.label.show()
        self.update_config(self.config)

    def update_config(self, config):
        import random
        self.config = config
        try:
            with open(config['filename']) as texts:
                self.texts = texts.read().split('\n')
            self.label.setText(self.config['format'].format(random.choice(self.texts)))
        except Exception as exp:
            self.label.setText(self.config['format'].format('出现错误：{}'.format(exp)))

    def unload(self):
        self.label.setVisible(False)
        del self.label


class AcrylicEffect:
    effect_id = 'wdcd.acrylic'
    effect_friendly_name = '亚克力效果'
    effect_description = '将倒计时页面背景应用亚克力效果。需要Windows10以及更新版本的Windows。'
    default_config = {
        'description': {
            'type': 'label',
            'text': '本特效利用了dwm内置的api，由zhiyiyo提供的基于MIT协议开源代码调用。本特效仅能在Windows 10以及更新版本的Windows上工作。',
            'word_warp': True
        },
        'background_color_type': {
            'type': 'combo_box',
            'name': '背景色来源',
            'items': [
                '当前主题',
                '自定义'
            ],
            'default': 0,
            'description': '选择背景色的来源。'
        },
        'background_color': {
            'type': 'string',
            'name': '自定义背景色（RRGGBB）',
            'default': '000000',
            'description': '输入背景色色号，格式是RRGGBB。'
        },
        'transparent': {
            'type': 'int',
            'name': '不透明度',
            'default': 128,
            'min': 0,
            'max': 255,
            'description': '背景颜色不透明度，范围0-255。'
        }
    }
    light_bg = 'f5f5f5'
    dark_bg = '31363b'

    def __init__(self, app, countdown, config):
        import UIFrames.countdown
        import wcdapp
        self.app: wcdapp.WDesktopCD = app
        self.countdown: UIFrames.countdown.CountdownWin = countdown
        self.config = config
        self.bg_color = '00000000'
        self.raw_style = self.countdown.styleSheet()

    def set_enabled(self):
        self.load_config()
        # self.countdown.ui.window_bg.setAttribute(Qt.WA_paint, False)
        self.countdown.ui.window_bg.setStyleSheet('background:rgba(0,0,0,0)')
        self.countdown.setAutoFillBackground(True)
        blur_effects.WindowEffect().setAcrylicEffect(int(self.countdown.winId()), self.bg_color)
        self.countdown.show()

    def update_config(self, config):
        self.load_config(config)
        blur_effects.WindowEffect().setAcrylicEffect(int(self.countdown.winId()), self.bg_color)
        self.countdown.show()

    def unload(self):
        # self.countdown.setAttribute(Qt.WA_TranslucentBackground, False)
        self.countdown.setUpdatesEnabled(True)
        self.countdown.ui.window_bg.setStyleSheet(self.raw_style)
        blur_effects.WindowEffect().removeBackgroundEffect(int(self.countdown.winId()))
        self.countdown.show()

    def load_config(self, config=None):
        if config is None:
            config = self.config
        else:
            self.config = config

        if config['background_color_type'] == 0:
            if properties.ld_themes[self.app.app_cfg.cfg['appearance']['ld_style']] == 'light':
                self.bg_color = self.light_bg
            else:
                self.bg_color = self.dark_bg
        else:
            self.bg_color = self.config['background_color']
        self.bg_color += str(hex(self.config['transparent']))[2:]


for i in (SampleEffect, RollingTexts, AcrylicEffect):
    add_effect(i)
