import os
import sqlite3
import json

DB_NAME = "students.db"

# Si la base existe déjà, on ne fait rien
if os.path.exists(DB_NAME):
    print("📁 Base déjà existante, aucune action nécessaire.")
else:
    print("🛠️ Création de la base...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Création des tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS etudiants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        groupe TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS residences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        etudiant_id INTEGER NOT NULL,
        adresse TEXT NOT NULL,
        ville TEXT NOT NULL,
        date_debut TEXT NOT NULL,
        date_fin TEXT,
        FOREIGN KEY (etudiant_id) REFERENCES etudiants(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meteo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        residence_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        vent REAL,
        FOREIGN KEY (residence_id) REFERENCES residences(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historique_recherches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT,
        ville1 TEXT,
        vent1 REAL,
        ville2 TEXT,
        vent2 REAL,
        heure TEXT
    )
    """)

    print("✅ Tables créées.")

    # Chargement du fichier JSON
    try:
        with open("etudiants.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        for etu in data:
            cursor.execute("INSERT INTO etudiants (nom, prenom, groupe) VALUES (?, ?, ?)",
                           (etu["nom"].upper(), etu["prenom"].capitalize(), etu["groupe"]))
            etudiant_id = cursor.lastrowid

            for res in etu["residences"]:
                cursor.execute("""
                    INSERT INTO residences (etudiant_id, adresse, ville, date_debut, date_fin)
                    VALUES (?, ?, ?, ?, ?)
                """, (etudiant_id, res["adresse"], res["ville"], res["date_debut"], res["date_fin"]))

        print("📥 Étudiants importés depuis le JSON.")
        conn.commit()
    except Exception as e:
        print("❌ Erreur lors de l'import :", e)
    finally:
        conn.close()
