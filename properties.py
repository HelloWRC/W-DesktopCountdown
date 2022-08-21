version = '0.5.5 beta'
version_code = '0.5.5b'
version_id = 50500
app_uuid = '721A9FA1-351A-B68A-AE4B-52E9B9460144'

log_styles = '[%(asctime)s] [%(threadName)s/%(module)s.%(funcName)s(%(lineno)s)/%(levelname)s] %(message)s'
datefmt = '%Y/%m/%d %H:%M:%S'
work_root = './'
profile_prefix = work_root + 'profiles/'
qss_prefix = work_root + 'qss-styles/'
plugins_prefix = work_root + 'plugins/'
cache_prefix = work_root + 'cache/'
log_root = 'logs/'
update_prefix = cache_prefix + 'update/'

log_file_fmt = log_root + '%Y-%m-%d %H-%M-%S.log'
latest_log_file_fmt = log_root + 'latest.log'
debug_log_file_fmt = log_root + 'debug.log'
update_file = work_root + 'update.exe'
update_meta = update_prefix + 'meta.json'
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
        'mouse_tran': False,
        'skip_taskbar': True
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
    'border-width': 1,
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

update_meta_default = {
    'name': 'W-DesktopCountdown',
    'uuid': app_uuid,
    'last_updated': 0,
    'versions': {},
    'branches': {}
}

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
        # Generated from default_basic_config
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

    },
    'update': {
        'last_checked': 0,
        'status': 0,
        'download': {
            'source': '',
            'branch': '',
            'channel': ''
        },
        'auto_update': {
            'auto_check': True
        }
    }
}

default_basic_config = {
    'title_auto_align': {
        'type': 'label',
        'text': '<h2>对齐</h2><p>可以在移动倒计时时快速和其他窗口对齐</p>',
        'word_warp': True
    },
    'align_enabled': {
        'type': 'bool',
        'name': '启用对齐',
        'default': True
    },
    'align_offset': {
        'type': 'int',
        'name': '对齐误差范围',
        'default': 20,
        'min': 0,
        'max': 128,
        'description': '触发对齐的误差值。'
    },
    'line_1': {
        'type': 'line'
    },
    'title_advanced': {
        'type': 'label',
        'text': '<h2>杂项</h2>',
        'word_warp': True
    },
    'launch_on_start': {
        'type': 'bool',
        'name': '开机自启',
        'default': True,
        'description': '让应用在系统启动时自动启动'
    },
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

countdown_skipped = ['effects', 'automate']

update_source = 'https://gitee.com/userwrc/static_data/raw/master/app_services/update/W-DesktopCountdown/metadata.json'

update_status = [
    '当前状态不支持更新',
    '没有检查更新',
    '您已是最新',
    '发现新版本',
    '发现新版本，准备安装'
]

ucfg_test_temple = {
    'label': {
        'view': 'wdcd.label',
        'text': 'Hello world!'
    },
    'line': {
        'view': 'wdcd.line'
    },
    'checkbox': {
        'view': 'wdcd.check_box',
        'name': '这是一个复选框',
        'default': True,
        'description': '这是一个复选框'
    },
    'line_edit': {
        'view': 'wdcd.line_edit',
        'name': '这是一个单行文本框',
        'default': '欸嘿~',
        'placeholder': 'ehe',
        'description': '在这里随便输入点啥……'
    },
    'int': {
        'view': 'wdcd.spin_box',
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
        'view': 'wdcd.spin_box',
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
    'combo_box': {
        'view': 'wdcd.combo_box',
        'name': '这是一个下拉框',
        'items': [
            'venti', 'kazuha', 'xiao', 'heizou'
        ],
        'default': 0,  # 索引值
        # 可选选项
        'description': '在这里选择一个颜色'
    },
    'color1': {
        'view': 'wdcd.color_picker',
        'name': '这是一个颜色',
        'default': '#45b5a8',  # 索引值
        # 可选选项
        'description': '在这里选择一个颜色'
    },
    'color2': {
        'view': 'wdcd.color_picker',
        'name': '这是一个颜色',
        'default': '#c84232',  # 索引值
        # 可选选项
        'description': '在这里选择一个颜色'
    }
}

cob_people = [
    {
        'icon': ':/resources/img/contributors/HelloWRC.jpg',
        'title': 'HelloWRC',
        'content': '项目作者，目前主要开发者。',
        'links': [
            {
                'text': 'Github',
                'link': 'https://github.com/HelloWRC'
            }
        ]
    },
    {
        'icon': '',
        'title': '其他为此项目做出贡献的人员',
        'content': '包括但不限于提交、提出Issues、提交PR',
        'links': [
            {
                'text': '在Github上查看贡献列表',
                'link': 'https://github.com/HelloWRC/W-DesktopCountdown/graphs/contributors'
            }
        ]
    }
]

cob_projects = [
    {
        'icon': ':/resources/img/contributors/qt-material.png',
        'title': 'Qt Material',
        'content': '全局主题',
        'links': [
            {
                'text': 'Github仓库',
                'link': 'https://github.com/UN-GCPDS/qt-material'
            },
            {
                'text': '许可证：BSD-2-Clause License',
                'link': 'https://github.com/UN-GCPDS/qt-material/blob/master/LICENSE'
            },
            {
                'text': '作者：UN-GCPDS',
                'link': 'https://github.com/UN-GCPDS/qt-material'
            }
        ]
    },
    {
        'icon': ':/resources/img/contributors/kde.svg',
        'title': 'Breeze Icons',
        'content': '图标主题',
        'links': [
            {
                'text': 'kde.org',
                'link': 'https://kde.org'
            },
            {
                'text': 'Github仓库',
                'link': 'https://github.com/KDE/breeze-icons'
            },
            {
                'text': '许可证：GPLv2.1',
                'link': 'https://github.com/KDE/breeze-icons/blob/master/COPYING.LIB'
            },
            {
                'text': '作者：KDE',
                'link': 'https://github.com/KDE'
            }
        ]
    },
    {
        'icon': ':/resources/img/contributors/lib.svg',
        'title': 'Qt-Frameless-Window',
        'content': '从中提取了亚克力效果的部分',
        'links': [
            {
                'text': 'Github仓库',
                'link': 'https://github.com/zhiyiYo/PyQt-Frameless-Window'
            },
            {
                'text': '许可证：MIT License',
                'link': 'https://github.com/zhiyiYo/PyQt-Frameless-Window/blob/master/LICENSE'
            },
            {
                'text': '作者：之一',
                'link': 'https://github.com/zhiyiYo'
            }
        ]
    },
    {
        'icon': ':/resources/img/contributors/qt.png',
        'title': 'Qt & PyQt',
        'content': '本项目基于Qt框架和PyQt开发',
        'links': [
            {
                'text': 'qt.io',
                'link': 'https://www.qt.io'
            },
            {
                'text': '许可证：BSD-2-Clause License',
                'link': 'https://github.com/UN-GCPDS/qt-material/blob/master/LICENSE'
            }
        ]
    },
    {
        'icon': ':/resources/img/contributors/python.png',
        'title': 'Python',
        'content': '本项目由Python驱动',
        'links': [
            {
                'text': 'python.org',
                'link': 'https://python.org'
            }
        ]
    },
    {
        'icon': ':/resources/img/contributors/lib.svg',
        'title': '其余的一些依赖库',
        'content': 'pywin32 - 调用win32 api\nrequests - 文件下载\nzipfile - 解压文件\npyinstaller - 将Python包打包为可执行文件',
        'links': [
        ]
    }
]