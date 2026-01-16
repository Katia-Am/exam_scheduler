import mysql.connector
from pathlib import Path

# Config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "exam_scheduler"
}

SQL_FILE = Path(__file__).parent.parent / "sql" / "full_schema.sql"

def run_sql_file():
    print(f"🔌 Connexion à la BDD {DB_CONFIG['database']}...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print(f"📖 Lecture de {SQL_FILE}...")
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        # Split statements (naïve approach but sufficient for schema)
        statements = sql_content.split(';')
        
        count = 0
        for statement in statements:
            stmt = statement.strip()
            if stmt:
                try:
                    cur.execute(stmt)
                    count += 1
                except mysql.connector.Error as err:
                    print(f"⚠️ Erreur sur : {stmt[:50]}... \n -> {err}")
        
        conn.commit()
        print(f"✅ {count} instructions SQL exécutées avec succès.")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur critique : {e}")

if __name__ == "__main__":
    run_sql_file()
