import copy
import time

from PyQt5.QtCore import QThread, QObject
from PyQt5.QtGui import QColor
from PyQt5.Qt import pyqtSignal

import logging

import UIFrames.countdown
import blur_effects
import properties


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
        },
        'color1': {
            'type': 'color',
            'name': '这是一个颜色',
            'default': '#000000',  # 索引值
            # 可选选项
            'description': '在这里选择一个颜色'
        },
        'color2': {
            'type': 'color',
            'name': '这是一个颜色',
            'default': '#000000',  # 索引值
            # 可选选项
            'description': '在这里选择一个颜色'
        }
    }

    def __init__(self, app, countdown, config):
        logging.info('effect init')
        self.countdown: UIFrames.countdown.CountdownWin = countdown
        # self.hook = self.countdown.hook_mgr.hook(self.hint, 'show', 1)

    def set_enabled(self):
        logging.info('effect enabled')

    def update_config(self, config):
        logging.info('effect reload')

    def unload(self):
        logging.info('effect unload')
        # self.countdown.hook_mgr.unhook(self.hook)


class RollingTexts:
    effect_id = 'wdcd.rolling_texts'
    effect_friendly_name = '滚动标语'
    effect_description = '向倒计时页面添加自定义标语，可以从文件读取，随机展示。'
    default_config = {
        'label': {
            'type': 'label',
            'text': '向倒计时页面添加自定义标语，可以从文件读取，随机展示。指向文本文件中每行包含一条标语，文件编码应为UTF-8。',
            'word_warp': True
        },
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
            'type': 'color',
            'name': '自定义背景色',
            'default': '#000000',
            'description': '输入背景色色号'
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
            self.bg_color = self.config['background_color'][1:]
        self.bg_color += str(hex(self.config['transparent']))[2:]


class CharmUpdateThread(QThread):
    sig_stop = pyqtSignal()

    def __init__(self, charm):
        super(CharmUpdateThread, self).__init__()
        self.charm: CharmBase = charm
        self.sig_stop.connect(self.stop)
        self.stopped = False

    def run(self):
        while not self.stopped:
            sleep_gap = 1 / self.charm.cfg['fps'] * 1000
            self.charm.sig_update.emit()
            self.msleep(int(sleep_gap))

    def stop(self):
        self.stopped = True


class CharmBase(QObject):
    sig_update = pyqtSignal()
    default_config = {
        'lb_description1': {
            'type': 'label',
            'text': '调整渐变设置。'
        },
        'start_color': {
            'type': 'color',
            'name': '开始颜色',
            'default': '#000000',
            'description': '渐变开始时的颜色'
        },
        'end_color': {
            'type': 'color',
            'name': '结束颜色',
            'default': '#000000',
            'description': '渐变结束时的颜色'
        },
        'loop_type': {
            'type': 'combo_box',
            'name': '循环类型',
            'items': [
                '反转',
                '从头开始'
            ],
            'default': 0,
            'description': '循环类型。'
        },
        'color_type': {
            'type': 'combo_box',
            'name': '渐变类型',
            'items': [
                'RGB',
                'HSV'
            ],
            'default': 0,
            'description': '渐变时控制颜色的渐变模式'
        },
        'fps': {
            'type': 'int',
            'name': '刷新频率',
            'default': 30,
            'min': 1,
            'max': 200,
            # 可选选项
            'description': '动画的刷新频率。请谨慎调节，更高的频率可能会造成卡顿。',
            'step': 1,
            'prefix': '',
            'suffix': '次/秒'
        },
        'time': {
            'type': 'float',
            'name': '循环时长',
            'default': 5,
            'min': 0.1,
            'max': 360000,
            # 可选选项
            'description': '每次动画的循环时长',
            'step': 1,
            'prefix': '',
            'suffix': '秒'
        },
        'lb_description2': {
            'type': 'label',
            'text': '在HSV模式下，若开始和结束色调相同，会呈现出色调循环的效果。'
        }
    }

    def __init__(self, app, countdown, config):
        super(CharmBase, self).__init__()
        self.app = app
        self.countdown: UIFrames.countdown.CountdownWin = countdown
        self.cfg = config
        self.start_time = 0
        self.sig_update.connect(self.update)
        self.start_color = QColor(self.cfg['start_color']).getRgb()
        self.end_color = QColor(self.cfg['end_color']).getRgb()
        self.update_thread = CharmUpdateThread(self)

    def set_enabled(self):
        self.start_time = time.time()
        self.update_thread.start()

    def update_config(self, config):
        self.cfg = config
        if self.cfg['color_type'] == 0:
            self.start_color = QColor(self.cfg['start_color']).getRgb()
            self.end_color = QColor(self.cfg['end_color']).getRgb()
        else:
            self.start_color = QColor(self.cfg['start_color']).getHsv()
            self.end_color = QColor(self.cfg['end_color']).getHsv()
            if self.start_color == self.end_color:
                self.start_color = (0, self.start_color[1], self.start_color[2])
                self.end_color = (359, self.end_color[1], self.end_color[2])

    def unload(self):
        self.update_thread.stop()
        self.clear_color()

    def update(self):
        total_time = self.cfg['time']

        if time.time() - self.start_time > total_time:
            self.start_time = time.time()
            if self.cfg['loop_type'] == 0:
                temp = copy.deepcopy(self.start_color)
                self.start_color = copy.deepcopy(self.end_color)
                self.end_color = copy.deepcopy(temp)

        now_time: float = time.time() - self.start_time * 1.0
        process = now_time / total_time
        now_color = [0, 0, 0]

        for i in range(3):
            inter = self.end_color[i] - self.start_color[i]
            now_color[i] = self.start_color[i] + inter * process

        if self.cfg['color_type'] == 0:
            self.set_rgb_color(now_color)
        else:
            self.set_hsv_color(now_color)

    def set_rgb_color(self, color):
        pass

    def set_hsv_color(self, color):
        pass

    def clear_color(self):
        pass


class BackgroundCharm(CharmBase):
    effect_id = 'wdcd.background_charm'
    effect_friendly_name = '背景渐变'
    effect_description = '让背景颜色随时间渐变'

    def __init__(self, app, countdown, config):
        super(BackgroundCharm, self).__init__(app, countdown, config)
        self.countdown: UIFrames.countdown.CountdownWin = countdown

    def set_rgb_color(self, color):
        self.countdown.ui.window_bg.setStyleSheet('#window_bg{background-color:rgb(' + '{}, {}, {}'.format(color[0], color[1], color[2]) + ')}')

    def set_hsv_color(self, color):
        self.countdown.ui.window_bg.setStyleSheet('#window_bg{background-color:hsv(' + '{}, {}, {}'.format(color[0], color[1], color[2]) + ')}')

    def clear_color(self):
        self.countdown.ui.window_bg.setStyleSheet('')


class CountdownCharm(CharmBase):
    effect_id = 'wdcd.countdown_charm'
    effect_friendly_name = '倒计时渐变'
    effect_description = '让倒计时文字随时间渐变'

    def __init__(self, app, countdown, config):
        super(CountdownCharm, self).__init__(app, countdown, config)
        self.countdown: UIFrames.countdown.CountdownWin = countdown

    def set_rgb_color(self, color):
        self.countdown.ui.lb_CountDown.setStyleSheet('color:rgb(' + '{}, {}, {}'.format(color[0], color[1], color[2]) + ')')

    def set_hsv_color(self, color):
        self.countdown.ui.lb_CountDown.setStyleSheet('color:hsv(' + '{}, {}, {}'.format(color[0], color[1], color[2]) + ')')

    def clear_color(self):
        self.countdown.ui.lb_CountDown.setStyleSheet('')
