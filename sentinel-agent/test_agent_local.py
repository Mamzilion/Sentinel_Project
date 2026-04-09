# test_agent.py - Test complet de l'agent
import sys
import os

print("=" * 60)
print(" TEST COMPLET DE L'AGENT SENTINEL")
print("=" * 60)

# Test 1 : Vérifier les imports
print("\n1. Vérification des modules...")
try:
    import psutil
    print("   ✅ psutil")
except: print("   ❌ psutil")

try:
    import cv2
    print("   ✅ opencv")
except: print("   ❌ opencv")

try:
    import websockets
    print("   ✅ websockets")
except: print("   ❌ websockets")

try:
    import cryptography
    print("   ✅ cryptography")
except: print("   ❌ cryptography")

# Test 2 : Webcam
print("\n2. Test webcam...")
from webcam import capturer_webcam
image = capturer_webcam()
print(f"   {'✅ OK' if image else '❌ KO'}")

# Test 3 : Dossier travail
print("\n3. Test dossier travail...")
from config import DOSSIER_TRAVAIL
os.makedirs(DOSSIER_TRAVAIL, exist_ok=True)
print(f"   ✅ {DOSSIER_TRAVAIL}")

# Test 4 : USB
print("\n4. Test détection USB...")
from usb_guard import get_usb_drives
usb = get_usb_drives()
print(f"   ✅ Lecteurs USB détectés : {usb if usb else 'aucun'}")

print("\n" + "=" * 60)
print("✅ Tests terminés")