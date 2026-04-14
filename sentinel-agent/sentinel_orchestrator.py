import threading
import time
import subprocess
import sys
from sentinel_security import SentinelSecurity
from tkinter import messagebox

class SentinelOrchestrator:
    def __init__(self, matricule="ETU_DEV"):
        self.security = SentinelSecurity(matricule)
        self.is_running = True

    def security_loop(self):
        """Boucle de surveillance en arrière-plan"""
        print("[SENTINEL] Surveillance active...")
        while self.is_running:
            # 1. Détection USB
            if self.security.check_usb_devices():
                print("[ALERTE] Clé USB détectée !")
                self.security.take_snapshot("USB_DETECTED")
            
            # 2. Détection Navigateur
            browser = self.security.check_prohibited_processes()
            if browser:
                print(f"[ALERTE] Navigateur détecté : {browser}")
                self.security.take_snapshot("BROWSER_OPENED")

            time.sleep(3) # Vérification toutes les 3 secondes pour ne pas surcharger le CPU

    def start(self):
        # 1. Snapshot de début
        self.security.take_snapshot("EXAM_START")
        
        # 2. Lancer la sécurité dans un thread séparé
        security_thread = threading.Thread(target=self.security_loop, daemon=True)
        security_thread.start()

        # 3. Lancer l'Agent Sentinel (le fichier unique)
        print("[SENTINEL] Lancement de l'Agent...")
        try:
            # On lance sentinel_agent.py comme un processus séparé
            process = subprocess.Popen([sys.executable, "sentinel_agent.py"])
            process.wait() # Attend la fin de l'examen
        except Exception as e:
            print(f"Erreur de lancement : {e}")
        finally:
            # 4. Snapshot de fin et fermeture
            self.is_running = False
            self.security.take_snapshot("EXAM_END")
            print("[SENTINEL] Session terminée.")

if __name__ == "__main__":
    # Dans la réalité, on récupère le matricule via un argument ou une config
    orchestrator = SentinelOrchestrator()
    orchestrator.start()