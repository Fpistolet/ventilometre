import json
import sqlite3

# Charger le fichier JSON
with open("etudiants.json", "r", encoding="utf-8") as f:
    etudiants = json.load(f)

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

for etu in etudiants:
    nom = etu["nom"].upper()
    prenom = etu["prenom"].capitalize()
    groupe = etu.get("groupe", "INCONNU")

    # Vérifie si l'étudiant existe déjà
    cursor.execute("SELECT id FROM etudiants WHERE nom = ? AND prenom = ?", (nom, prenom))
    row = cursor.fetchone()

    if row:
        etudiant_id = row[0]
    else:
        cursor.execute("INSERT INTO etudiants (nom, prenom, groupe) VALUES (?, ?, ?)", (nom, prenom, groupe))
        etudiant_id = cursor.lastrowid

    for res in etu["residences"]:
        adresse = res["adresse"]
        ville = res["ville"]
        date_debut = res["date_debut"]
        date_fin = res["date_fin"]
        cursor.execute("""
            INSERT INTO residences (etudiant_id, adresse, ville, date_debut, date_fin)
            VALUES (?, ?, ?, ?, ?)
        """, (etudiant_id, adresse, ville, date_debut, date_fin))

conn.commit()
conn.close()

print("Import terminé sans doublons.")