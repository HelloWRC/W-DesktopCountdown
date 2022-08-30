import time


class WhenCountdownEnd:
    trigger_id = 'wdcd.countdown_end'
    trigger_name = '倒计时结束时'
    default_config = {
        'offset': {
            'view': 'wdcd.spin_box',
            'type': 'int',
            'name': '延后时间',
            'default': 0,
            'min': 0,
            'max': 2147483647,
            # 可选选项
            'description': '在倒计时结束后在触发事件前等待特定的时间',
            'step': 1,
            'prefix': '',
            'suffix': '秒'
        },
        'delay': {
            'view': 'wdcd.check_box',
            'type': 'bool',
            'name': '如果已经结束，依然触发',
            'default': False
        }
    }

    def __init__(self, api, countdown, config):
        import UIFrames.countdown
        self.api = api
        self.countdown: UIFrames.countdown.CountdownWin = countdown
        self.config = config
        if 'triggered' not in self.config:
            self.config['triggered'] = not self.config['delay']
        if not self.is_end():
            self.config['triggered'] = False

    def is_end(self):
        return time.time() >= self.countdown.cfg.cfg['countdown']['end'] + self.config['offset']

    def check(self):
        if not self.is_end():
            self.config['triggered'] = False
        if self.config['triggered']:
            return False
        if self.is_end():
            self.config['triggered'] = True
            return True
        return False


class WhenCountdownStart:
    trigger_id = 'wdcd.countdown_start'
    trigger_name = '倒计时开始时'
    default_config = {
        'offset': {
            'view': 'wdcd.spin_box',
            'type': 'int',
            'name': '提前时间',
            'default': 0,
            'min': 0,
            'max': 2147483647,
            # 可选选项
            'description': '在倒计时开始前指定时间触发事件',
            'step': 1,
            'prefix': '',
            'suffix': '秒'
        },
        'delay': {
            'view': 'wdcd.check_box',
            'name': '如果已经开始，依然触发',
            'default': False
        }
    }

    def __init__(self, api, countdown, config):
        import UIFrames.countdown
        self.api = api
        self.countdown: UIFrames.countdown.CountdownWin = countdown
        self.config = config
        if 'triggered' not in self.config:
            self.config['triggered'] = not self.config['delay']
        if not self.is_started():
            self.config['triggered'] = False

    def is_started(self):
        return time.time() >= self.countdown.cfg.cfg['countdown']['start'] - self.config['offset']

    def check(self):
        if not self.is_started():
            self.config['triggered'] = False
        if self.config['triggered']:
            return False
        if self.is_started():
            self.config['triggered'] = True
            return True
        return False


class WhenCountdownShow:
    trigger_id = 'wdcd.countdown_show'
    trigger_name = '倒计时显示时'
    default_config = {
    }

    def __init__(self, api, countdown, config):
        import UIFrames.countdown
        self.api = api
        self.countdown: UIFrames.countdown.CountdownWin = countdown
        self.config = config
        self.config['triggered'] = False

    def check(self):
        if self.config['triggered']:
            return False
        self.config['triggered'] = True
        return True
