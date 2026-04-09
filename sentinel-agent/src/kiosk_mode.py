# kiosk_mode.py - Mode kiosque : plein écran forcé et bloqué
import subprocess
import time
import threading
import os
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

def forcer_plein_ecran():
    """Force la fenêtre active en plein écran (F11)"""
    time.sleep(2)
    try:
        # Envoyer F11
        user32.keybd_event(0x7A, 0, 0, 0)
        time.sleep(0.1)
        user32.keybd_event(0x7A, 0, 2, 0)
        print(" [KIOSQUE] Plein écran forcé")
    except Exception as e:
        print(f" Erreur plein écran : {e}")

def lancer_navigateur_kiosque(url):
    """Lance le navigateur en mode kiosque (plein écran verrouillé)"""
    
    # Options pour mode kiosque
    options = "--kiosk --no-first-run --disable-infobars --disable-session-crashed-bubble --disable-features=ChromeWhatsNewUI,TranslationUI,PasswordImport --disable-default-apps --disable-popup-blocking --disable-notifications --disable-extensions --no-default-browser-check --noerrdialogs"
    
    # Chemins des navigateurs
    navigateurs = [
        (r"C:\Program Files\Google\Chrome\Application\chrome.exe", options),
        (r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", options),
        (r"C:\Program Files\Microsoft\Edge\Application\msedge.exe", f"--kiosk --no-first-run"),
        (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", f"--kiosk --no-first-run"),
    ]
    
    for chemin, opt in navigateurs:
        if os.path.exists(chemin):
            try:
                subprocess.Popen([chemin, opt, url], shell=False)
                print(f" Navigateur lancé en mode kiosque")
                threading.Thread(target=forcer_plein_ecran, daemon=True).start()
                return True
            except Exception as e:
                print(f" Erreur : {e}")
    
    # Fallback
    try:
        subprocess.Popen([url], shell=True)
        threading.Thread(target=forcer_plein_ecran, daemon=True).start()
        print(" Navigateur par défaut (mode kiosque non garanti)")
        return True
    except Exception as e:
        print(f" Impossible de lancer le navigateur : {e}")
        return False

def surveiller_plein_ecran(callback_alerte):
    """Surveille et maintient le plein écran"""
    print(" [KIOSQUE] Surveillance plein écran ACTIVE")
    
    while True:
        try:
            hwnd = user32.GetForegroundWindow()
            
            # Vérifier si la fenêtre couvre tout l'écran
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            
            screen_w = user32.GetSystemMetrics(0)
            screen_h = user32.GetSystemMetrics(1)
            
            win_w = rect.right - rect.left
            win_h = rect.bottom - rect.top
            
            # Si pas en plein écran
            if win_w < screen_w - 10 or win_h < screen_h - 10:
                print(" [KIOSQUE] Sortie du plein écran détectée !")
                callback_alerte({
                    "type": "SORTIE_PLEIN_ECRAN",
                    "timestamp": time.time()
                })
                
                # Reforcer le plein écran
                user32.keybd_event(0x7A, 0, 0, 0)
                time.sleep(0.1)
                user32.keybd_event(0x7A, 0, 2, 0)
                print(" [KIOSQUE] Plein écran rétabli")
                
        except Exception:
            pass
        
        time.sleep(1)

if __name__ == "__main__":
    print("Test mode kiosque")
    lancer_navigateur_kiosque("https://www.google.com")
    
    def alerte(data):
        print(f" {data}")
    
    threading.Thread(target=surveiller_plein_ecran, args=(alerte,), daemon=True).start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nArrêt")