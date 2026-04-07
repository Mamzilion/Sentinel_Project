import os
import psutil
import cv2
import requests
import time
import uuid
import keyboard
import atexit
import hashlib
import zipfile

# --- CONFIGURATION ---
SERVER_URL = "http://localhost:3000/api"
ID_ETUDIANT = "123456"  # À dynamiser après le login
EXAM_DURATION_SEC = 60 * 60  # Durée : 1 heure
START_TIME = time.time()
SOURCE_DIR = "./mon_travail"  # Dossier à aspirer à la fin

# --- FONCTIONS SYSTÈME & SÉCURITÉ ---

def get_mac_address():
    """Identifiant unique du poste"""
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                    for ele in range(0, 8*6, 8)][::-1])
    return mac

def lock_system():
    """Mode Kiosque : Bloque la navigation OS"""
    keys_to_block = ['windows', 'left windows', 'right windows', 'tab', 'alt', 'f4', 'f11', 'f12']
    try:
        for key in keys_to_block:
            keyboard.block_key(key)
        print("🔒 Mode Kiosque Activé")
    except Exception as e:
        print(f"⚠️ Erreur verrouillage : {e}")

def unlock_system():
    """Libère le PC"""
    keyboard.unhook_all()
    print("🔓 Système déverrouillé.")

atexit.register(unlock_system)

# --- SURVEILLANCE & CAPTURE ---

def capture_webcam(incident_type):
    """Preuve photo en cas d'infraction"""
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        filename = f"alert_{incident_type}_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        print(f"📸 Preuve enregistrée : {incident_type}")
    cam.release()

def check_security_breaches():
    """Scan des ports USB et des processus"""
    prohibited = ["chrome.exe", "firefox.exe", "msedge.exe", "vlc.exe"]
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() in prohibited:
                print(f"⚠️ Logiciel interdit : {proc.info['name']}")
                capture_webcam("LOGICIEL_INTERDIT")
        except: continue

    for disk in psutil.disk_partitions():
        try:
            if 'removable' in disk.opts or 'usb' in disk.device.lower():
                print(f"⚠️ USB détecté sur {disk.device}")
                capture_webcam("USB_DISPOSITIF")
        except: continue

# --- GESTION DES COPIES (NOUVEAU) ---

def create_copy_archive(source_dir, output_zip):
    """Compresse le travail et génère le Hash SHA-256"""
    if not os.path.exists(source_dir):
        os.makedirs(source_dir) # Crée le dossier s'il n'existe pas pour le test
        
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                zipf.write(os.path.join(root, file), 
                           os.path.relpath(os.path.join(root, file), source_dir))
    
    with open(output_zip, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    return file_hash

def submit_exam(file_path, file_hash):
    """Envoi final au serveur Node.js"""
    print(f"📦 Tentative d'envoi de la copie... (Hash: {file_hash[:10]}...)")
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'studentId': ID_ETUDIANT, 'macAddress': get_mac_address(), 'hash': file_hash}
            response = requests.post(f"{SERVER_URL}/upload", files=files, data=data)
            if response.status_code == 200:
                print("✅ Copie transmise avec succès au serveur !")
                return True
    except Exception as e:
        print(f"❌ Erreur réseau : {e} (Copie sauvegardée localement)")
        return False

# --- BOUCLE PRINCIPALE ---

if __name__ == "__main__":
    print(f"🛡️ AGENT SENTINEL - IUT NGAOUNDÉRÉ")
    print(f"📍 MAC : {get_mac_address()}")
    
    lock_system()
    
    try:
        while True:
            # 1. Vérifier la sécurité
            check_security_breaches()
            
            # 2. Gérer le temps
            elapsed = time.time() - START_TIME
            remaining = EXAM_DURATION_SEC - elapsed
            
            if remaining <= 0:
                print("\n⏰ TEMPS ÉCOULÉ ! Récupération automatique...")
                h = create_copy_archive(SOURCE_DIR, "copie_finale.zip")
                submit_exam("copie_finale.zip", h)
                break
            
            if int(remaining) % 60 == 0: # Log chaque minute
                print(f"⏳ Temps restant : {int(remaining)//60} min")
                
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n🛑 Interruption manuelle.")