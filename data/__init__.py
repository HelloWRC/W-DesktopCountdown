import data.effects
import data.actions

from PyQt5.QtWidgets import QAction

plugin_id = 'wdcd'
plugin_name = '内置'
plugin_website = 'https://github.com/HelloWRC/W-DesktopCountdown'
plugin_description = 'W-DesktopCountdown的内置数据'

provided_effects = (
    effects.SampleEffect,
    effects.AcrylicEffect,
    effects.RollingTexts
)

provided_actions = (
)

provided_triggers = (
)

countdownmgr_toolbar_actions = (
    QAction('test'),
)

def on_load(config, app):
    print('on load')