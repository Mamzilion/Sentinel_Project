import cv2
import requests
import threading
import time
from datetime import datetime
from config import API_BASE_URL

class CameraGuardian:
    def __init__(self, matricule, exam_id):
        self.matricule = matricule
        self.exam_id = exam_id
        self.is_running = False
        self.camera = None

    def start_monitoring(self):
        self.is_running = True
        thread = threading.Thread(target=self._capture_loop, daemon=True)
        thread.start()

    def _capture_loop(self):
        """Prend une photo de manière aléatoire ou régulière (ex: toutes les 3 min)"""
        self.camera = cv2.VideoCapture(0)
        
        while self.is_running:
            # Attendre 3 minutes entre chaque capture automatique
            time.sleep(180) 
            if not self.is_running: break
            
            self.take_snapshot("MONITORING_ROUTINE")

    def take_snapshot(self, reason):
        """Prend une photo et l'envoie immédiatement au serveur"""
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                _, img_encoded = cv2.imencode('.jpg', frame)
                files = {'image': ('capture.jpg', img_encoded.tobytes(), 'image/jpeg')}
                data = {
                    'matricule': self.matricule,
                    'examenId': self.exam_id,
                    'type': reason,
                    'timestamp': datetime.now().isoformat()
                }
                try:
                    requests.post(f"{API_BASE_URL}/examen/upload-evidence", 
                                  files=files, data=data, timeout=5)
                except:
                    print("📡 Erreur d'envoi de la preuve visuelle")

    def stop(self):
        self.is_running = False
        if self.camera:
            self.camera.release()