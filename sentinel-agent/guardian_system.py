import tkinter as tk
import threading
import time

class SystemGuardian:
    def __init__(self, root, on_fraud_detected):
        self.root = root
        self.on_fraud_detected = on_fraud_detected
        self.is_monitoring = False

    def start(self):
        """Active tous les verrous logiques"""
        self.is_monitoring = True
        self.start_clipboard_killer()
        # On lie l'événement de perte de focus de la fenêtre
        self.root.bind("<FocusOut>", self.handle_focus_loss)

    def start_clipboard_killer(self):
        """Vide le presse-papier en boucle dans un thread séparé"""
        def killer():
            # Nécessite sa propre instance pour le thread
            try:
                while self.is_monitoring:
                    self.root.clipboard_clear()
                    self.root.clipboard_append("SÉCURITÉ SENTINEL : Action interdite.")
                    time.sleep(1.5)
            except: pass
        
        thread = threading.Thread(target=killer, daemon=True)
        thread.start()

    def handle_focus_loss(self, event):
        """Déclenché si l'étudiant clique en dehors de la fenêtre"""
        if self.is_monitoring:
            print("⚠️ Tentative de sortie de la fenêtre détectée")
            self.on_fraud_detected("SORTIE_FENETRE")

    def stop(self):
        self.is_monitoring = False
        self.root.unbind("<FocusOut>")