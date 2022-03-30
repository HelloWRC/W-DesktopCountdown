import data.effects
import data.actions
import data.triggers

from PyQt5.QtWidgets import QAction


plugin_id = 'wdcd'
plugin_name = '内置'
plugin_website = ''
plugin_description = 'W-DesktopCountdown的内置数据'

provided_effects = (
    effects.AcrylicEffect,
    effects.RollingTexts,
    effects.BackgroundCharm,
    effects.CountdownCharm
)

provided_actions = (
    actions.RunCommand,
    actions.StartFile,
    actions.PushCountdownBack,
    actions.HideCountdown,
    actions.ExitApp,
    actions.PopMessageBox,
    actions.PopNotification
)

provided_triggers = (
    triggers.WhenCountdownEnd,
    triggers.WhenCountdownStart,
    triggers.WhenCountdownShow
)


def on_load(config, app):
    pass
