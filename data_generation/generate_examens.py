import mysql.connector
from datetime import datetime, timedelta
import random

# Connexion à la base
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="exam_scheduler"
)
cur = conn.cursor()

print("Génération des examens initiaux")

# Nettoyage (DELETE au lieu de TRUNCATE pour éviter l'erreur FK)
cur.execute("DELETE FROM examens")
cur.execute("ALTER TABLE examens AUTO_INCREMENT = 1")  # Remettre l'ID à 1

# Récupération des données nécessaires
cur.execute("SELECT id FROM modules")
modules = [r[0] for r in cur.fetchall()]

cur.execute("SELECT id FROM professeurs")
profs = [r[0] for r in cur.fetchall()]

cur.execute("SELECT id FROM lieux_examen")
salles = [r[0] for r in cur.fetchall()]

# Date de départ des examens
start = datetime(2026, 1, 10, 8, 0)

# Génération des examens (DISTRIBUTION EQUITABLE)
# On mélange les profs pour ne pas toujours favoriser les mêmes par ordre alphabétique
random.shuffle(profs)
nb_profs = len(profs)

for i, module_id in enumerate(modules):
    # Round Robin pour l'équité : on cycle sur la liste des profs
    prof_id = profs[i % nb_profs]
    
    cur.execute("""
        INSERT INTO examens (module_id, prof_id, salle_id, date_heure, duree_minutes)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        module_id,
        prof_id,
        random.choice(salles),
        start + timedelta(hours=2*i),
        120
    ))

# Validation
conn.commit()
cur.close()
conn.close()

print("Examens initiaux générés")
