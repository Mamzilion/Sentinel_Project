# network.py - Version Windows avec netsh advfirewall
import subprocess
import sys

SERVER_IP = "192.168.10.1"

def activer_isolation():
    """Bloque tout sauf le serveur Sentinel (Windows Firewall)"""
    if sys.platform != "win32":
        print(" Ce code est pour Windows uniquement")
        return False
    
    try:
        # Supprimer les règles existantes
        subprocess.run(f'netsh advfirewall firewall delete rule name="SentinelBlockAll"', shell=True, capture_output=True)
        subprocess.run(f'netsh advfirewall firewall delete rule name="SentinelAllowServer"', shell=True, capture_output=True)
        
        # Autoriser uniquement le serveur Sentinel
        subprocess.run(f'netsh advfirewall firewall add rule name="SentinelAllowServer" dir=out remoteip={SERVER_IP} action=allow', shell=True, check=True)
        
        # Bloquer tout le reste
        subprocess.run(f'netsh advfirewall firewall add rule name="SentinelBlockAll" dir=out action=block', shell=True, check=True)
        
        print(f" Isolation réseau activée (seul {SERVER_IP} est autorisé)")
        return True
    except subprocess.CalledProcessError as e:
        print(f" Erreur isolation réseau : {e}")
        return False

def desactiver_isolation():
    """Restaure l'accès réseau normal"""
    if sys.platform != "win32":
        return False
    try:
        subprocess.run(f'netsh advfirewall firewall delete rule name="SentinelBlockAll"', shell=True, capture_output=True)
        subprocess.run(f'netsh advfirewall firewall delete rule name="SentinelAllowServer"', shell=True, capture_output=True)
        print(" Réseau restauré")
        return True
    except Exception as e:
        print(f" Erreur restauration : {e}")
        return False

def statut_isolation():
    """Vérifie si l'isolation est active"""
    result = subprocess.run(f'netsh advfirewall firewall show rule name="SentinelBlockAll"', shell=True, capture_output=True, text=True)
    return "SentinelBlockAll" in result.stdout