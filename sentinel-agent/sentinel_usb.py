import subprocess
import os

class SentinelUSB:
    def __init__(self):
        # On mémorise les lettres de lecteurs présentes au lancement
        self.initial_devices = self._get_usb_list()

    def _get_usb_list(self):
        """Récupère la liste des lecteurs amovibles sous Windows"""
        try:
            # Type 2 = Removable, Type 3 = Local Disk
            # On récupère uniquement la lettre du lecteur (DeviceID)
            cmd = 'wmic logicaldisk where "drivetype=2" get deviceid'
            output = subprocess.check_output(cmd, shell=True).decode()
            
            # On nettoie la sortie pour avoir une liste de lettres (ex: ['E:', 'F:'])
            devices = [line.strip() for line in output.splitlines() if line.strip() and ":" in line]
            return set(devices)
        except Exception as e:
            print(f"[!] Erreur scan USB Windows: {e}")
            # Fallback simple si WMIC échoue : scanner les lettres de D à Z
            return self._fallback_scan()

    def _fallback_scan(self):
        """Méthode de secours si WMI est bloqué"""
        import string
        from ctypes import windll
        devices = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                # 2 = DRIVE_REMOVABLE
                if windll.kernel32.GetDriveTypeW(f"{letter}:\\") == 2:
                    devices.append(f"{letter}:")
            bitmask >>= 1
        return set(devices)

    def has_new_device(self):
        """Vérifie si une nouvelle lettre de lecteur est apparue"""
        current_devices = self._get_usb_list()
        new_devices = current_devices - self.initial_devices
        if new_devices:
            # On met à jour pour ne pas déclencher l'alerte en boucle
            # (ou on laisse l'orchestrateur gérer la logique de sanction)
            return True, list(new_devices)
        return False, []

if __name__ == "__main__":
    print("[*] MODE WINDOWS - Scan initial effectué.")
    print("[*] Insérez une clé USB pour tester...")
    detector = SentinelUSB()
    try:
        import time
        while True:
            detected, names = detector.has_new_device()
            if detected:
                print(f"[ALERTE] Nouvelle clé Windows détectée : {names}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[*] Arrêt du test USB.")