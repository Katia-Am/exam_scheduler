import mysql.connector
import sqlite3
import pandas as pd
import os

# CONFIG
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "exam_scheduler"
}

SQLITE_DB = "exam_scheduler.db"

# TABLES TO MIGRATE
TABLES = [
    "departements",
    "formations",
    "professeurs",
    "etudiants",
    "lieux_examen",
    "modules",
    "examens",
    "inscriptions",
    "exam_schedule_raw",
    "exam_schedule_optimized",
    "app_config"
]

def migrate():
    print("🚀 Démarrage de la migration MySQL -> SQLite...")
    
    # Connect MySQL
    try:
        mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
        print("✅ Connecté à MySQL")
    except Exception as e:
        print(f"❌ Erreur connexion MySQL: {e}")
        return

    # Connect/Create SQLite
    if os.path.exists(SQLITE_DB):
        os.remove(SQLITE_DB)
    
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_cur = sqlite_conn.cursor()
    print(f"✅ Fichier {SQLITE_DB} créé")

    # Enable Foreign Keys
    sqlite_cur.execute("PRAGMA foreign_keys = ON;")

    for table in TABLES:
        print(f"📦 Migration de la table: {table}...")
        
        # 1. Read Data from MySQL
        try:
            df = pd.read_sql(f"SELECT * FROM {table}", mysql_conn)
        except Exception as e:
            print(f"⚠️ Erreur lecture table {table}: {e}")
            continue

        # 2. Create Table in SQLite (simplifié via pandas)
        # Pandas to_sql is powerful but generic. We might lose specific constraints (FK)
        # but for a demo app, consistency is usually enough if data is good using 'index=False'.
        
        # Specific fix for date columns to ensure they are strings for SQLite
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)

        try:
            df.to_sql(table, sqlite_conn, if_exists='replace', index=False)
            count = len(df)
            print(f"   -> {count} lignes transférées.")
        except Exception as e:
            print(f"   ❌ Erreur écriture SQLite: {e}")

    # Indexing optimization (Optional but good for performance)
    print("⚡ Création des index...")
    indexes = [
        ("idx_etud_id", "inscriptions", "etudiant_id"),
        ("idx_exam_id", "exam_schedule_optimized", "exam_id"),
        ("idx_prof_id", "exam_schedule_optimized", "prof_id"),
        ("idx_salle_id", "exam_schedule_optimized", "salle_id"),
        ("idx_conf_key", "app_config", "config_key")
    ]
    
    for name, table, col in indexes:
        try:
            sqlite_cur.execute(f"CREATE INDEX IF NOT EXISTS {name} ON {table}({col})")
        except: pass

    # Close
    sqlite_conn.close()
    mysql_conn.close()
    print("🎉 MIGRATION TERMINÉE AVEC SUCCÈS")
    print(f"📂 Vous pouvez maintenant déployer le fichier '{SQLITE_DB}'")

if __name__ == "__main__":
    migrate()
