import os
import psutil
import cv2
import requests
import time
import uuid

# Configuration
SERVER_URL = "http://localhost:3000/api"  # Adresse de ton serveur Node.js
ID_ETUDIANT = "123456" # À récupérer dynamiquement après login

def get_mac_address():
    """Récupère l'adresse MAC pour l'authentification forte"""
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                    for ele in range(0, 8*6, 8)][::-1])
    return mac

def capture_webcam(incident_type):
    """Prend une photo flash en cas d'alerte"""
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        filename = f"alert_{incident_type}_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        # Ici on ajoutera le code pour envoyer l'image au serveur
        print(f"📸 Flash Webcam déclenché : {incident_type}")
    cam.release()

def monitor_processes():
    """Surveille les logiciels interdits (ex: Chrome, Firefox hors examen)"""
    prohibited = ["chrome.exe", "firefox.exe", "msedge.exe", "vlc.exe"]
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() in prohibited:
            print(f"⚠️ Alerte : Processus interdit détecté -> {proc.info['name']}")
            capture_webcam("PROCESS_FORBIDDEN")
            # Optionnel : proc.kill() pour fermer le logiciel automatiquement

if __name__ == "__main__":
    print("🛡️ Agent Sentinel Activé...")
    print(f"📍 Adresse MAC détectée : {get_mac_address()}")
    
    try:
        while True:
            monitor_processes()
            time.sleep(5) # Vérification toutes les 5 secondes
    except KeyboardInterrupt:
        print("Arrêt de l'agent.")