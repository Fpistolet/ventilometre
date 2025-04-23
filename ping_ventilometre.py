import requests
import time

URL = "https://ventilometre.onrender.com"  

while True:
    try:
        print("🔁 Ping en cours...")
        res = requests.get(URL)
        print(f"✅ Statut : {res.status_code} ({res.reason})")
    except Exception as e:
        print(f"❌ Erreur : {e}")

    time.sleep(600)  # attends 10 minutes (600 secondes)
