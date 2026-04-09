# focus_guard.py - Mode kiosque : détection et blocage
import time
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

# Liste des touches à bloquer (Alt+F4, Ctrl+W, etc.)
TOUCHES_BLOQUEES = [0x73, 0x57]  # F4, W

def get_active_window_title():
    """Récupère le titre de la fenêtre active"""
    try:
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
    except Exception:
        return ""

def surveiller_focus(callback_alerte):
    """Détecte et bloque les changements de fenêtre"""
    print(" Mode kiosque ACTIF")
    
    fenetre_connue = None
    
    while True:
        try:
            fenetre_courante = get_active_window_title()
            
            if fenetre_connue is None and fenetre_courante:
                fenetre_connue = fenetre_courante
                
            elif fenetre_courante and fenetre_courante != fenetre_connue:
                print(f" [KIOSQUE] Changement fenêtre : {fenetre_courante[:50]}")
                callback_alerte({
                    "type": "CHANGEMENT_FOCUS",
                    "fenetre": fenetre_courante,
                    "timestamp": time.time()
                })
                
                # Tenter de revenir à la fenêtre précédente
                try:
                    hwnd = user32.FindWindowW(None, fenetre_connue)
                    if hwnd:
                        user32.SetForegroundWindow(hwnd)
                except:
                    pass
                
                fenetre_connue = fenetre_courante
                
        except Exception:
            pass
        
        time.sleep(1)

if __name__ == "__main__":
    def alerte(data):
        print(f" ALERTE : {data}")
    surveiller_focus(alerte)