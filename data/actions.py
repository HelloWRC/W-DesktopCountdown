class SampleTrigger:
    trigger_id = 'wdcd.sample_trigger'
    trigger_name = '测试触发器'
    default_config = {}

    def __init__(self, app, countdown, config):
        self.app = app
        self.countdown = countdown
        self.config = config

    def check(self):
        return True


class AlwaysFalse:
    trigger_id = 'wdcd.always_false'
    trigger_name = '总是返回否的触发器'
    default_config = {}

    def __init__(self, app, countdown, config):
        self.app = app
        self.countdown = countdown
        self.config = config

    def check(self):
        return False


class SampleAction:
    action_id = 'wdcd.sample_action'
    action_name = '测试动作'
    default_config = {
        'string': {
            'type': 'string',
            'name': '要打印的内容',
            'default': 'Hello!'
        }
    }

    def __init__(self, app, countdown, config):
        self.cfg = config

    def run(self):
        print(self.cfg['string'])


class SampleAction2:
    action_id = 'wdcd.sample_action2'
    action_name = '测试动作2号'
    default_config = {
        'string': {
            'type': 'string',
            'name': '要打印的内容',
            'default': 'Hello!'
        }
    }

    def __init__(self, app, countdown, config):
        self.cfg = config

    def run(self):
        print(self.cfg['string'])
