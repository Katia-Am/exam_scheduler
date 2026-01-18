import sqlite3
import random
from datetime import date, timedelta
from pathlib import Path

# DB PATH
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "exam_scheduler.db"

# CONNEXION SQLITE
conn = sqlite3.connect(str(DB_PATH))
cur = conn.cursor()

print("Génération planning BRUT (SQLite)")

# RESET TABLE
cur.execute("DELETE FROM exam_schedule_raw")

# DATA
cur.execute("SELECT id FROM examens")
exam_ids = [r[0] for r in cur.fetchall()]

cur.execute("SELECT id FROM professeurs")
profs = [r[0] for r in cur.fetchall()]

cur.execute("SELECT id FROM lieux_examen")
salles = [r[0] for r in cur.fetchall()]

start = date(2026, 1, 10)
# Use legacy slot format for RAW to match expectations or consistent ID?
# App expects display string. Let's send INT slots 1-4 to be consistent with Optimization if we want,
# OR keep strings but ensure app handles it.
# The `generate_raw_schedule.py` used strings. `streamlit_app.py` has code to handle both or just display.
# Let's keep strict strings for raw as it highlights the "bad" nature.
slots = ["08:30 - 10:00", "10:30 - 12:00", "13:00 - 14:30", "15:00 - 16:30"]

# INSERT NAÏF (VOLONTAIREMENT)
for exam_id in exam_ids:
    cur.execute("""
        INSERT INTO exam_schedule_raw
        (exam_id, prof_id, salle_id, date_exam, time_slot)
        VALUES (?, ?, ?, ?, ?)
    """, (
        exam_id,
        random.choice(profs),
        random.choice(salles),
        (start + timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d"), # SQLite needs string dates
        random.choice(slots)
    ))

conn.commit()
cur.close()
conn.close()

print("Planning BRUT généré (avec conflits)")

print("Planning BRUT généré (avec conflits)")
