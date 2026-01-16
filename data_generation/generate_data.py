import mysql.connector
import random
from config import DB_CONFIG

# ================= CONNEXION =================
conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor()

# ================= DONNÉES ALGÉRIENNES =================
NOMS_ETUDIANTS = [
    "Benali","Bensaid","Bouzidi","Khelifi","Zerrouki","Touati","Lakhdari","Rahmani",
    "Saadi","Cherif","Amirat","Meghari","Bouras","Hamdi","Meftah","Msili",
    "Hadjrabia","Bendahbia","Boudaoud","Maouche"
]

PRENOMS_ETUDIANTS = [
    "Katia","Chaima","Imane","Sara","Amina","Nour","Salma","Yasmine","Hiba","Aya",
    "Ahmed","Mohamed","Yacine","Sami","Anis","Oussama","Riad","Ilies","Nassim","Walid"
]

NOMS_PROFS = [
    "Benamar","Belkacem","Boumediene","Mansouri","Boudiaf","Saidi","Toufik","Kerboua",
    "Medjber","AitAhmed","Bouguerra","Haddad","Slimani","Ferhat","Djelloul",
    "Kaci","Ouali","Benaissa","Belaid","Ziani"
]

SPECIALITES = [
    "Génie Logiciel","Intelligence Artificielle","Bases de Données",
    "Réseaux","Systèmes","Mathématiques Appliquées","Data Science"
]

# ================= NETTOYAGE =================
print("♻️ Nettoyage de la base...")
tables = [
    "exam_schedule_optimized",
    "exam_schedule_raw",
    "inscriptions",
    "examens",
    "etudiants",
    "modules",
    "professeurs",
    "formations",
    "departements",
    "lieux_examen"
]

for t in tables:
    cur.execute(f"DELETE FROM {t}")
conn.commit()
print("✅ Base nettoyée")

# ================= DÉPARTEMENTS =================
departements = [
    "Informatique",
    "Mathématiques",
    "Physique",
    "Chimie",
    "Biologie",
    "STAPS",
    "Science de la Matière",
    "Agronomie"
]

for d in departements:
    cur.execute("INSERT INTO departements (nom) VALUES (%s)", (d,))
conn.commit()

cur.execute("SELECT id, nom FROM departements")
dept_map = {nom: did for did, nom in cur.fetchall()}
print("✅ Départements insérés")

# ================= FORMATIONS =================
formations = []

# ---- Informatique (NE PAS TOUCHER)
info_id = dept_map["Informatique"]
formations_info = [
    "L1 Informatique",
    "L2 Informatique",
    "L3 Informatique",
    "L3 Systèmes d’Information",
    "M1 Génie Logiciel",
    "M1 Intelligence Artificielle Appliquée",
    "M2 Génie Logiciel",
    "M2 Intelligence Artificielle"
]

for f in formations_info:
    formations.append((f, info_id, random.randint(6, 9)))

# ---- Autres départements (structure contrôlée)
parcours = ["Général", "Recherche", "Professionnel", "Appliqué", "Ingénierie"]
cycles = ["L1", "L2", "L3", "M1", "M2", "D1", "D2"]

for dept, dept_id in dept_map.items():
    if dept == "Informatique":
        continue
    for p in parcours:
        for c in cycles:
            nom = f"{c} {dept} ({p})"
            formations.append((nom, dept_id, random.randint(6, 9)))

cur.executemany("""
INSERT INTO formations (nom, dept_id, nb_modules)
VALUES (%s, %s, %s)
""", formations)

conn.commit()
print(f"✅ {len(formations)} formations insérées (objectif >200 respecté)")

# ================= PROFESSEURS =================
professeurs = []
dept_ids = list(dept_map.values())

for _ in range(120):
    professeurs.append((
        random.choice(NOMS_PROFS),
        random.choice(dept_ids),
        random.choice(SPECIALITES)
    ))

cur.executemany("""
INSERT INTO professeurs (nom, dept_id, specialite)
VALUES (%s, %s, %s)
""", professeurs)
conn.commit()
print("✅ Professeurs insérés")

# ================= MODULES =================
cur.execute("SELECT id FROM formations")
formation_ids = [f[0] for f in cur.fetchall()]

modules = []
for fid in formation_ids:
    for i in range(random.randint(6, 8)):
        modules.append((
            f"Module {i+1}",
            random.randint(2, 4),
            fid,
            None
        ))

cur.executemany("""
INSERT INTO modules (nom, credits, formation_id, pre_req_id)
VALUES (%s, %s, %s, %s)
""", modules)
conn.commit()
print("✅ Modules insérés")

# ================= LIEUX D’EXAMEN =================
lieux = []
for i in range(25):
    lieux.append((f"Salle {i+1}", 30, "salle", "Bloc A"))
for i in range(8):
    lieux.append((f"Amphi {i+1}", random.randint(150, 400), "amphi", "Bloc Central"))

cur.executemany("""
INSERT INTO lieux_examen (nom, capacite, type, batiment)
VALUES (%s, %s, %s, %s)
""", lieux)
conn.commit()
print("✅ Lieux d’examen insérés")

# ================= ÉTUDIANTS =================
etudiants = []
for _ in range(26_000):
    etudiants.append((
        random.choice(NOMS_ETUDIANTS),
        random.choice(PRENOMS_ETUDIANTS),
        random.choice(formation_ids),
        random.randint(2020, 2025)
    ))

cur.executemany("""
INSERT INTO etudiants (nom, prenom, formation_id, promo)
VALUES (%s, %s, %s, %s)
""", etudiants)
conn.commit()
print("✅ 13 000 étudiants insérés")

# ================= INSCRIPTIONS =================
cur.execute("SELECT id, formation_id FROM etudiants")
etudiants_db = cur.fetchall()

cur.execute("SELECT id, formation_id FROM modules")
modules_db = cur.fetchall()

modules_by_formation = {}
for mid, fid in modules_db:
    modules_by_formation.setdefault(fid, []).append(mid)

inscriptions = []
for eid, fid in etudiants_db:
    mods = modules_by_formation.get(fid, [])
    for m in random.sample(mods, min(len(mods), random.randint(4, 6))):
        inscriptions.append((eid, m))

cur.executemany("""
INSERT IGNORE INTO inscriptions (etudiant_id, module_id)
VALUES (%s, %s)
""", inscriptions)
conn.commit()
print("✅ Inscriptions générées")

cur.close()
conn.close()
print("🎉 DATASET GÉNÉRÉ AVEC SUCCÈS")
