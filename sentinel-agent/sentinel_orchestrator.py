import subprocess
import sys
import threading
import time
from sentinel_camera import SentinelCamera
from sentinel_usb import SentinelUSB
from sentinel_proc import SentinelProc

class SentinelOrchestrator:
    def __init__(self, matricule="LION_TECH_DEV"):
        self.cam = SentinelCamera(matricule)
        self.usb = SentinelUSB()
        self.proc = SentinelProc()
        self.running = True

    def monitor_security(self):
        """Boucle de surveillance multidimensionnelle"""
        print("[*] Cerveau de sécurité Sentinel actif...")
        
        while self.running:
            # 1. Check USB
            usb_detected, usb_names = self.usb.has_new_device()
            if usb_detected:
                print(f"[FRAUDE] USB branché : {usb_names}")
                self.cam.capture(f"FRAUDE_USB")

            # 2. Check Processus (Navigateurs)
            proc_detected, proc_name = self.proc.check_prohibited_processes()
            if proc_detected:
                print(f"[FRAUDE] Navigateur ouvert : {proc_name}")
                self.cam.capture(f"FRAUDE_PROC")

            time.sleep(3) # On ne sature pas le CPU

    def start(self):
        print("--- [SENTINEL SYSTEM WINDOWS - DEV BRANCH] ---")
        
        # Capture initiale
        self.cam.capture("EXAM_START")

        # Lancement de la surveillance threadée
        monitor_thread = threading.Thread(target=self.monitor_security, daemon=True)
        monitor_thread.start()

        try:
            # Lancement de l'agent graphique (ton fichier unique)
            print("[+] Lancement de Sentinel Agent...")
            subprocess.run([sys.executable, "sentinel_agent.py"], check=True)
        except Exception as e:
            print(f"[!] Erreur session : {e}")
        finally:
            self.running = False
            self.cam.capture("EXAM_END")
            print("--- [SESSION TERMINÉE] ---")

if __name__ == "__main__":
    # On peut passer le matricule via l'orchestrateur ici
    orchestrator = SentinelOrchestrator("DEV_STUDENT_001")
    orchestrator.start()