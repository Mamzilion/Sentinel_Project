# main.py - Version Windows complète
import asyncio
import threading
import sys
import os
from network import activer_isolation, desactiver_isolation
from process_guard import surveiller_processus
from usb_guard import surveiller_usb
from focus_guard import surveiller_focus
from ws_client import connecter

TOKEN_JWT = "TOKEN_RECU_APRES_AUTH"

def demarrer_surveillance():
    """Lance tous les threads de surveillance"""
    
    def callback_alerte(data):
        print(f" ALERTE : {data}")
    
    # Thread 1 : Processus
    t1 = threading.Thread(target=surveiller_processus, daemon=True)
    t1.start()
    print(" Surveillance processus démarrée")
    
    # Thread 2 : USB
    t2 = threading.Thread(target=surveiller_usb, args=(callback_alerte,), daemon=True)
    t2.start()
    print(" Surveillance USB démarrée")
    
    # Thread 3 : Focus (mode kiosque)
    t3 = threading.Thread(target=surveiller_focus, args=(callback_alerte,), daemon=True)
    t3.start()
    print(" Mode kiosque (focus) démarré")

def nettoyer():
    """Nettoie avant de quitter"""
    print("\n Arrêt de l'agent Sentinel...")
    desactiver_isolation()
    print(" Agent arrêté")

if __name__ == "__main__":
    print("=" * 50)
    print(" AGENT SENTINEL - Version Windows")
    print("=" * 50)
    
    from config import DOSSIER_TRAVAIL
    os.makedirs(DOSSIER_TRAVAIL, exist_ok=True)
    
    try:
        print("\n Activation isolation réseau...")
        activer_isolation()
        
        print("\n Lancement surveillances...")
        demarrer_surveillance()
        
        print("\n Connexion au serveur...")
        asyncio.run(connecter(TOKEN_JWT))
        
    except KeyboardInterrupt:
        print("\n\n Interruption utilisateur")
    finally:
        nettoyer()
