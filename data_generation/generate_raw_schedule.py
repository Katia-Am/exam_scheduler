import mysql.connector
import random
from datetime import date, timedelta


# CONNEXION MYSQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",          # adapte si besoin
    password="",          # adapte si besoin
    database="exam_scheduler"
)
cur = conn.cursor()

print("Génération planning BRUT")


# RESET TABLE
cur.execute("TRUNCATE TABLE exam_schedule_raw")


# DATA
cur.execute("SELECT id FROM examens")
exam_ids = [r[0] for r in cur.fetchall()]

cur.execute("SELECT id FROM professeurs")
profs = [r[0] for r in cur.fetchall()]

cur.execute("SELECT id FROM lieux_examen")
salles = [r[0] for r in cur.fetchall()]

start = date(2026, 1, 10)
slots = ["08:00-10:00", "10:30-12:30", "14:00-16:00"]


# INSERT NAÏF (VOLONTAIREMENT)
for exam_id in exam_ids:
    cur.execute("""
        INSERT INTO exam_schedule_raw
        (exam_id, prof_id, salle_id, date_exam, time_slot)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        exam_id,
        random.choice(profs),
        random.choice(salles),
        start + timedelta(days=random.randint(0, 5)),
        random.choice(slots)
    ))

conn.commit()
cur.close()
conn.close()

print("Planning BRUT généré (avec conflits)")
