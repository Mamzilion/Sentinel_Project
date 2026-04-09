# usb_guard.py - Version Windows
import subprocess
import time
import threading

def get_usb_drives():
    """Récupère la liste des lecteurs USB (type amovible)"""
    try:
        result = subprocess.run('wmic logicaldisk where drivetype=2 get deviceid', shell=True, capture_output=True, text=True)
        lignes = result.stdout.strip().split('\n')[1:]
        return [l.strip() for l in lignes if l.strip()]
    except Exception:
        return []

def eject_usb_drive(lettre):
    """Tente d'éjecter/démonter un lecteur USB"""
    try:
        subprocess.run(f'powershell -command "$drive = Get-WmiObject Win32_Volume -Filter \'DriveLetter = \\"{lettre}\\"\'; $drive.Dismount($true)"', shell=True, capture_output=True)
        print(f" Éjection de {lettre}")
    except Exception:
        pass

def surveiller_usb(callback_alerte):
    """Surveille les insertions USB et bloque"""
    print(" Surveillance USB démarrée...")
    lecteurs_connus = set(get_usb_drives())
    
    while True:
        try:
            lecteurs_actuels = set(get_usb_drives())
            nouveaux = lecteurs_actuels - lecteurs_connus
            for lecteur in nouveaux:
                print(f" USB détecté : {lecteur}")
                eject_usb_drive(lecteur)
                callback_alerte({"type": "USB_DETECTE", "device": lecteur, "timestamp": time.time()})
            lecteurs_connus = lecteurs_actuels
        except Exception as e:
            print(f"Erreur USB : {e}")
        time.sleep(2)

if __name__ == "__main__":
    def alerte_test(data):
        print(f" ALERTE : {data}")
    surveiller_usb(alerte_test)