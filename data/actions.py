import logging
import os

import UIFrames.countdown

from PyQt5.QtWidgets import QMessageBox

import wcdapp


class RunCommand:
    action_id = 'wdcd.run_command'
    action_name = '运行命令'
    action_description = '运行指定的命令。'
    default_config = {
        'command': {
            'view': 'wdcd.line_edit',
            'name': '命令行',
            'default': ''
        }
    }

    def __init__(self, app, countdown, config):
        self.cfg = config

    def run(self):
        os.system(self.cfg['command'])


class StartFile:
    action_id = 'wdcd.start_file'
    action_name = '打开文件'
    action_description = '打开指定的文件'
    default_config = {
        'path': {
            'view': 'wdcd.line_edit',
            'name': '文件路径',
            'default': '',
            'description': '要打开的文件路径'
        }
    }

    def __init__(self, app, countdown, config):
        self.cfg = config

    def run(self):
        try:
            os.startfile(self.cfg['path'])
        except Exception as exp:
            logging.error('Could not open file "%s": %s', self.cfg['path'], exp)


class PushCountdownBack:
    action_id = 'wdcd.push_countdown_back'
    action_name = '推后倒计时'
    action_descriprion = '将倒计时延后。'
    default_config = {
        'start_offset': {
            'view': 'wdcd.spin_box',
            'type': 'int',
            'name': '开始时间延后',
            'default': 0,
            'min': 0,
            'max': 2147483647,
            # 可选选项
            'description': '将开始时间延后',
            'step': 1,
            'prefix': '',
            'suffix': '秒'
        },
        'end_offset': {
            'view': 'wdcd.spin_box',
            'type': 'int',
            'name': '结束时间延后',
            'default': 0,
            'min': 0,
            'max': 2147483647,
            # 可选选项
            'description': '将结束时间延后',
            'step': 1,
            'prefix': '',
            'suffix': '秒'
        }
    }

    def __init__(self, app, countdown, config):
        self.cfg = config
        self.countdown = countdown

    def run(self):
        self.countdown.cfg.cfg['countdown']['start'] += self.cfg['start_offset']
        self.countdown.cfg.cfg['countdown']['end'] += self.cfg['end_offset']
        self.countdown.write_config()


class HideCountdown:
    action_id = 'wdcd.hide_countdown'
    action_name = '隐藏倒计时'
    action_descriprion = '将倒计时隐藏'
    default_config = {}

    def __init__(self, app, countdown, config):
        self.cfg = config
        self.countdown: UIFrames.countdown.CountdownWin = countdown

    def run(self):
        self.countdown.cfg.cfg['enabled'] = False
        self.countdown.set_countdown_enabled(False)
        self.countdown.write_config()


class ExitApp:
    action_id = 'wdcd.exit_app'
    action_name = '退出应用'
    action_descriprion = '退出W-DesktopCountdown'
    default_config = {}

    def __init__(self, app, countdown, config):
        self.cfg = config
        self.app = app

    def run(self):
        self.app.quit(0)


class PopMessageBox:
    action_id = 'wdcd.pop_msg_box'
    action_name = '弹出提示框'
    action_descriprion = '弹出一个自定义的提示框'
    default_config = {
        'msg_type': {
            'view': 'wdcd.combo_box',
            'name': '提示类型',
            'items': [
                '信息',
                '询问',
                '警告',
                '错误'
            ],
            'default': 0,
            'description': '弹出的提示框的类型'
        },
        'title': {
            'view': 'wdcd.line_edit',
            'name': '消息标题',
            'default': '',
            'description': '提示框标题栏内容'
        },
        'text': {
            'view': 'wdcd.line_edit',
            'name': '消息文本',
            'default': '',
            'description': '提示框要显示的文本'
        },
    }
    msg_box = [
        QMessageBox.information, QMessageBox.question, QMessageBox.warning, QMessageBox.critical
    ]

    def __init__(self, app, countdown, config):
        self.cfg = config
        self.app = app
        self.countdown = countdown

    def run(self):
        self.msg_box[self.cfg['msg_type']](self.countdown, self.cfg['title'], self.cfg['text'])


class PopNotification:
    action_id = 'wdcd.pop_notification'
    action_name = '弹出通知'
    action_descriprion = '弹出一个自定义的通知'
    default_config = {
        'title': {
            'view': 'wdcd.line_edit',
            'name': '通知标题',
            'default': '',
            'description': '通知标题'
        },
        'text': {
            'view': 'wdcd.line_edit',
            'name': '通知文本',
            'default': '',
            'description': '要显示的文本'
        },
    }

    def __init__(self, app, countdown, config):
        self.cfg = config
        self.app: wcdapp.WDesktopCD = app
        self.countdown = countdown

    def run(self):
        self.app.tray.showMessage(self.cfg['title'], self.cfg['text'])
