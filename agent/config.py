# config.py
import os

SERVER_IP = "10.86.120.245"  # a remplacer par la vraie IP de la machine
SERVER_PORT = 3000
WS_URL = f"ws://{SERVER_IP}:{SERVER_PORT}"

# Processus autorisés pendant l'examen (noms Windows)
PROCESSUS_AUTORISES = [
    "python.exe", "code.exe", "chrome.exe", "firefox.exe",
    "msedge.exe", "cmd.exe", "powershell.exe", "explorer.exe",
    "taskmgr.exe", "winword.exe", "excel.exe", "notepad.exe"
]

# Dossier de travail de l'étudiant (Windows)
DOSSIER_TRAVAIL = os.path.expandvars(r"%USERPROFILE%\Documents\examen")

# Dossier temporaire pour les archives
TEMP_DIR = os.path.expandvars(r"%TEMP%\sentinel_agent")
os.makedirs(TEMP_DIR, exist_ok=True)

# Fichier de consentement webcam
CONSENTEMENT_FILE = os.path.expandvars(r"%USERPROFILE%\.sentinel_consentement")