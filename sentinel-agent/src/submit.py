# submit.py
import tarfile
import hashlib
import os
import requests
from config import SERVER_IP, SERVER_PORT, DOSSIER_TRAVAIL, TEMP_DIR

def soumettre_travaux(token_jwt: str) -> dict:
    """Compresse, hache et envoie les travaux (FORCÉ)"""
    
    if not os.path.exists(DOSSIER_TRAVAIL):
        os.makedirs(DOSSIER_TRAVAIL, exist_ok=True)
    
    archive_path = os.path.join(TEMP_DIR, "travaux_examen.tar.gz")
    
    try:
        # Compression
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(DOSSIER_TRAVAIL, arcname="travaux")
        
        # Hash SHA-256
        sha256 = hashlib.sha256()
        with open(archive_path, "rb") as f:
            for bloc in iter(lambda: f.read(4096), b""):
                sha256.update(bloc)
        hash_value = sha256.hexdigest()
        print(f" Hash SHA-256 : {hash_value[:20]}...")
        
        # Envoi au serveur
        with open(archive_path, "rb") as f:
            response = requests.post(
                f"http://{SERVER_IP}:{SERVER_PORT}/api/submit",
                files={"archive": f},
                data={"hash_sha256": hash_value},
                headers={"Authorization": f"Bearer {token_jwt}"},
                timeout=30
            )
        
        if response.status_code == 200:
            print(" Travaux soumis avec succès")
            return {"ok": True, "hash": hash_value}
        return {"ok": False, "status": response.status_code}
        
    except Exception as e:
        print(f" Erreur soumission : {e}")
        return {"ok": False, "erreur": str(e)}
    finally:
        if os.path.exists(archive_path):
            os.remove(archive_path)