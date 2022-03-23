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
    actions.SampleAction,
    actions.SampleAction2
)

provided_triggers = (
    actions.SampleTrigger,
    actions.AlwaysFalse
)


def on_load(config, app):
    pass
