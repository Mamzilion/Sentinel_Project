# webcam.py
import cv2
import base64
from datetime import datetime

def capturer_webcam() -> str:
    """Capture une image et retourne en base64"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print(" Webcam indisponible")
        return None
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return None
    
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
    image_b64 = base64.b64encode(buffer).decode('utf-8')
    
    print(f"📸 Capture webcam effectuée à {datetime.now():%H:%M:%S}")
    return image_b64

if __name__ == "__main__":
    image = capturer_webcam()
    if image:
        print(f" Capture réussie ({len(image)} caractères)")