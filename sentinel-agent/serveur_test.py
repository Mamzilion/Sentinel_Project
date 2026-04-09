# serveur_test.py - Serveur Sentinel factice pour tester l'agent
import asyncio
import websockets
import json
import time
from datetime import datetime

# Stockage des connexions actives
connexions = set()

async def envoyer_commande(websocket, commande):
    """Envoie une commande à l'agent"""
    await websocket.send(json.dumps(commande))
    print(f" Commande envoyée : {commande.get('action')}")

async def gerer_agent(websocket, path):
    """Gère la communication avec un agent"""
    connexions.add(websocket)
    print(f" Agent connecté (total: {len(connexions)})")
    
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f" Reçu de l'agent : {data.get('type', 'INCONNU')}")
            
            if data.get("type") == "SOUMISSION":
                print(f" Travaux reçus !")
                print(f"   → Hash SHA-256 : {data.get('hash')}")
                print(f"   → Succès : {data.get('ok')}")
                
            elif data.get("type") == "WEBCAM_CAPTURE":
                taille = len(data.get('image', ''))
                print(f"📸 Image webcam reçue ! (taille: {taille} caractères)")
                
            elif data.get("type") == "PONG":
                print(f" Pong reçu")
                
    except websockets.exceptions.ConnectionClosed:
        print(f" Agent déconnecté")
    finally:
        connexions.remove(websocket)

async def menu_interactif():
    """Menu pour envoyer des commandes"""
    while True:
        await asyncio.sleep(0.1)
        
        print("\n" + "="*50)
        print(" SERVEUR SENTINEL - MODE TEST")
        print("="*50)
        print(f" Agents connectés : {len(connexions)}")
        print("\nCommandes :")
        print("  1 → FIN_EXAMEN")
        print("  2 → CAPTURER_WEBCAM")
        print("  3 → DEVERROUILLER")
        print("  4 → PING")
        print("  q → Quitter")
        print("="*50)
        
        choix = await asyncio.get_event_loop().run_in_executor(None, input, "Votre choix : ")
        
        if choix == "q":
            print(" Arrêt...")
            break
        elif choix == "1":
            commande = {"action": "FIN_EXAMEN"}
        elif choix == "2":
            commande = {"action": "CAPTURER_WEBCAM", "raison": "COMMANDE_MANUEL"}
        elif choix == "3":
            commande = {"action": "DEVERROUILLER"}
        elif choix == "4":
            commande = {"action": "PING"}
        else:
            print(" Commande inconnue")
            continue
        
        if connexions:
            for ws in connexions:
                await envoyer_commande(ws, commande)
        else:
            print(" Aucun agent connecté")

async def main():
    server = await websockets.serve(gerer_agent, "127.0.0.1", 3000)
    
    print("="*50)
    print(" SERVEUR SENTINEL DE TEST DÉMARRÉ")
    print("="*50)
    print(" Adresse : ws://127.0.0.1:3000")
    print(" En attente de connexion...")
    print("="*50)
    
    try:
        await asyncio.gather(server.wait_closed(), menu_interactif())
    except KeyboardInterrupt:
        print("\n Arrêt...")
        server.close()
        await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())