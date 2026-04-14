import uuid
import re
import os
import subprocess

def get_mac_address():
    mac_num = hex(uuid.getnode()).replace('0x', '').zfill(12)
    mac = ':'.join(re.findall('..', mac_num))
    return mac.lower()

def lock_linux_system():
    """Désactive les raccourcis GNOME pour empêcher la triche"""
    if os.name == 'posix': 
        try:
            subprocess.run(["gsettings", "set", "org.gnome.desktop.wm.keybindings", "switch-applications", "['']"])
            subprocess.run(["gsettings", "set", "org.gnome.mutter", "overlay-key", "''"])
        except: pass

def unlock_linux_system():
    """Réactive le système après l'examen"""
    if os.name == 'posix':
        try:
            subprocess.run(["gsettings", "set", "org.gnome.desktop.wm.keybindings", "switch-applications", "['<Alt>Tab']"])
            subprocess.run(["gsettings", "set", "org.gnome.mutter", "overlay-key", "'Super_L'"])
        except: pass