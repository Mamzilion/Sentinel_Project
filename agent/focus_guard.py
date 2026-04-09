# focus_guard.py - Surveillance du focus fenêtre (Windows) - CORRIGÉ
import time
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

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

def get_active_window_process():
    """Récupère le nom du processus de la fenêtre active"""
    try:
        hwnd = user32.GetForegroundWindow()
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        import psutil
        try:
            proc = psutil.Process(pid.value)
            return proc.name()
        except:
            return "inconnu"
    except Exception:
        return "inconnu"

def surveiller_focus(callback_alerte):
    """Surveille les changements de fenêtre active (mode kiosque)"""
    print(" Surveillance focus (mode kiosque) démarrée...")
    print("   Change de fenêtre pour voir la détection !")
    print("   Appuie sur Ctrl+C pour arrêter\n")
    
    fenetre_connue = None
    
    while True:
        try:
            fenetre_courante = get_active_window_title()
            
            # Première initialisation
            if fenetre_connue is None:
                fenetre_connue = fenetre_courante
                print(f"   Fenêtre initiale : {fenetre_courante[:50] if fenetre_courante else '(vide)'}")
            
            # Détection de changement (CORRIGÉ : à chaque fois)
            elif fenetre_courante and fenetre_courante != fenetre_connue:
                print(f"\n [ALERTE] Changement de fenêtre détecté !")
                print(f"   → Ancienne : {fenetre_connue[:50] if fenetre_connue else '(vide)'}")
                print(f"   → Nouvelle : {fenetre_courante[:50]}")
                
                callback_alerte({
                    "type": "CHANGEMENT_FOCUS",
                    "ancienne_fenetre": fenetre_connue,
                    "nouvelle_fenetre": fenetre_courante,
                    "processus": get_active_window_process(),
                    "timestamp": time.time()
                })
                
                # CORRECTION : Met à jour la fenêtre connue à chaque changement
                fenetre_connue = fenetre_courante
                
        except Exception as e:
            print(f"Erreur : {e}")
        
        time.sleep(1)  # Vérification toutes les secondes

if __name__ == "__main__":
    def alerte_test(data):
        print(f"    [CALLBACK] Changement détecté vers : {data['nouvelle_fenetre'][:40]}")
    
    try:
        surveiller_focus(alerte_test)
    except KeyboardInterrupt:
        print("\n\n Test du mode kiosque arrêté")