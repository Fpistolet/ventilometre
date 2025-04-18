from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import reset_db
import collect_wind

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    historique = []
    historique_utilisateur = []
    vent_collectif = None

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    # Vérifie que la colonne 'prenom' existe dans historique_recherches, sinon l'ajoute
    try:
        cursor.execute("ALTER TABLE historique_recherches ADD COLUMN prenom TEXT")
    except sqlite3.OperationalError:
        pass  # Colonne déjà existante, on ignore l'erreur

    # Calcul du vent médian collectif
    cursor.execute("SELECT vent FROM meteo WHERE date = date('now')")
    vents = [row[0] for row in cursor.fetchall() if row[0] is not None]
    if vents:
        vents.sort()
        n = len(vents)
        vent_collectif = vents[n // 2] if n % 2 == 1 else (vents[n // 2 - 1] + vents[n // 2]) / 2

    if request.method == "POST":
        nom_recherche = request.form["nom"]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            SELECT e.id, e.nom, e.prenom, r.ville, r.date_fin, r.id
            FROM etudiants e
            JOIN residences r ON e.id = r.etudiant_id
            WHERE e.nom = ?
        """, (nom_recherche.upper(),))
        rows = cursor.fetchall()

        if rows:
            id_, nom, prenom, ville1, _, res1_id = rows[0]
            ville2 = None
            res2_id = None
            for row in rows[1:]:
                if row[4] is not None:
                    ville2 = row[3]
                    res2_id = row[5]

            cursor.execute("SELECT vent FROM meteo WHERE residence_id = ? AND date = date('now')", (res1_id,))
            vent1 = cursor.fetchone()
            vent1 = vent1[0] if vent1 else None

            vent2 = None
            if res2_id:
                cursor.execute("SELECT vent FROM meteo WHERE residence_id = ? AND date = date('now')", (res2_id,))
                res = cursor.fetchone()
                vent2 = res[0] if res else None

            cursor.execute("""
                INSERT INTO historique_recherches (nom, prenom, ville1, vent1, ville2, vent2, heure)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nom, prenom, ville1, vent1, ville2, vent2, now))

            result = {
                "nom": nom,
                "prenom": prenom,
                "ville1": ville1,
                "vent1": vent1,
                "ville2": ville2,
                "vent2": vent2
            }

    cursor.execute("SELECT * FROM historique_recherches ORDER BY id DESC LIMIT 10")
    historique = cursor.fetchall()

    if result:
        cursor.execute("SELECT * FROM historique_recherches WHERE nom = ?", (result["nom"],))
        historique_utilisateur = cursor.fetchall()

    conn.commit()
    conn.close()

    return render_template("index.html", result=result, historique=historique,
                           historique_utilisateur=historique_utilisateur, vent_collectif=vent_collectif)

@app.route("/clear", methods=["POST"])
def clear_history():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historique_recherches")
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/etudiants")
def etudiants():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.id, e.nom, e.prenom, e.groupe, r.ville, r.date_fin
        FROM etudiants e
        JOIN residences r ON e.id = r.etudiant_id
        ORDER BY e.id, r.date_fin IS NULL DESC, r.date_fin
    """)
    rows = cursor.fetchall()
    conn.close()

    etudiants_data = {}

    for id_, nom, prenom, groupe, ville, date_fin in rows:
        if id_ not in etudiants_data:
            etudiants_data[id_] = {
                "nom": nom,
                "prenom": prenom,
                "groupe": groupe,
                "ville_principale": None,
                "ville_secondaire": None
            }

        if date_fin is None and etudiants_data[id_]["ville_principale"] is None:
            etudiants_data[id_]["ville_principale"] = ville
        elif date_fin is not None and etudiants_data[id_]["ville_secondaire"] is None:
            etudiants_data[id_]["ville_secondaire"] = ville

    etudiants = list(etudiants_data.values())

    return render_template("etudiants.html", etudiants=etudiants)

if __name__ == "__main__":
    app.run(debug=True)
