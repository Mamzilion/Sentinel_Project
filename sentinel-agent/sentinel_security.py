import os
import cv2
import psutil
import time
import subprocess

class SentinelSecurity:
    def __init__(self, matricule):
        self.matricule = matricule
        self.log_dir = "sentinel_logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def take_snapshot(self, event_name):
        """Prend une photo avec la webcam et l'enregistre"""
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"{self.log_dir}/{self.matricule}_{event_name}_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
            cap.release()

    def check_usb_devices(self):
        """Détecte si une nouvelle clé USB est insérée (Linux)"""
        try:
            # Vérifie les montages de disques amovibles
            output = subprocess.check_output("lsblk", shell=True).decode()
            if "removable" in output or "/media/" in output:
                return True
        except:
            pass
        return False

    def check_prohibited_processes(self):
        """Détecte les navigateurs ou moteurs de recherche ouverts"""
        forbidden = ["chrome", "firefox", "brave", "opera", "msedge", "chromium"]
        for proc in psutil.process_iter(['name']):
            try:
                if any(browser in proc.info['name'].lower() for browser in forbidden):
                    return proc.info['name']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None