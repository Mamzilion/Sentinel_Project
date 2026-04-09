# network.py - Isolation réseau TOTALE (sauf serveur)
import subprocess
import sys

SERVER_IP = "192.168.10.1"

def activer_isolation():
    """Bloque TOUT accès réseau sauf au serveur Sentinel"""
    if sys.platform != "win32":
        print(" Ce code est pour Windows")
        return False
    
    try:
        # Supprimer les anciennes règles
        subprocess.run(f'netsh advfirewall firewall delete rule name="SentinelBlockAll"', shell=True, capture_output=True)
        subprocess.run(f'netsh advfirewall firewall delete rule name="SentinelAllowServer"', shell=True, capture_output=True)
        
        # Autoriser UNIQUEMENT le serveur
        subprocess.run(f'netsh advfirewall firewall add rule name="SentinelAllowServer" dir=out remoteip={SERVER_IP} action=allow', shell=True, check=True)
        
        # Bloquer TOUT le reste (Internet, autres IP, etc.)
        subprocess.run(f'netsh advfirewall firewall add rule name="SentinelBlockAll" dir=out action=block', shell=True, check=True)
        
        print(f" Isolation réseau ACTIVÉE (seul {SERVER_IP} est accessible)")
        return True
    except Exception as e:
        print(f" Erreur isolation : {e}")
        return False

def desactiver_isolation():
    """Restaure l'accès réseau normal"""
    try:
        subprocess.run(f'netsh advfirewall firewall delete rule name="SentinelBlockAll"', shell=True, capture_output=True)
        subprocess.run(f'netsh advfirewall firewall delete rule name="SentinelAllowServer"', shell=True, capture_output=True)
        print(" Réseau RESTAURÉ")
        return True
    except Exception as e:
        print(f" Erreur restauration : {e}")
        return False