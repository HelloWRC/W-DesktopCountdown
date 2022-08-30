import copy
import time

from PyQt5.QtCore import QThread, QObject, QTimer
from PyQt5.QtGui import QColor
from PyQt5.Qt import pyqtSignal, QEvent

import logging

import UIFrames.countdown
import functions.plugins
import properties


class RollingTexts:
    effect_id = 'wdcd.rolling_texts'
    effect_friendly_name = '滚动标语'
    effect_description = '向倒计时页面添加自定义标语，可以从文件读取，随机展示。'
    default_config = {
        'label': {
            'view': 'wdcd.label',
            'text': '向倒计时页面添加自定义标语，可以从文件读取，随机展示。指向文本文件中每行包含一条标语，文件编码应为UTF-8。',
            'word_warp': True
        },
        'filename': {
            'view': 'wdcd.file_dialog',
            'name': '文件路径',
            'default': '',
            'sel_type': 0,
            'open_mode': 0,
            'file_types': '文本文档 (*.txt)',
            'description': '包含要显示的标语的文本文件，编码为UTF-8，一行一条。'
        },
        'format': {
            'view': 'wdcd.rich_edit',
            'name': '标语格式',
            'default': '{}',
            'formats': {
                '{}': '标语内容'
            },
            'description': '标语格式，“{}”将被替换为要显示的标语，可以使用HTML。'
        }
    }

    def __init__(self, api, countdown, config):
        import UIFrames.countdown
        from PyQt5.QtWidgets import QLabel
        self.api = api
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
            self.label.setText('<p style="color: red">出现错误：{}</p>'.format(exp))

    def unload(self):
        self.label.setVisible(False)
        del self.label


class AcrylicEffect:
    effect_id = 'wdcd.acrylic'
    effect_friendly_name = '亚克力效果'
    effect_description = '将倒计时页面背景应用亚克力效果。需要Windows10以及更新版本的Windows。'
    default_config = {
        'background_color_type': {
            'view': 'wdcd.combo_box',
            'name': '背景色来源',
            'items': [
                '当前主题',
                '自定义'
            ],
            'default': 0,
            'description': '选择背景色的来源。'
        },
        'background_color': {
            'view': 'wdcd.color_picker',
            'name': '自定义背景色',
            'default': '#000000',
            'description': '输入背景色色号'
        },
        'transparent': {
            'view': 'wdcd.spin_box',
            'type': 'int',
            'name': '不透明度',
            'default': 128,
            'min': 0,
            'max': 255,
            'description': '背景颜色不透明度，范围0-255。'
        },
        'disable_on_move': {
            'view': 'wdcd.check_box',
            'type': 'bool',
            'name': '移动时禁用',
            'default': True,
            'description': '窗体移动时禁用亚克力效果'
        }
    }
    light_bg = 'f5f5f5'
    dark_bg = '31363b'

    def __init__(self, api, countdown, config):
        import UIFrames.countdown
        import wcdapp
        self.api: functions.plugins.PluginAPI = api
        self.countdown: UIFrames.countdown.CountdownWin = countdown
        self.config = config
        self.bg_color = '00000000'
        self.raw_style = self.countdown.styleSheet()
        self.win_moving = False

    def set_enabled(self):
        try:
            import blur_effects
        except:
            logging.error('Unable to import blur support.')
        self.load_config()
        # self.countdown.ui.window_bg.setAttribute(Qt.WA_paint, False)
        self.countdown.ui.window_bg.setStyleSheet('background:rgba(0,0,0,0)')
        self.countdown.setAutoFillBackground(True)
        try:
            blur_effects.WindowEffect().setAcrylicEffect(int(self.countdown.winId()), self.bg_color, True)
        except:
            logging.info('Unable to enable acrylic effect')
        self.countdown.show()

    def update_config(self, config):
        try:
            import blur_effects
        except:
            logging.error('Unable to import blur support.')
        self.load_config(config)
        try:
            blur_effects.WindowEffect().setAcrylicEffect(int(self.countdown.winId()), self.bg_color, True)
        except:
            logging.info('Unable to enable acrylic effect')
        self.countdown.show()

    def unload(self):
        try:
            import blur_effects
        except:
            logging.error('Unable to import blur support.')
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
            if properties.ld_themes[self.api.app.app_cfg.cfg['appearance']['ld_style']] == 'light':
                self.bg_color = self.light_bg
            else:
                self.bg_color = self.dark_bg
        else:
            self.bg_color = self.config['background_color'][1:]
        self.bg_color += str(hex(self.config['transparent']))[2:]

    def on_event(self, watched, event: QEvent):
        if self.config['disable_on_move']:
            if event.type() == QEvent.Move and self.countdown.drag_flag and not self.win_moving:
                self.unload()
                self.win_moving = True
            if (not self.countdown.drag_flag) and self.win_moving:
                self.set_enabled()
                self.win_moving = False


class CharmBase(QObject):
    sig_update = pyqtSignal()
    default_config = {
        'lb_description1': {
            'view': 'wdcd.label',
            'text': '调整渐变设置。'
        },
        'start_color': {
            'view': 'wdcd.color_picker',
            'name': '开始颜色',
            'default': '#000000',
            'description': '渐变开始时的颜色'
        },
        'end_color': {
            'view': 'wdcd.color_picker',
            'name': '结束颜色',
            'default': '#000000',
            'description': '渐变结束时的颜色'
        },
        'loop_type': {
            'view': 'wdcd.combo_box',
            'name': '循环类型',
            'items': [
                '反转',
                '从头开始'
            ],
            'default': 0,
            'description': '循环类型。'
        },
        'color_type': {
            'view': 'wdcd.combo_box',
            'name': '渐变类型',
            'items': [
                'RGB',
                'HSV'
            ],
            'default': 0,
            'description': '渐变时控制颜色的渐变模式'
        },
        'fps': {
            'view': 'wdcd.spin_box',
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
            'view': 'wdcd.spin_box',
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
            'view': 'wdcd.label',
            'text': '在HSV模式下，若开始和结束色调相同，会呈现出色调循环的效果。',
            'word_warp': True
        }
    }

    def __init__(self, api, countdown, config):
        super(CharmBase, self).__init__()
        self.api = api
        self.countdown: UIFrames.countdown.CountdownWin = countdown
        self.cfg = config
        self.start_time = 0
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.start_color = QColor(self.cfg['start_color']).getRgb()
        self.end_color = QColor(self.cfg['end_color']).getRgb()

    def set_enabled(self):
        self.update_config(self.cfg)
        self.start_time = time.time()
        self.update_timer.start()

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
        self.update_timer.setInterval(int(1 / self.cfg['fps'] * 1000))

    def unload(self):
        self.update_timer.stop()
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

    def __init__(self, api, countdown, config):
        super(BackgroundCharm, self).__init__(api, countdown, config)
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

    def __init__(self, api, countdown, config):
        super(CountdownCharm, self).__init__(api, countdown, config)
        self.countdown: UIFrames.countdown.CountdownWin = countdown

    def set_rgb_color(self, color):
        self.countdown.ui.lb_CountDown.setStyleSheet('color:rgb(' + '{}, {}, {}'.format(color[0], color[1], color[2]) + ')')

    def set_hsv_color(self, color):
        self.countdown.ui.lb_CountDown.setStyleSheet('color:hsv(' + '{}, {}, {}'.format(color[0], color[1], color[2]) + ')')

    def clear_color(self):
        self.countdown.ui.lb_CountDown.setStyleSheet('')
