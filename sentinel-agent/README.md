# Agent Sentinel - Mon agent de surveillance d'examen

## Ce que fait l'agent
-  Bloque Internet (sauf serveur)
-  Tue les apps non autorisées
-  Éjecte les clés USB
-  Détecte les changements de fenêtre
-  Force le plein écran
-  Capture la webcam
-  Soumet les travaux automatiquement

## Installation manuelle

```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt

##  Description de chaque fichier
### Dossier `src/` (code principal)
le fichier `main.py` sert de Point d'entrée il est charge de Lancer tous les blocages et la connexion au serveur 
le fichier `config.py`  sert de **Configuration** - IP du serveur, ports, dossiers, applications autorisées  
le fichier `network.py` permet l'Isolation réseau Active/désactive le blocage Internet via le firewall  
le fichier `process_guard.py` permet le Blocage des processus il, Tue toute application non autorisée 
le fichier `usb_guard.py` permet le Blocage USB il Détecte et éjecte les clés USB 
le fichier `webcam.py`   permet de faire des Captures webcam il Prend une photo et la convertit en texte (base64) 
le fichier `submit.py` permet la Soumission des travaux il Compresse, calcule l'empreinte et envoie au serveur 
le fichier `ws_client.py`  permet la Communication il Dialogue en temps réel avec le serveur (WebSocket)
le fichier `focus_guard.py`  permet le Mode kiosque il Surveille les changements de fenêtre (Alt+Tab) 
le fichier  `kiosk_mode.py` permet le Plein écran forcé il Lance le navigateur en mode kiosque et maintient le plein écran 

### Dossier `tests/`

le fichier  `test_agent.py` permet de faire un Test rapide pour vérifier que tout fonctionne 

### Dossier `scripts/` 
 `install.bat` | Installe automatiquement l'environnement et les dépendances 
 

 ##  Dossier `scripts/` (utilitaires)
    Ce dossier contient des scripts optionnels pour faciliter l'installation et l'utilisation de l'agent.

| Fichier         | Rôle                                                | Commande                |
|--------------   |------                                               |                         |
| `install.bat`   | Installe l'environnement virtuel et les dépendances | `scripts\install.bat`   |
| `start.bat`     | Lance l'agent rapidement                            | `scripts\start.bat`     |
| `uninstall.bat` | Supprime l'environnement virtuel                    | `scripts\uninstall.bat` |


### Fichiers racine

 `requirements.txt` | Liste des bibliothèques Python à installer |


##  Comment exécuter mon agent

```bash
# 1. Activer l'environnement
env\Scripts\activate

# 2. Lancer l'agent
python src/main.py