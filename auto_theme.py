import os
import json
import platform
import subprocess


def get_system_color_scheme():
    os_name = platform.system()
    if os_name in ['FreeBSD', 'OpenBSD', 'NetBSD', 'DragonFly']:
        output = subprocess.check_output(['sysctl', '-n', 'hw.cfb.mode'])
        if (output=='3'or'2'):
            scheme='Dark'
    
    elif os_name == 'Darwin':
        output = subprocess.check_output(['defaults', 'read', 'NSGlobalDomain', 'AppleAquaGraphite'])
        if(output=='1'):
            scheme='Dark'
    
    elif os_name == 'Linux':
        output = subprocess.check_output(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'])
        if ('dark'in output):
            scheme='Dark'
light_theme, dark_theme = kitty.conf.get('light_and_dark_mode_themes', '').split(',')
mutex = ipc.Mutex('kitty_theme_mutex')

def on_system_color_scheme_change(scheme):
    get_system_color_scheme()
    if scheme == 'Dark':
        theme = dark_theme
    else:
        theme = light_theme
    with mutex:
        try:
            output = kitten('themes', '--dump-theme', '--check-age=-1', theme)
            colors = json.loads(output)
        except Exception:
            output = kitten('themes', '--dump-theme', '--cache-age=0', theme)
            colors = json.loads(output)
    Boss.patch_colors(colors)
Boss.on_system_color_scheme_change = on_system_color_scheme_change