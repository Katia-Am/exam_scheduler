import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "exam_scheduler"
}

conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor()

print("🔧 Création de la table de configuration...")
cur.execute("""
CREATE TABLE IF NOT EXISTS app_config (
    config_key VARCHAR(50) PRIMARY KEY,
    config_value VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
""")

# Initialisation des valeurs par défaut si elles n'existent pas
defaults = [
    ('global_validated', '0'),
    ('published', '0')
]

for k, v in defaults:
    cur.execute("""
    INSERT IGNORE INTO app_config (config_key, config_value) VALUES (%s, %s)
    """, (k, v))

# Pour les départements, on va créer une entrée par département "dept_validated_{id}"
cur.execute("SELECT id FROM departements")
dept_ids = [r[0] for r in cur.fetchall()]

for did in dept_ids:
    k = f"dept_validated_{did}"
    cur.execute("""
    INSERT IGNORE INTO app_config (config_key, config_value) VALUES (%s, '0')
    """, (k,))

conn.commit()
cur.close()
conn.close()
print("✅ Table app_config prête et initialisée.")
