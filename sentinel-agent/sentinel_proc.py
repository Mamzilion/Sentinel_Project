import psutil

class SentinelProc:
    def __init__(self):
        # Liste des exécutables de navigateurs courants sous Windows
        self.forbidden_browsers = [
            "chrome.exe", "firefox.exe", "msedge.exe", 
            "opera.exe", "brave.exe", "iexplore.exe",
            "browser.exe", "whale.exe"
        ]

    def check_prohibited_processes(self):
        """Détecte si un navigateur est en cours d'exécution"""
        try:
            for proc in psutil.process_iter(['name']):
                # On compare en minuscule pour éviter les contournements simples
                proc_name = proc.info['name'].lower()
                if any(browser in proc_name for browser in self.forbidden_browsers):
                    return True, proc.info['name']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        return False, None

if __name__ == "__main__":
    print("[*] MODE WINDOWS - Surveillance des processus activée.")
    print("[*] Ouvrez un navigateur pour tester la détection...")
    detector = SentinelProc()
    try:
        import time
        while True:
            found, name = detector.check_prohibited_processes()
            if found:
                print(f"[ALERTE] Navigateur interdit détecté : {name}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[*] Arrêt du test Process.")