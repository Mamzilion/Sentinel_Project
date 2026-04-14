import tkinter as tk
from tkinter import messagebox
import requests
from config import API_BASE_URL, BG_COLOR, HEADER_COLOR
from copy_manager import CopyManager

class ExamSession:
    def __init__(self, app, exam_data):
        self.app = app
        self.root = app.root
        self.exam_data = exam_data
        
        self.current_question_index = 0
        self.responses = {}
        
        # Initialisation du CopyManager pour la sécurité des données
        self.copy_manager = CopyManager(app.current_user['matricule'], exam_data['_id'])
        
        # Gestion du temps (minutes -> secondes)
        self.time_left = int(self.exam_data.get('duree', 60)) * 60
        self.timer_loop = None

    def start(self):
        """Lance l'interface d'examen et le timer"""
        self.root.update() # <--- CRITIQUE : Force Tkinter à calculer la taille réelle
        self.render_ui()
        self.update_timer()
        self.root.update() # <--- RE-FORCE après le rendu des widgets

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            mins, secs = divmod(self.time_left, 60)
            if hasattr(self, 'timer_label'):
                self.timer_label.config(text=f"⏱ TEMPS RESTANT : {mins:02d}:{secs:02d}")
                if self.time_left < 300: # Alerte visuelle 5 min
                    self.timer_label.config(fg="#e74c3c")
            self.timer_loop = self.root.after(1000, self.update_timer)
        else:
            messagebox.showwarning("SENTINEL", "Temps écoulé !")
            self.submit_exam(forced=True)

    def render_ui(self):
        self.app.clear_window()
        
        # Bandeau Header / Timer
        header = tk.Frame(self.root, bg=HEADER_COLOR)
        header.pack(fill="x")
        self.timer_label = tk.Label(header, text="", font=("Courier", 16, "bold"), 
                                    bg=HEADER_COLOR, fg="#f1c40f", pady=10)
        self.timer_label.pack()

        # Zone de contenu
        self.content_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.content_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.display_question()
        self.root.update_idletasks() # <--- Force le placement des widgets

    def display_question(self):
        # On vide la zone de contenu avant d'afficher la nouvelle question
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        questions = self.exam_data.get('questions', [])
        q = questions[self.current_question_index]

        tk.Label(self.content_frame, text=f"Question {self.current_question_index + 1} / {len(questions)}", 
                 font=("Arial", 10), bg=BG_COLOR, fg="#7f8c8d").pack()
        
        tk.Label(self.content_frame, text=q['enonce'], font=("Arial", 13, "bold"), 
                 wraplength=600, bg=BG_COLOR).pack(pady=20)

        # Rendu selon le type (QCM / REDACTION / CODE)
        if q.get('type') == "QCM":
            for opt in q.get('options', []):
                tk.Button(self.content_frame, text=opt, width=50, 
                          command=lambda o=opt: self.save_and_next(o)).pack(pady=5)
        
        elif q.get('type') in ["REDACTION", "CODE"]:
            text_area = tk.Text(self.content_frame, height=12, width=70)
            text_area.pack(pady=10)
            
            q_id = q.get('_id', str(self.current_question_index))
            if q_id in self.responses:
                text_area.insert("1.0", self.responses[q_id])
            
            tk.Button(self.content_frame, text="💾 SAUVEGARDER LA RÉPONSE", 
                      command=lambda: self.save_response(text_area.get("1.0", "end-1c"))).pack()

        # Navigation
        nav_frame = tk.Frame(self.content_frame, bg=BG_COLOR)
        nav_frame.pack(side="bottom", pady=20)
        
        if self.current_question_index > 0:
            tk.Button(nav_frame, text="⬅ Précédent", command=self.prev_question).pack(side="left", padx=10)
        
        if self.current_question_index < len(questions) - 1:
            tk.Button(nav_frame, text="Suivant ➡", command=self.next_question).pack(side="left", padx=10)
        else:
            tk.Button(nav_frame, text="✅ TERMINER", bg="#e67e22", fg="white", 
                      command=self.submit_exam).pack(side="left", padx=10)

    def save_response(self, value):
        questions = self.exam_data.get('questions', [])
        q_id = questions[self.current_question_index].get('_id', str(self.current_question_index))
        self.responses[q_id] = value
        # Backup local immédiat pour éviter toute perte à Ngaoundéré (coupures de courant)
        self.copy_manager.save_locally(self.responses)

    def save_and_next(self, value):
        self.save_response(value)
        self.next_question()

    def next_question(self):
        self.current_question_index += 1
        self.display_question()

    def prev_question(self):
        self.current_question_index -= 1
        self.display_question()

    def submit_exam(self, forced=False):
        if not forced and not messagebox.askyesno("SENTINEL", "Voulez-vous remettre votre copie ?"):
            return
        
        if self.timer_loop:
            self.root.after_cancel(self.timer_loop)
            
        success, message = self.copy_manager.submit_final(self.responses, self.app.mac_address)
        if success:
            messagebox.showinfo("Succès", message)
            self.app.exit_exam_to_dashboard()
        else:
            messagebox.showerror("Erreur", message)