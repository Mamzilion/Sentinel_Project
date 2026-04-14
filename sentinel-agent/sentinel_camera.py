import cv2
import os
import time
import sys

class SentinelCamera:
    def __init__(self, matricule="STUDENT"):
        self.matricule = matricule
        self.log_dir = "sentinel_logs/captures"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)

    def capture(self, event_name="MONITORING"):
        """Méthode robuste de capture instantanée"""
        # On tente d'ouvrir la caméra par défaut (index 0)
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print(f"[!] Erreur: Impossible d'accéder à la webcam pour {event_name}")
            return False

        # Petite pause pour laisser la caméra s'ajuster à la lumière
        time.sleep(0.5) 
        
        ret, frame = cap.read()
        if ret:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{self.log_dir}/{self.matricule}_{event_name}_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"[*] Snapshot enregistré : {filename}")
            success = True
        else:
            print(f"[!] Erreur de lecture du flux pour {event_name}")
            success = False

        cap.release()
        return success

if __name__ == "__main__":
    # Test unitaire : permet de vérifier si la caméra marche
    cam = SentinelCamera("TEST_USER")
    cam.capture("MANUAL_TEST")