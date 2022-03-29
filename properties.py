version = '0.4.5 alpha'
version_code = '0.4.5a'
log_styles = '[%(asctime)s] [%(threadName)s/%(module)s.%(funcName)s(%(lineno)s)/%(levelname)s] %(message)s'
datefmt = '%Y/%m/%d %H:%M:%S'
work_root = './'
profile_prefix = work_root + 'profiles/'
qss_prefix = work_root + 'qss-styles/'
plugins_prefix = work_root + 'plugins/'
cache_prefix = work_root + 'cache/'
default_profile_name = '@@_default_@@.json'

extra_ui_cfg = {'font_family': 'Microsoft YaHei UI',
}

icon_themes = {
    'Breeze': {
        'light': 'breeze-light',
        'dark': 'breeze-dark'
    }
}

default_colors = [
    'amber', 'blue', 'cyan', 'lightgreen', 'pink', 'purple', 'red', 'teal', 'yellow'
]

ld_themes = [
    'light', 'dark', 'light'  # system fallback value
]

system_color = '#FF5D99'

countdown_config_default = {
    'window': {
        'width': 300,
        'height': 100,
        'window_mode': 0,
        'pos_x': 0,
        'pos_y': 0,
        'show_title_bar': True,
        'no_background': False,
        'mouse_tran': False
    },
    'countdown': {
        'start': 0,
        'end': 0,
        'title': 'countdown'
    },
    'display': {
        'target_format': '%Y/%m/%d %H:%M:%S',
        'countdown_format': '%D天',
        'show_progress_bar': True,
        'reverse_progress_bar': False,
        'end_text': '计时结束',
        'start_text': '计时未开始'
    },
    'effects': {},
    'automate': [],
    'style': {
        'window_bg': {},
        'lb_event': {},
        'lb_targetddate': {},
        'lb_text1': {},
        'lb_text2': {},
        'lb_CountDown': {},
        'progressBar': {}
    },
    'style_enabled': {
        'window_bg': {},
        'lb_event': {},
        'lb_targetddate': {},
        'lb_text1': {},
        'lb_text2': {},
        'lb_CountDown': {},
        'progressBar': {}
    },
    'enabled': True,
    'automate_enabled': True,
    'trusted': True
}

default_widget_style = {
    'background-color': '#FFFFFF',
    'background-image': '',
    'background-repeat': 'no-repeat',
    'background-position': 'center center',
    'font': '',
    'color': '#FFFFFF',
    'border-radius': 0,
    'border-width': 0,
    'border-color': '#000000',
    'border-style': 'solid'
}

default_widget_enabled = {
    'background-color': False,
    'background-image': False,
    'background-repeat': True,
    'background-position': False,
    'font': False,
    'color': False,
    'border-radius': False,
    'border-width': False,
    'border-color': False,
    'border-style': False

}

countdown_widget_id = [
    'window_bg',
    'lb_event',
    'lb_targetddate',
    'lb_text1',
    'lb_text2',
    'lb_CountDown',
    'progressBar',
]

countdown_widget_name = [
    '倒计时背景', '文字：倒计时标题', '文字：结束日期', '文字：“距离”', '文字：“还有”', '倒计时文字', '进度条'
]

default_automate_section = {
    'name': '',
    'trigger_type': 0,
    'triggers': [],
    'actions': []
}

default_auto_value = {
    'id': '',
    'config': {}
}

default_config = {
    'basic': {
        'splash': False,
        'auto_start': False,
        'exp_flags': True
    },
    'appearance': {
        'language': 'zhs',
        'ld_style': 2,  # 0:亮色;1:暗色;2:跟随系统
        'app_style': 'Material',
        'color_theme': {
            'type': 1,  # 0：主题值;1：跟随系统;2：自定
            'theme': 0,
            'color': '#FF5D99'
        },
        'custom_font': 'Microsoft YaHei',
        'custom_dpi': {
            'enabled': False,
            'dpi': 1,
            'force_app_dpi': False
        }
    },
    'plugins': {

    }
}

exp_flags = True

LIGHT_THEME_TEMPLE = '''
<!--?xml version="1.0" encoding="UTF-8"?-->
<resources>
  <color name="primaryColor">{}</color>
  <color name="primaryLightColor">{}</color>
  <color name="secondaryColor">#f5f5f5</color>
  <color name="secondaryLightColor">#ffffff</color>
  <color name="secondaryDarkColor">#e6e6e6</color>
  <color name="primaryTextColor">#3c3c3c</color>
  <color name="secondaryTextColor">#555555</color>
</resources>
'''

DARK_THEME_TEMPLE = '''
<!--?xml version="1.0" encoding="UTF-8"?-->
<resources>
  <color name="primaryColor">{}</color>
  <color name="primaryLightColor">{}</color>
  <color name="secondaryColor">#232629</color>
  <color name="secondaryLightColor">#4f5b62</color>
  <color name="secondaryDarkColor">#31363b</color>
  <color name="primaryTextColor">#000000</color>
  <color name="secondaryTextColor">#ffffff</color>
</resources>
'''
