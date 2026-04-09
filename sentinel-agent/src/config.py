# config.py
import os

# Serveur
SERVER_IP = "192.168.10.1"
SERVER_PORT = 3000
WS_URL = f"ws://{SERVER_IP}:{SERVER_PORT}"

# URL de l'examen (serveur Sentinel)
URL_EXAMEN = f"http://{SERVER_IP}"

# Processus autorisés (seulement ce qui est nécessaire)
PROCESSUS_AUTORISES = [
    "python.exe",           # L'agent lui-même
    "chrome.exe",           # Chrome
    "msedge.exe",           # Edge
    "firefox.exe"           # Firefox
]

# Dossiers
DOSSIER_TRAVAIL = os.path.expandvars(r"%USERPROFILE%\Documents\examen")
TEMP_DIR = os.path.expandvars(r"%TEMP%\sentinel_agent")
os.makedirs(TEMP_DIR, exist_ok=True)