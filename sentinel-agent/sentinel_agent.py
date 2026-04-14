import tkinter as tk
from tkinter import messagebox, ttk
import requests
import uuid
import re
import os
import subprocess

# --- CONFIGURATION ---
API_BASE_URL = "http://localhost:3000/api"

class SentinelAgent:
    def __init__(self, root):
        self.root = root
        self.root.title("SENTINEL v2 - IUT Ngaoundéré")
        self.root.geometry("500x550")
        self.root.configure(bg="#f5f6fa")
        self.root.eval('tk::PlaceWindow . center')

        # Variables de session
        self.current_user = None
        self.mac_address = self.get_mac_address()
        self.examens_actifs = []
        
        # Variables d'examen et Timer
        self.current_exam_data = None
        self.current_question_index = 0
        self.responses = {} 
        self.time_left = 0  
        self.timer_label = None
        self.timer_loop = None

        self.setup_login_ui()

    def get_mac_address(self):
        mac_num = hex(uuid.getnode()).replace('0x', '').zfill(12)
        mac = ':'.join(re.findall('..', mac_num))
        return mac.lower()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- 1. INTERFACE DE CONNEXION ---
    def setup_login_ui(self):
        self.clear_window()
        self.root.geometry("450x450")
        tk.Label(self.root, text="SENTINEL", font=("Helvetica", 24, "bold"), fg="#2c3e50", bg="#f5f6fa").pack(pady=(30, 10))
        container = tk.Frame(self.root, bg="#f5f6fa")
        container.pack(pady=10)
        
        tk.Label(container, text="Matricule", bg="#f5f6fa", fg="#2c3e50").pack(anchor="w")
        self.entry_matricule = tk.Entry(container, font=("Helvetica", 12), width=25)
        self.entry_matricule.pack(pady=(0, 15))
        
        tk.Label(container, text="Mot de passe", bg="#f5f6fa", fg="#2c3e50").pack(anchor="w")
        self.entry_password = tk.Entry(container, font=("Helvetica", 12), width=25, show="*")
        self.entry_password.pack(pady=(0, 20))
        
        tk.Button(self.root, text="CONNEXION", command=self.handle_login, bg="#2c3e50", fg="white", font=("Helvetica", 10, "bold"), width=20, height=2).pack()
        tk.Label(self.root, text=f"Poste identifié : {self.mac_address}", font=("Courier", 8), fg="#bdc3c7", bg="#f5f6fa").pack(side="bottom", pady=10)

    def handle_login(self):
        matricule = self.entry_matricule.get().strip()
        password = self.entry_password.get().strip()
        try:
            payload = {"matricule": matricule, "password": password, "macAddress": self.mac_address}
            response = requests.post(f"{API_BASE_URL}/auth/login", json=payload)
            data = response.json()
            if response.status_code == 200:
                self.current_user = data['user']
                if self.current_user.get('isFirstLogin'):
                    self.setup_change_password_ui()
                else:
                    self.setup_dashboard_ui()
            else:
                messagebox.showerror("Accès refusé", data.get("message", "Identifiants invalides"))
        except Exception as e:
            messagebox.showerror("Erreur Serveur", "Impossible de joindre le serveur.")

    # --- 2. CHANGEMENT DE MOT DE PASSE (PREMIÈRE CONNEXION) ---
    def setup_change_password_ui(self):
        self.clear_window()
        self.root.geometry("450x400")
        
        tk.Label(self.root, text="Nouveau mot de passe requis", 
                 font=("Arial", 12, "bold"), bg="#f5f6fa", fg="#2c3e50").pack(pady=30)
        
        tk.Label(self.root, text="Par mesure de sécurité, veuillez changer\nvotre mot de passe par défaut.", 
                 bg="#f5f6fa", fg="#7f8c8d").pack(pady=10)

        container = tk.Frame(self.root, bg="#f5f6fa")
        container.pack(pady=20)

        self.new_pass_entry = tk.Entry(container, font=("Arial", 12), width=25, show="*")
        self.new_pass_entry.pack()
        
        tk.Button(self.root, text="VALIDER LE CHANGEMENT", bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                  command=self.handle_password_change, height=2, width=25).pack(pady=20)

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
            res = requests.post(f"{API_BASE_URL}/auth/change-password", json=payload, timeout=5)
            
            if res.status_code == 200:
                messagebox.showinfo("Succès", "Mot de passe mis à jour avec succès.")
                self.current_user['isFirstLogin'] = False
                self.setup_dashboard_ui()
            else:
                messagebox.showerror("Erreur", res.json().get("message", "Échec de la mise à jour"))
        except Exception as e:
            messagebox.showerror("Erreur Réseau", f"Impossible de joindre le serveur.")

    # --- 3. DASHBOARD ---
    def setup_dashboard_ui(self):
        self.clear_window()
        self.root.attributes("-fullscreen", False)
        self.root.state('normal')
        self.root.geometry("500x550")
        
        header = tk.Frame(self.root, bg="#2c3e50", height=80)
        header.pack(fill="x")
        tk.Label(header, text=f"Espace Étudiant : {self.current_user['nom']}", fg="white", bg="#2c3e50", font=("Arial", 12, "bold")).pack(pady=20)
        
        info_frame = tk.LabelFrame(self.root, text=" Session en cours ", bg="white", padx=20, pady=20)
        info_frame.pack(pady=20, padx=20, fill="x")
        tk.Label(info_frame, text=f"👤 Matricule : {self.current_user['matricule']}", bg="white").pack(anchor="w")
        tk.Label(info_frame, text=f"💻 Poste : {self.mac_address}", bg="white", fg="#27ae60").pack(anchor="w")
        
        tk.Label(self.root, text="Sélectionnez un examen :", bg="#f5f6fa").pack(pady=5)
        self.combo_exam = ttk.Combobox(self.root, state="readonly", width=40)
        self.combo_exam.pack(pady=10)
        
        self.btn_launch = tk.Button(self.root, text="🚀 LANCER L'EXAMEN", command=self.prepare_exam, bg="#3498db", fg="white", font=("Arial", 12, "bold"), state="disabled", width=25, height=2)
        self.btn_launch.pack(pady=20)
        self.fetch_examens_actifs()

    def fetch_examens_actifs(self):
        try:
            matricule = self.current_user['matricule']
            res = requests.get(f"{API_BASE_URL}/examen/liste-actifs/{matricule}")
            if res.status_code == 200:
                self.examens_actifs = res.json()
                options = [f"[{e.get('codeMatiere', '???')}] {e.get('titre', 'Sans titre')}" for e in self.examens_actifs]
                self.combo_exam['values'] = options
                if options:
                    self.btn_launch.config(state="normal")
                    self.combo_exam.current(0)
                else:
                    self.btn_launch.config(state="disabled")
                    self.combo_exam.set("Aucun examen disponible")
        except: pass

    def prepare_exam(self):
        idx = self.combo_exam.current()
        if idx != -1:
            selected_exam = self.examens_actifs[idx]
            if messagebox.askyesno("Sentinel", f"Lancer l'examen {selected_exam['codeMatiere']} ?"):
                self.start_locked_exam(selected_exam['_id'])

    # --- 4. MODE EXAMEN (LOCK, TIMER & QUESTIONS) ---
    def lock_linux_system(self):
        if os.name == 'posix': 
            try:
                subprocess.run(["gsettings", "set", "org.gnome.desktop.wm.keybindings", "switch-applications", "['']"])
                subprocess.run(["gsettings", "set", "org.gnome.mutter", "overlay-key", "''"])
            except: pass

    def unlock_linux_system(self):
        if os.name == 'posix':
            try:
                subprocess.run(["gsettings", "set", "org.gnome.desktop.wm.keybindings", "switch-applications", "['<Alt>Tab']"])
                subprocess.run(["gsettings", "set", "org.gnome.mutter", "overlay-key", "'Super_L'"])
            except: pass

    def start_locked_exam(self, exam_id):
        self.clear_window()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.lock_linux_system()
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        try:
            res = requests.get(f"{API_BASE_URL}/examen/{exam_id}")
            if res.status_code == 200:
                self.render_questions(res.json())
            else:
                messagebox.showerror("Erreur", "Impossible de charger le sujet.")
                self.exit_exam_debug()
        except: self.exit_exam_debug()

    def render_questions(self, exam_data):
        self.current_exam_data = exam_data
        self.current_question_index = 0
        self.responses = {} 
        duree = int(self.current_exam_data.get('duree', 60))
        self.time_left = duree * 60
        self.display_current_question()
        self.update_timer()

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            mins, secs = divmod(self.time_left, 60)
            if self.timer_label:
                self.timer_label.config(text=f"⏱ TEMPS RESTANT : {mins:02d}:{secs:02d}")
                if self.time_left < 300: self.timer_label.config(fg="#e74c3c")
            self.timer_loop = self.root.after(1000, self.update_timer)
        else:
            messagebox.showwarning("SENTINEL", "Temps écoulé ! Soumission automatique.")
            self.submit_final_exam(forced=True)

    def display_current_question(self):
        self.clear_window()
        timer_frame = tk.Frame(self.root, bg="#2c3e50")
        timer_frame.pack(fill="x")
        self.timer_label = tk.Label(timer_frame, text="", font=("Courier", 16, "bold"), bg="#2c3e50", fg="#f1c40f", pady=10)
        self.timer_label.pack()
        
        questions = self.current_exam_data.get('questions', [])
        if not questions:
            tk.Label(self.root, text="Aucune question disponible.", bg="#f5f6fa").pack(pady=50)
            tk.Button(self.root, text="RETOUR", command=self.exit_exam_debug).pack()
            return

        q = questions[self.current_question_index]
        tk.Label(self.root, text=f"EXAMEN : {self.current_exam_data['titre']}", font=("Arial", 14, "bold"), bg="#f5f6fa").pack(pady=10)
        tk.Label(self.root, text=f"Question {self.current_question_index + 1} / {len(questions)}", fg="#7f8c8d", bg="#f5f6fa").pack()
        tk.Label(self.root, text=q['enonce'], font=("Arial", 13), wraplength=700, bg="#f5f6fa").pack(pady=30)

        if q.get('type') == "QCM":
            for opt in q.get('options', []):
                tk.Button(self.root, text=opt, width=50, bg="#ecf0f1", font=("Arial", 11),
                          command=lambda o=opt: self.save_response(o, auto_next=True)).pack(pady=5)
        elif q.get('type') in ["REDACTION", "CODE"]:
            bg_c, fg_c = ("#2d3436", "#00ff00") if q.get('type') == "CODE" else ("white", "black")
            self.txt_answer = tk.Text(self.root, height=15, width=80, font=("Courier New", 11), bg=bg_c, fg=fg_c)
            self.txt_answer.pack(pady=10)
            q_id = q.get('_id', str(self.current_question_index))
            if q_id in self.responses: self.txt_answer.insert("1.0", self.responses[q_id])
            tk.Button(self.root, text="💾 ENREGISTRER", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"),
                      command=lambda: self.save_response(self.txt_answer.get("1.0", "end-1c"), auto_next=True)).pack(pady=5)

        nav_frame = tk.Frame(self.root, bg="#f5f6fa")
        nav_frame.pack(side="bottom", pady=50)
        if self.current_question_index > 0:
            tk.Button(nav_frame, text="⬅️ Précédente", width=15, command=self.prev_question).pack(side="left", padx=20)
        if self.current_question_index < len(questions) - 1:
            tk.Button(nav_frame, text="Suivante ➡️", width=15, command=self.next_question).pack(side="left", padx=20)
        else:
            tk.Button(nav_frame, text="✅ TERMINER", bg="#e67e22", fg="white", font=("Arial", 12, "bold"), command=self.submit_final_exam).pack(side="left", padx=20)

    def save_response(self, value, auto_next=False):
        q_id = self.current_exam_data['questions'][self.current_question_index].get('_id', str(self.current_question_index))
        self.responses[q_id] = value
        if auto_next and self.current_question_index < len(self.current_exam_data['questions']) - 1: self.next_question()

    def next_question(self):
        self.current_question_index += 1
        self.display_current_question()

    def prev_question(self):
        self.current_question_index -= 1
        self.display_current_question()

    def submit_final_exam(self, forced=False):
        if not forced and not messagebox.askyesno("Confirmation", "Remettre votre copie ?"): return
        try: self.root.after_cancel(self.timer_loop)
        except: pass
        try:
            payload = {"matricule": self.current_user['matricule'], "examenId": self.current_exam_data['_id'], 
                       "macAddress": self.mac_address, "responses": self.responses}
            res = requests.post(f"{API_BASE_URL}/examen/soumettre", json=payload)
            if res.status_code in [200, 201]:
                if not forced: messagebox.showinfo("Succès", "Copie transmise !")
                self.exit_exam_debug()
            else: messagebox.showerror("Erreur", "Échec de l'envoi.")
        except: messagebox.showerror("Erreur", "Connexion perdue.")

    def exit_exam_debug(self):
        self.unlock_linux_system()
        self.root.attributes("-topmost", False)
        self.root.attributes("-fullscreen", False)
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.setup_dashboard_ui()

if __name__ == "__main__":
    root = tk.Tk()
    app = SentinelAgent(root)
    root.mainloop()