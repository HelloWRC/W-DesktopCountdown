import data.effects
import data.actions
import data.triggers
import data.configure_widgets as cw

from PyQt5.QtWidgets import QAction


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

provided_cfg_views = (
    cw.Label,
    cw.Line,
    cw.CheckBox,
    cw.SpinBox,
    cw.LineEdit,
    cw.ComboBox,
    cw.ColorPicker
)