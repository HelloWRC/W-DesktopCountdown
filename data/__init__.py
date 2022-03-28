import data.effects
import data.actions
import data.triggers

from PyQt5.QtWidgets import QAction


plugin_id = 'wdcd'
plugin_name = '内置'
plugin_website = 'https://github.com/HelloWRC/W-DesktopCountdown'
plugin_description = 'W-DesktopCountdown的内置数据'

provided_effects = (
    effects.SampleEffect,
    effects.AcrylicEffect,
    effects.RollingTexts,
    effects.BackgroundCharm,
    effects.CountdownCharm
)

provided_actions = (
    actions.SampleAction,
    actions.SampleAction2,
    actions.RunCommand,
    actions.PushCountdownBack,
    actions.HideCountdown,
    actions.ExitApp
)

provided_triggers = (
    triggers.SampleTrigger,
    triggers.AlwaysFalse,
    triggers.WhenCountdownEnd,
    triggers.WhenCountdownStart
)


def on_load(config, app):
    pass
