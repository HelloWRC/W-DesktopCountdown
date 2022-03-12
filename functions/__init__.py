import properties
import platform

from .appearance import hexcnv

if 'Windows' in platform.system():
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize') as key:
        properties.ld_themes[2] = properties.ld_themes[1-winreg.QueryValueEx(key, 'AppsUseLightTheme')[0]]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\DWM') as key:
        properties.system_color = hexcnv(winreg.QueryValueEx(key, 'AccentColor')[0])
