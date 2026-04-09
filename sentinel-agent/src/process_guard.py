# process_guard.py - Tue TOUT processus non autorisé
import psutil
import time
from config import PROCESSUS_AUTORISES

def surveiller_processus():
    """Tue immédiatement tout processus non autorisé"""
    print("🔫 Surveillance processus ACTIVE")
    mon_pid = psutil.Process().pid
    
    while True:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                nom = proc.info['name'].lower()
                pid = proc.info['pid']
                
                # Ne pas se tuer soi-même
                if pid == mon_pid:
                    continue
                
                # Vérifier si le processus est autorisé
                if nom not in [p.lower() for p in PROCESSUS_AUTORISES]:
                    proc.kill()
                    print(f" PROCESSUS TUÉ : {nom} (PID: {pid})")
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        time.sleep(1)  # Vérification toutes les secondes

if __name__ == "__main__":
    surveiller_processus()