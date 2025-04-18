import sqlite3
import requests
from datetime import date

API_KEY = "a8509ca3fb0936444107b801b3edab07"
API_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_wind(ville):
    try:
        res = requests.get(API_URL, params={
            "q": ville,
            "appid": API_KEY,
            "units": "metric",
            "lang": "fr"
        })
        return res.json()['wind']['speed']
    except:
        return None

today = date.today().isoformat()

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("SELECT id, ville FROM residences")
residences = cursor.fetchall()

for res_id, ville in residences:
    # Évite d'insérer deux fois la même date pour la même résidence
    cursor.execute("SELECT 1 FROM meteo WHERE residence_id = ? AND date = ?", (res_id, today))
    if cursor.fetchone() is None:
        vent = get_wind(ville)
        cursor.execute("INSERT INTO meteo (residence_id, date, vent) VALUES (?, ?, ?)", (res_id, today, vent))

conn.commit()
conn.close()
print("✅ Données de vent enregistrées pour le jour :", today)
