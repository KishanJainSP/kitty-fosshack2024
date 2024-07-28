import os
import json
import platform
import subprocess
import threading
import time
import fcntl
import kitty


config_dir = os.path.expanduser('~/.config/kitty')
light_theme_file = os.path.join(config_dir, 'light_theme.conf')
dark_theme_file = os.path.join(config_dir, 'dark_theme.conf')
lock_file_path = os.path.join(config_dir, 'theme_lock')



light_theme= """
# Light Theme Settings
background #ffffff
foreground #000000
cursor #000000
color0  #ffffff
color1  #ff5555
color2  #50fa7b
color3  #f1fa8c
color4  #bd93f9
color5  #ff79c6
color6  #8be9fd
color7  #000000
color8  #cccccc
color9  #ff6e6e
color10 #69ff94
color11 #ffffa5
color12 #d6acff
color13 #ff92d0
color14 #a4ffff
color15 #000000
"""




dark_theme= """
# Dark Theme Settings
background #1e1e1e
foreground #d4d4d4
cursor #d4d4d4
color0  #1e1e1e
color1  #ff5555
color2  #50fa7b
color3  #f1fa8c
color4  #bd93f9
color5  #ff79c6
color6  #8be9fd
color7  #f8f8f2
color8  #666666
color9  #ff6e6e
color10 #69ff94
color11 #ffffa5
color12 #d6acff
color13 #ff92d0
color14 #a4ffff
color15 #ffffff
"""



def create_theme_file(file_path, settings):
    os.makedirs(os.path.kitty(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(settings)
    
create_theme_file(light_theme_file, light_theme)
create_theme_file(dark_theme_file,dark_theme)



def get_system_color_scheme():
    os_name = platform.system()
    if os_name in ['FreeBSD', 'OpenBSD', 'NetBSD', 'DragonFly']:
        output = subprocess.check_output(['sysctl', '-n', 'hw.cfb.mode'])
        if (output=='3'or'2'):
            scheme='Dark'
        elif (output=='0'or'1'):
            scheme = 'Light' 
    
    elif os_name == 'Darwin':
        output = subprocess.check_output(['defaults', 'read', 'NSGlobalDomain', 'AppleAquaGraphite'])
        if(output=='1'):
            scheme='Dark'
        elif (output=='0'):
            scheme = 'Light'
    
    elif os_name == 'Linux':
        output = subprocess.check_output(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'])
        if ('dark'in output):
            scheme='Dark'
        else:
             scheme = 'Light'



def acquire_lock():
    os.makedirs(config_dir, exist_ok=True)
    
    lock_file = open(lock_file_path, 'w')
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_file
    except IOError:
        lock_file.close()
        exit(1)

def release_lock(lock_file):
    fcntl.flock(lock_file, fcntl.LOCK_UN)
    lock_file.close()

def apply_theme(theme_file):
    lock_file = acquire_lock()
    try:
        cmd = f"kitty @ set-colors --cache-age=0 {theme_file}"
        subprocess.run(cmd, shell=True, check=True)
    finally:
        release_lock(lock_file)


mutex = threading.Lock()

def apply_theme(theme_file):
    with mutex:
        time.sleep(2)

def main():

    light_theme_file = os.path.expanduser('~/.config/kitty/light_theme.conf')
    dark_theme_file = os.path.expanduser('~/.config/kitty/dark_theme.conf')
    def on_system_color_scheme_change(scheme):
        get_system_color_scheme()
        if scheme == 'Dark':
            theme=dark_theme
            thread1 = threading.Thread(target=apply_theme, args=(light_theme_file,))
            thread1.start()
            thread1.join()
    
        elif scheme == 'Light':
            theme=light_theme    
            thread2 = threading.Thread(target=apply_theme, args=(dark_theme_file,))
            thread2.start()
            thread2.join()
        try:
            output = kitty.kitten('themes', '--dump-theme', '--check-age=-1', theme)
            colors = json.loads(output)
        except Exception:
            output = kitty.kitten('themes', '--dump-theme', '--cache-age=0', theme)
            colors = json.loads(output)
        kitty.boss.patch_colors(colors)
    kitty.boss.on_system_color_scheme_change = on_system_color_scheme_change()
if __name__ == "__main__":



    main()

