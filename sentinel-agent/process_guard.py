# process_guard.py
import psutil
import time
from config import PROCESSUS_AUTORISES

def surveiller_processus():
    """Tue tout processus non autorisé"""
    print("🔍 Surveillance des processus démarrée...")
    
    while True:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                nom = proc.info['name'].lower()
                if nom not in [p.lower() for p in PROCESSUS_AUTORISES]:
                    if proc.pid != psutil.Process().pid:
                        proc.kill()
                        print(f"⛔ Processus tué : {nom} (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        time.sleep(2)

if __name__ == "__main__":
    surveiller_processus()