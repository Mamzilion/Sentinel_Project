# ws_client.py - Version complète avec consentement webcam
import asyncio
import websockets
import json
import os
import sys
from webcam import capturer_webcam
from submit import soumettre_travaux
from config import WS_URL, CONSENTEMENT_FILE

token_jwt = None
consentement_webcam = False

def verifier_consentement():
    """Vérifie si l'étudiant a accepté la webcam"""
    global consentement_webcam
    
    try:
        if os.path.exists(CONSENTEMENT_FILE):
            with open(CONSENTEMENT_FILE, 'r') as f:
                contenu = f.read().strip()
                consentement_webcam = (contenu == "accepte")
        else:
            consentement_webcam = False
    except Exception as e:
        print(f" Erreur lecture consentement : {e}")
        consentement_webcam = False
    
    return consentement_webcam

def enregistrer_consentement(accepte):
    """Enregistre le consentement de l'étudiant"""
    global consentement_webcam
    consentement_webcam = accepte
    
    try:
        dossier = os.path.dirname(CONSENTEMENT_FILE)
        if dossier and not os.path.exists(dossier):
            os.makedirs(dossier, exist_ok=True)
        
        with open(CONSENTEMENT_FILE, 'w') as f:
            f.write("accepte" if accepte else "refuse")
        
        print(f" Consentement webcam enregistré : {'accepté' if accepte else 'refusé'}")
    except Exception as e:
        print(f" Erreur enregistrement : {e}")

def demander_consentement_utilisateur():
    """Demande le consentement à l'utilisateur"""
    print("\n" + "="*60)
    print(" DEMANDE DE CONSENTEMENT - WEBCAM")
    print("="*60)
    print("L'enseignant peut demander une capture webcam en cas de")
    print("suspicion de fraude (téléphone, tiers, etc.).")
    print("="*60)
    
    while True:
        reponse = input("\nAutorisez-vous la capture webcam ? (o/n) : ").lower()
        if reponse in ['o', 'oui', 'yes', 'y']:
            return True
        elif reponse in ['n', 'non', 'no', '']:
            return False
        else:
            print("Veuillez répondre par 'o' (oui) ou 'n' (non)")

async def connecter(token: str):
    """Connecte l'agent au serveur Sentinel"""
    global token_jwt
    token_jwt = token
    
    try:
        async with websockets.connect(
            f"{WS_URL}?token={token}",
            ping_interval=20,
            ping_timeout=10
        ) as ws:
            print(f" Connecté au serveur Sentinel")
            
            await ws.send(json.dumps({
                "type": "AGENT_HELLO",
                "version": "1.0.0",
                "os": sys.platform,
                "consentement_webcam": verifier_consentement()
            }))
            
            async for message in ws:
                try:
                    data = json.loads(message)
                    await traiter_commande(ws, data)
                except json.JSONDecodeError:
                    print(f" Message invalide")
                    
    except Exception as e:
        print(f" Erreur connexion : {e}")

async def traiter_commande(ws, data: dict):
    """Traite les commandes du serveur"""
    action = data.get("action")
    
    if action == "DEMANDER_CONSENTEMENT":
        accepte = demander_consentement_utilisateur()
        enregistrer_consentement(accepte)
        await ws.send(json.dumps({"type": "CONSENTEMENT", "accepte": accepte}))
        
        if accepte:
            image = capturer_webcam()
            if image:
                await ws.send(json.dumps({"type": "WEBCAM_CAPTURE", "image": image, "raison": "CONSENTEMENT_TEST"}))
    
    elif action == "FIN_EXAMEN":
        print(" Fin d'examen — soumission automatique")
        resultat = soumettre_travaux(token_jwt)
        await ws.send(json.dumps({"type": "SOUMISSION", "ok": resultat.get("ok", False), "hash": resultat.get("hash")}))
    
    elif action == "CAPTURER_WEBCAM":
        if not verifier_consentement():
            await ws.send(json.dumps({"type": "WEBCAM_CAPTURE", "error": "Consentement non obtenu"}))
            return
        image = capturer_webcam()
        await ws.send(json.dumps({"type": "WEBCAM_CAPTURE", "image": image}))
    
    elif action == "DEVERROUILLER":
        from network import desactiver_isolation
        desactiver_isolation()
        print(" Agent déverrouillé")
    
    elif action == "PING":
        await ws.send(json.dumps({"type": "PONG"}))