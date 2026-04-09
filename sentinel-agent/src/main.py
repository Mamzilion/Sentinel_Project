# main.py - Agent Sentinel complet avec mode kiosque
import asyncio
import threading
import sys
import os
from network import activer_isolation, desactiver_isolation
from process_guard import surveiller_processus
from usb_guard import surveiller_usb
from focus_guard import surveiller_focus
from kiosk_mode import lancer_navigateur_kiosque, surveiller_plein_ecran
from ws_client import connecter

TOKEN_JWT = "TOKEN_RECU_APRES_AUTH"

def demarrer_blocages():
    """Démarre TOUS les blocages"""
    
    def alerte(data):
        print(f" ALERTE SÉCURITÉ : {data}")
    
    # Blocage processus
    t1 = threading.Thread(target=surveiller_processus, daemon=True)
    t1.start()
    print(" Blocage processus ACTIF")
    
    # Blocage USB
    t2 = threading.Thread(target=surveiller_usb, args=(alerte,), daemon=True)
    t2.start()
    print(" Blocage USB ACTIF")
    
    # Mode kiosque (changement fenêtre)
    t3 = threading.Thread(target=surveiller_focus, args=(alerte,), daemon=True)
    t3.start()
    print(" Mode kiosque (focus) ACTIF")
    
    # Surveillance plein écran
    t4 = threading.Thread(target=surveiller_plein_ecran, args=(alerte,), daemon=True)
    t4.start()
    print(" Surveillance plein écran ACTIVE")

if __name__ == "__main__":
    print("=" * 60)
    print(" AGENT SENTINEL - VERROUILLAGE TOTAL")
    print("=" * 60)
    print(" Isolation réseau ACTIVÉE")
    print(" Blocage processus ACTIVÉ")
    print(" Blocage USB ACTIVÉ")
    print(" Mode kiosque ACTIVÉ")
    print(" Plein écran FORCÉ")
    print(" Webcam IMPOSÉE")
    print("=" * 60)
    
    # Création du dossier
    from config import DOSSIER_TRAVAIL, URL_EXAMEN
    os.makedirs(DOSSIER_TRAVAIL, exist_ok=True)
    
    try:
        # 1. Isolation réseau
        print("\n Activation isolation réseau...")
        activer_isolation()
        
        # 2. Lancement du navigateur en mode kiosque
        print("\n Lancement du navigateur en mode kiosque...")
        lancer_navigateur_kiosque(URL_EXAMEN)
        
        # 3. Tous les blocages
        print("\n Activation des blocages...")
        demarrer_blocages()
        
        # 4. Connexion au serveur
        print("\n🔌 Connexion au serveur Sentinel...")
        asyncio.run(connecter(TOKEN_JWT))
        
    except KeyboardInterrupt:
        print("\n\n Arrêt demandé")
    finally:
        desactiver_isolation()
        print(" Agent arrêté")