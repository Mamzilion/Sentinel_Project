import json
import os
import requests
from tkinter import messagebox
from config import API_BASE_URL

class CopyManager:
    def __init__(self, matricule, examen_id):
        self.matricule = matricule
        self.examen_id = examen_id
        self.local_backup_path = f"backup_{matricule}_{examen_id}.json"

    def save_locally(self, responses):
        """Sauvegarde temporaire sur le disque en cas de crash"""
        try:
            with open(self.local_backup_path, 'w') as f:
                json.dump(responses, f)
        except Exception as e:
            print(f"Erreur backup local : {e}")

    def submit_final(self, responses, mac_address):
        """Envoi définitif au serveur"""
        payload = {
            "matricule": self.matricule,
            "examenId": self.examen_id,
            "macAddress": mac_address,
            "responses": responses 
        }
        
        try:
            res = requests.post(f"{API_BASE_URL}/examen/soumettre", json=payload, timeout=15)
            if res.status_code in [200, 201]:
                # Si succès, on supprime le backup local
                if os.path.exists(self.local_backup_path):
                    os.remove(self.local_backup_path)
                return True, "Copie transmise avec succès !"
            else:
                return False, f"Échec de l'envoi : {res.json().get('message')}"
        except Exception as e:
            return False, f"Erreur de connexion : {str(e)}"