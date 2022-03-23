class SampleTrigger:
    trigger_id = 'wdcd.sample_trigger'
    trigger_name = '测试触发器'
    trigger_config = {}

    def __init__(self, app, countdown, config):
        self.app = app
        self.countdown = countdown
        self.config = config

    def check(self):
        return True


class AlwaysFalse:
    trigger_id = 'wdcd.always_false'
    trigger_name = '总是返回否的触发器'
    trigger_config = {}

    def __init__(self, app, countdown, config):
        self.app = app
        self.countdown = countdown
        self.config = config

    def check(self):
        return False


class SampleAction:
    action_id = 'wdcd.sample_action'
    action_name = '测试动作'
    action_config = {}

    def __init__(self, app, countdown, config):
        pass

    def run(self):
        print('Hello!')
