import tkinter as tk
from tkinter import messagebox, ttk
import requests
from config import *
import security_utils as sec_utils
from auth_manager import AuthManager
from exam_session import ExamSession
from guardian_system import SystemGuardian
from guardian_camera import CameraGuardian

class SentinelAgent:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=BG_COLOR)
        
        # Initialisation Système
        self.mac_address = sec_utils.get_mac_address()
        self.current_user = None
        self.examens_actifs = []
        
        # Gestionnaires de modules
        self.auth = AuthManager(self)
        self.system_guardian = None
        self.camera_guardian = None
        
        # Lancement de l'UI de connexion
        self.setup_login_ui()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- 1. AUTHENTIFICATION ---
    def setup_login_ui(self):
        self.clear_window()
        self.root.geometry("450x450")
        tk.Label(self.root, text="SENTINEL", font=("Helvetica", 24, "bold"), fg=HEADER_COLOR, bg=BG_COLOR).pack(pady=30)
        
        container = tk.Frame(self.root, bg=BG_COLOR)
        container.pack(pady=10)
        
        tk.Label(container, text="Matricule", bg=BG_COLOR).pack(anchor="w")
        self.entry_mat = tk.Entry(container, font=("Arial", 12), width=25)
        self.entry_mat.pack(pady=5)
        
        tk.Label(container, text="Mot de passe", bg=BG_COLOR).pack(anchor="w")
        self.entry_pass = tk.Entry(container, font=("Arial", 12), width=25, show="*")
        self.entry_pass.pack(pady=5)
        
        tk.Button(self.root, text="CONNEXION", bg=HEADER_COLOR, fg="white", width=20,
                  command=lambda: self.auth.login(self.entry_mat.get(), self.entry_pass.get(), self.mac_address)).pack(pady=20)

    # --- 2. CHANGEMENT DE MOT DE PASSE (CORRIGÉ) ---
    def setup_change_password_ui(self):
        self.clear_window()
        self.root.geometry("450x400")
        
        tk.Label(self.root, text="Nouveau mot de passe requis", 
                 font=("Arial", 12, "bold"), bg=BG_COLOR).pack(pady=30)
        
        tk.Label(self.root, text="Par mesure de sécurité, veuillez changer\nvotre mot de passe par défaut.", 
                 bg=BG_COLOR, fg="#7f8c8d").pack(pady=10)

        container = tk.Frame(self.root, bg=BG_COLOR)
        container.pack(pady=20)

        self.new_pass_entry = tk.Entry(container, font=("Arial", 12), width=25, show="*")
        self.new_pass_entry.pack()
        
        # Correction : On appelle handle_password_change au lieu de setup_dashboard_ui directement
        tk.Button(self.root, text="VALIDER LE CHANGEMENT", bg=HEADER_COLOR, fg="white",
                  command=self.handle_password_change).pack(pady=20)

    def handle_password_change(self):
        new_password = self.new_pass_entry.get().strip()
        
        if len(new_password) < 4:
            messagebox.showwarning("Sécurité", "Le mot de passe doit faire au moins 4 caractères.")
            return

        try:
            payload = {
                "matricule": self.current_user['matricule'],
                "newPassword": new_password
            }
            # Envoi réel au backend Lion Tech
            res = requests.post(f"{API_BASE_URL}/auth/change-password", json=payload, timeout=5)
            
            if res.status_code == 200:
                messagebox.showinfo("Succès", "Mot de passe mis à jour dans le système de l'IUT.")
                # Important : on met à jour l'état local pour valider la session actuelle
                self.current_user['isFirstLogin'] = False
                self.setup_dashboard_ui()
            else:
                messagebox.showerror("Erreur", res.json().get("message", "Échec de la mise à jour"))
                
        except Exception as e:
            messagebox.showerror("Erreur Réseau", f"Impossible de joindre le serveur : {e}")

    # --- 3. DASHBOARD ---
    def setup_dashboard_ui(self):
        self.clear_window()
        self.root.geometry(WINDOW_SIZE)
        
        header = tk.Frame(self.root, bg=HEADER_COLOR, height=80)
        header.pack(fill="x")
        tk.Label(header, text=f"Bienvenue, {self.current_user['nom']}", fg="white", bg=HEADER_COLOR, font=("Arial", 12)).pack(pady=20)
        
        tk.Label(self.root, text="Examens disponibles :", bg=BG_COLOR).pack(pady=10)
        self.combo_exam = ttk.Combobox(self.root, state="readonly", width=40)
        self.combo_exam.pack(pady=10)
        
        self.btn_launch = tk.Button(self.root, text="🚀 LANCER L'EXAMEN", bg=PRIMARY_BUTTON, fg="white", 
                                    font=("Arial", 12, "bold"), command=self.prepare_exam)
        self.btn_launch.pack(pady=20)
        
        self.fetch_exams()

    def fetch_exams(self):
        try:
            matricule = self.current_user['matricule']
            res = requests.get(f"{API_BASE_URL}/examen/liste-actifs/{matricule}", timeout=5)
            
            if res.status_code == 200:
                self.examens_actifs = res.json()
                options = [f"[{e.get('codeMatiere', '???')}] {e.get('titre', 'Sans titre')}" 
                           for e in self.examens_actifs]
                self.combo_exam['values'] = options
                
                if options:
                    self.combo_exam.current(0)
                    self.btn_launch.config(state="normal")
                else:
                    self.combo_exam.set("Aucun examen disponible pour vous")
                    self.btn_launch.config(state="disabled")
            else:
                self.combo_exam.set("Erreur lors de la récupération")
                self.btn_launch.config(state="disabled")
        except Exception as e:
            print(f"Erreur fetch_exams: {e}")
            self.combo_exam.set("Serveur injoignable")
            self.btn_launch.config(state="disabled")

    # --- 4. LOGIQUE D'EXAMEN ET SÉCURITÉ ---
    def prepare_exam(self):
        idx = self.combo_exam.current()
        if idx != -1:
            selected_exam = self.examens_actifs[idx]
            self.start_secured_session(selected_exam)

    def start_secured_session(self, exam_data):
        # Pour le test, on garde la fenêtre gérable
        # sec_utils.lock_linux_system()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        
        # Activation (commentée pour test initial)
        # self.system_guardian = SystemGuardian(self.root, self.report_fraud)
        # self.camera_guardian = CameraGuardian(self.current_user['matricule'], exam_data['_id'])
        # self.system_guardian.start()
        # self.camera_guardian.start_monitoring()
        
        self.session = ExamSession(self, exam_data)
        self.session.start()

    def report_fraud(self, fraud_type):
        if self.camera_guardian:
            self.camera_guardian.take_snapshot(f"ALERTE_{fraud_type}")
        print(f"FRAUDE DÉTECTÉE : {fraud_type}")

    def exit_exam_to_dashboard(self):
        if self.system_guardian: self.system_guardian.stop()
        if self.camera_guardian: self.camera_guardian.stop()
        
        sec_utils.unlock_linux_system()
        self.root.attributes("-fullscreen", False)
        self.root.attributes("-topmost", False)
        self.setup_dashboard_ui()

if __name__ == "__main__":
    root = tk.Tk()
    app = SentinelAgent(root)
    root.mainloop()