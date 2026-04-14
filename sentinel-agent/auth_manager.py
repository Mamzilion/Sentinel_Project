import requests
from tkinter import messagebox
import tkinter as tk
from config import API_BASE_URL

class AuthManager:
    def __init__(self, app):
        self.app = app # Référence à l'application principale (SentinelAgent)

    def login(self, matricule, password, mac_address):
        if not matricule or not password:
            messagebox.showwarning("Champs requis", "Veuillez remplir tous les champs.")
            return

        try:
            payload = {
                "matricule": matricule, 
                "password": password, 
                "macAddress": mac_address
            }
            response = requests.post(f"{API_BASE_URL}/auth/login", json=payload, timeout=10)
            data = response.json()

            if response.status_code == 200:
                self.app.current_user = data['user']
                if self.app.current_user.get('isFirstLogin'):
                    self.app.setup_change_password_ui()
                else:
                    self.app.setup_dashboard_ui()
            else:
                messagebox.showerror("Accès refusé", data.get("message", "Identifiants invalides"))
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Erreur Serveur", "Le serveur est injoignable. Vérifiez votre connexion à l'IUT.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")

    def update_password(self, new_password):
        # Logique pour changer le mot de passe au premier login
        # (À lier avec ton endpoint Node.js dédié)
        pass