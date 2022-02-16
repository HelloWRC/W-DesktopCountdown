version = '0.2.1 alpha'
log_styles = '[%(asctime)s] [%(threadName)s/%(module)s.%(funcName)s(%(lineno)s)/%(levelname)s] %(message)s'
datefmt = '%Y/%m/%d %H:%M:%S'
work_root = './'
profile_prefix = work_root + 'profiles/'
qss_prefix = work_root + 'qss-styles/'

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

default_config = {
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
    }
}

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
