import sqlite3
from datetime import date, timedelta
import collections
import sys
from pathlib import Path

# ---------------- DB ----------------
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "exam_scheduler.db"

try:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
except Exception as e:
    print(f"ERREUR CONNEXION DB: {e}")
    sys.exit(1)

print("Nettoyage du planning optimise (SQLite)...")
try:
    cur.execute("DELETE FROM exam_schedule_optimized")
    conn.commit()
except Exception as e:
    print(f"ERREUR DELETE: {e}")

# ---------------- PARAMETRES ----------------
start_date = date(2026, 1, 20)
nb_days = 25
time_slots = [1, 2, 3, 4] # 4 Creneaux par jour

dates = [start_date + timedelta(days=i) for i in range(nb_days)]

# ---------------- DATA CHARGEMENT ----------------
print("Chargement des donnees...")

# 1. Etudiants par Module
cur.execute("SELECT module_id, etudiant_id FROM inscriptions")
students_by_module = collections.defaultdict(set)
for mid, sid in cur.fetchall():
    students_by_module[mid].add(sid)

# 2. Examens
cur.execute("""
SELECT e.id, e.prof_id, e.salle_id, e.module_id, l.capacite
FROM examens e
JOIN lieux_examen l ON e.salle_id = l.id
""")
exams_data = cur.fetchall()

# Structurer les examens
exams_list = []
for eid, pid, sid, mid, cap in exams_data:
    students = students_by_module.get(mid, set())
    exams_list.append({
        "id": eid,
        "prof_id": pid,
        "salle_id": sid,
        "students": students,
        "nb_students": len(students),
        "capacity": cap
    })

# ---------------- HEURISTIQUE ----------------
# Trier par nombre d'etudiants decroissant
exams_list.sort(key=lambda x: x["nb_students"], reverse=True)

print(f"{len(exams_list)} examens a planifier.")

# ---------------- MEMOIRE DES OCCUPATIONS ----------------
# (ID, Date, Slot)
occupied_prof_slot = set()
occupied_salle_slot = set()
occupied_student_slot = set()

# (ID, Date) -> Count
prof_daily_load = collections.defaultdict(int)
student_daily_load = collections.defaultdict(int) 

# Contraintes
MAX_EXAMS_PROF_PER_DAY = 3
MAX_EXAMS_STUDENT_PER_DAY = 1 

# ---------------- ALGORITHME ----------------
placed_count = 0
unplaced_exams = []

for exam in exams_list:
    eid = exam["id"]
    pid = exam["prof_id"]
    sid = exam["salle_id"]
    students = exam["students"]
    
    placed = False

    for d in dates:
        if prof_daily_load[(pid, d)] >= MAX_EXAMS_PROF_PER_DAY:
            continue
            
        for slot in time_slots:
            if (pid, d, slot) in occupied_prof_slot:
                continue
            
            if (sid, d, slot) in occupied_salle_slot:
                continue
                
            conflict_found = False
            for student_id in students:
                if (student_id, d, slot) in occupied_student_slot:
                    conflict_found = True
                    break
                if student_daily_load[(student_id, d)] >= MAX_EXAMS_STUDENT_PER_DAY:
                    conflict_found = True
                    break
            
            if conflict_found:
                continue
            
            # SLOT VALIDE TROUVE
            try:
                cur.execute("""
                    INSERT INTO exam_schedule_optimized
                    (exam_id, prof_id, salle_id, date_exam, time_slot)
                    VALUES (?, ?, ?, ?, ?)
                """, (eid, pid, sid, d.strftime("%Y-%m-%d"), slot))
                
                occupied_prof_slot.add((pid, d, slot))
                occupied_salle_slot.add((sid, d, slot))
                prof_daily_load[(pid, d)] += 1
                
                for student_id in students:
                    occupied_student_slot.add((student_id, d, slot))
                    student_daily_load[(student_id, d)] += 1
                    
                placed = True
                placed_count += 1
                break 
            except Exception as e:
                print(f"Erreur INSERT: {e}")
                continue

        if placed:
            break 

    if not placed:
        unplaced_exams.append(eid)
        print(f"Impossible de placer examen {eid} ({exam['nb_students']} etudiants)")

conn.commit()
conn.close()

print("="*40)
print(f"FIN OPTIMISATION")
print(f"Examens places : {placed_count} / {len(exams_list)}")
if unplaced_exams:
    print(f"Examens non places : {len(unplaced_exams)}")
else:
    print("Succes total : Tous les examens sont places !")
