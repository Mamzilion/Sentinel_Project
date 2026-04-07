import os
import psutil
import cv2
import requests
import time
import uuid
import keyboard
import atexit

# --- CONFIGURATION ---
SERVER_URL = "http://localhost:3000/api"
ID_ETUDIANT = "123456" # À dynamiser plus tard
ALLOWED_PROCESSES = ["python.exe", "code.exe", "explorer.exe", "sentinel-agent.exe"]

# --- FONCTIONS SYSTÈME ---

def get_mac_address():
    """Identifiant unique du poste pour le serveur"""
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                    for ele in range(0, 8*6, 8)][::-1])
    return mac

def lock_system():
    """Active le mode Kiosque avec une méthode compatible par touche"""
    # On bloque les composants des raccourcis pour plus de compatibilité
    keys_to_block = ['windows', 'left windows', 'right windows', 'tab', 'alt', 'f4', 'f11', 'f12']
    
    try:
        for key in keys_to_block:
            keyboard.block_key(key)
        print("🔒 Mode Kiosque Activé (Navigation système verrouillée)")
    except Exception as e:
        print(f"⚠️ Erreur lors du verrouillage : {e}")

def unlock_system():
    """Libère le système"""
    keyboard.unhook_all()
    print("🔓 Système déverrouillé.")

# Enregistrer la fonction de déblocage pour qu'elle s'exécute à la fermeture
atexit.register(unlock_system)

# --- SURVEILLANCE ---

def capture_webcam(incident_type):
    """Preuve visuelle instantanée"""
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        timestamp = int(time.time())
        filename = f"alert_{incident_type}_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"📸 Flash Webcam : Preuve enregistrée pour {incident_type}")
    cam.release()

def check_security_breaches():
    """Vérifie les processus et les ports USB"""
    
    # 1. Détection de processus interdits
    prohibited = ["chrome.exe", "firefox.exe", "msedge.exe", "vlc.exe", "discord.exe"]
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() in prohibited:
                print(f"⚠️ TRICHE : Logiciel interdit détecté -> {proc.info['name']}")
                capture_webcam("LOGICIEL_INTERDIT")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    # 2. Détection de clé USB
    for disk in psutil.disk_partitions():
        try:
            if 'removable' in disk.opts or 'usb' in disk.device.lower():
                print(f"⚠️ ALERTE : Périphérique USB détecté sur {disk.device}")
                capture_webcam("USB_DISPOSITIF")
        except Exception:
            continue

# --- POINT D'ENTRÉE ---

if __name__ == "__main__":
    print(f"🛡️ AGENT SENTINEL - IUT NGAOUNDÉRÉ")
    print(f"📍 Machine : {get_mac_address()}")
    
    lock_system()
    
    print("\n🚀 Surveillance en cours... Appuyez sur Ctrl+C pour arrêter le test.")
    
    try:
        while True:
            check_security_breaches()
            time.sleep(3) # Fréquence de scan
    except KeyboardInterrupt:
        print("\n🛑 Test interrompu par l'utilisateur.")
        # unlock_system() est appelé automatiquement par atexit via la lib