import streamlit as st
import sqlite3
import pandas as pd
import subprocess
from pathlib import Path
import sys
import warnings

# ---------------- CONFIG & WARNINGS ----------------
st.set_page_config(page_title="Université de Boumerdès - Exam Scheduler", layout="wide", page_icon="🎓")
warnings.filterwarnings('ignore')

# ---------------- PATHS ----------------
BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPT_OPTIMIZE = BASE_DIR / "data_generation" / "generate_optimized_schedule.py" # Note: Scripts also need update if run online
SCRIPT_RAW = BASE_DIR / "data_generation" / "generate_raw_schedule.py"
BANNER_PATH = Path(__file__).parent / "home_banner.jpg"

# DB PATH
DB_PATH = BASE_DIR / "exam_scheduler.db"

# ---------------- DB UTILS ----------------
def get_connection():
    try:
        # Check if DB exists
        if not DB_PATH.exists():
            st.error(f"Base de données introuvable : {DB_PATH}")
            return None
        return sqlite3.connect(str(DB_PATH))
    except Exception as e:
        st.error(f"Erreur DB: {e}")
        return None

def get_config(key):
    conn = get_connection()
    if not conn: return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT config_value FROM app_config WHERE config_key = ?", (key,))
        res = cur.fetchone()
        return res[0] if res else '0'
    finally:
        conn.close()

def set_config(key, value):
    conn = get_connection()
    if not conn: return
    try:
        cur = conn.cursor()
        # SQLite Upsert
        cur.execute("""
            INSERT INTO app_config (config_key, config_value) 
            VALUES (?, ?)
            ON CONFLICT(config_key) DO UPDATE SET config_value = excluded.config_value
        """, (key, value))
        conn.commit()
    finally:
        conn.close()

# ---------------- SESSION & AUTH ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

def login_required(role_name):
    CREDS = {"Administrateur": "admin", "Vice-Doyen": "doyen", "Chef de Département": "dept"}
    
    if st.session_state.logged_in and st.session_state.role == role_name:
        return True
    
    st.sidebar.markdown(f"---")
    st.sidebar.subheader(f"🔑 Connexion {role_name}")
    pwd = st.sidebar.text_input("Mot de passe", type="password", key=f"login_{role_name}")
    if st.sidebar.button("Se connecter", key=f"btn_{role_name}"):
        if pwd == CREDS.get(role_name):
            st.session_state.logged_in = True
            st.session_state.role = role_name
            st.rerun()
        else:
            st.sidebar.error("Mot de passe incorrect")
    return False

# ----------------- UI COMPONENTS -----------------

def display_header():
    # Banner
    if BANNER_PATH.exists():
        st.image(str(BANNER_PATH), use_container_width=True)
    else:
        st.title("🎓 Université de Boumerdès - Plateforme Examens")

def format_slot(val):
    MAP = {1: "08:30 - 10:00", 2: "10:30 - 12:00", 3: "13:00 - 14:30", 4: "15:00 - 16:30"}
    try:
        val_int = int(val)
        return MAP.get(val_int, f"Slot {val}")
    except:
        return val

# ----------------- VIEWS -----------------

def view_admin():
    if not login_required("Administrateur"): return

    st.title("🛠️ Espace Administrateur (Planification)")
    
    conn = get_connection()
    
    # Check Status
    optimized = get_config("optimized_flag") == '1'
    
    # Counts
    count_raw = pd.read_sql("SELECT COUNT(*) FROM exam_schedule_raw", conn).iloc[0,0]
    count_opt = pd.read_sql("SELECT COUNT(*) FROM exam_schedule_optimized", conn).iloc[0,0]
    
    final_validated = get_config("global_validated") == '1'
    published = get_config("published") == '1'

    # --- TABS FOR WORKFLOW ---
    tab1, tab2, tab3 = st.tabs(["1. Planning Initial & Conflits", "2. Optimisation", "3. Publication"])
    
    with tab1:
        st.subheader("📋 Planning Initial (Brut)")
        if count_raw > 0:
            st.info(f"✅ Planning initial généré ({count_raw} examens). Contient des conflits.")
            
            # SHOW CONFLICTS FOR RAW
            st.markdown("### 🚨 Détection des Conflits (Planning Initial)")
            
            def show_conflicts_raw():
                q_stud = """
                SELECT i.etudiant_id, s.date_exam, s.time_slot, COUNT(*) as nb
                FROM inscriptions i
                JOIN examens e ON i.module_id = e.module_id 
                JOIN exam_schedule_raw s ON s.exam_id = e.id 
                GROUP BY i.etudiant_id, s.date_exam, s.time_slot HAVING nb > 1 LIMIT 50"""
                
                df = pd.read_sql(q_stud, conn)
                if not df.empty:
                    st.error(f"🛑 {len(df)}+ Conflits Étudiants détectés (50 premiers affichés)")
                    st.dataframe(df, hide_index=True)
                else:
                    st.success("Aucun conflit étudiant (Surprenant pour un brut !)")

            show_conflicts_raw()
            
        else:
            st.warning("⚠️ Aucun planning initial. Le système est vide.")
            st.markdown("### 1️⃣ Étape 1 : Génération du Planning Initial")
            
            # NOTE: On Cloud, we cannot run subprocesses like this easily if they interact with DB without connection changes.
            # But for "Deployment Ready" code using SQLite, the scripts ALSO need to use SQLite.
            # We assume user won't regenerate data ON THE CLOUD (Read-Only Demo usually), 
            # OR we need to update scripts. For now, we disable generation on cloud or warn.
            
            if st.button("🎲 Générer Automatiquement le Planning (Non Optimisé)", type="primary"):
                 st.warning("⚠️ Attention : La génération complète n'est pas disponible en mode Cloud/Démo SQLite (Lecture Seule).")
                 # We disable actual generation logic for the Cloud/SQLite version to allow simple deployment
                 # unless we migrated scripts too.
                 # Given limited time, we assume the data GENERATED LOCALLY is what we show.

    with tab2:
        st.subheader("⚙️ Optimisation")
        
        c1, c2 = st.columns([2, 1])
        with c1:
            if count_opt > 0:
                st.success(f"✅ Planning Optimisé Disponible ({count_opt} examens).")
                st.caption("Le planning optimisé est sensé n'avoir aucun conflit.")
            else:
                st.warning("En attente d'optimisation.")

        with c2:
            if st.button("🚀 Lancer l'Algorithme d'Optimisation"):
                # Same here: Optimization script uses MySQL connector. 
                # For the demo, we likely want to just SHOW the result we already calculated locally.
                # So we won't run the script, we just say "Optimization Done" (Mock) if data exists.
                if count_opt > 0:
                     st.success("Optimisation (simulée pour Cloud) terminée !")
                     set_config("optimized_flag", "1")
                     st.rerun()
                else:
                     st.error("Impossible de lancer l'optimisation en mode Cloud sans scripts adaptés.")

            if st.button("🔄 Réinitialiser TOTALEMENT (Démo)"):
                c = conn.cursor()
                c.execute("DELETE FROM exam_schedule_optimized")
                # c.execute("DELETE FROM exam_schedule_raw") # Don't delete RAW on cloud if we can't regenerate it easily
                c.execute("UPDATE app_config SET config_value='0' WHERE config_key LIKE 'global%' OR config_key LIKE 'dept%'") 
                conn.commit()
                st.success("Remise à zéro partielle (Optimisé effacé) pour démo.")
                st.rerun()
        
        # Verify Optimized Conflicts
        if count_opt > 0:
            st.markdown("#### 🔍 Vérification post-optimisation")
            nb_conflicts = pd.read_sql("""
                SELECT COUNT(*) FROM (
                    SELECT etudiant_id, date_exam, time_slot FROM inscriptions i 
                    JOIN examens e ON i.module_id=e.module_id 
                    JOIN exam_schedule_optimized s ON s.exam_id=e.id 
                    GROUP BY etudiant_id, date_exam, time_slot HAVING COUNT(*)>1
                ) as t
            """, conn).iloc[0,0]
            
            if nb_conflicts == 0:
                st.balloons()
                st.success("✅ 0 Conflits détectés dans le planning optimisé !")
            else:
                st.error(f"⚠️ Il reste {nb_conflicts} conflits.")

    with tab3:
        st.subheader("📢 Publication")
        if published:
            st.success("✅ PUBLIÉ AUX ÉTUDIANTS")
            if st.button("Retirer la publication"):
                set_config("published", "0")
                st.rerun()
        else:
            status_text = "En attente de validation Vice-Doyen"
            btn_disabled = True
            
            if final_validated:
                status_text = "✅ Validé par le Vice-Doyen. Prêt à publier."
                btn_disabled = False
            
            st.info(f"Statut : {status_text}")
            
            if st.button("Publier le Planning Officiel", disabled=btn_disabled):
                set_config("published", "1")
                st.rerun()
    
    conn.close()

def view_dept_head():
    if not login_required("Chef de Département"): return
    
    conn = get_connection()
    st.title("👤 Espace Chef de Département")
    
    # Select Dept
    depts = pd.read_sql("SELECT id, nom FROM departements", conn)
    dept_choice = st.selectbox("Département", depts['nom'])
    dept_id = depts[depts['nom'] == dept_choice]['id'].values[0]
    
    # Check Validation Status
    val_key = f"dept_validated_{dept_id}"
    is_validated = get_config(val_key) == '1'
    
    # Actions
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"### Planning : {dept_choice}")
    with c2:
        if is_validated:
            st.success("✅ Validé")
            if st.button("Annuler Validation"):
                set_config(val_key, "0")
                st.rerun()
        else:
            st.warning("⚠️ Non Validé")
            if st.button("✅ Valider le planning"):
                set_config(val_key, "1")
                st.rerun()
    
    # Show Schedule
    q = f"""
        SELECT m.nom as Module, f.nom as Formation, s.date_exam, s.time_slot as Creneau, l.nom as Salle
        FROM exam_schedule_optimized s
        JOIN examens e ON s.exam_id = e.id
        JOIN modules m ON e.module_id = m.id
        JOIN formations f ON m.formation_id = f.id
        JOIN lieux_examen l ON s.salle_id = l.id
        WHERE f.dept_id = {dept_id}
        ORDER BY s.date_exam, s.time_slot
    """
    df = pd.read_sql(q, conn)
    if not df.empty:
        if pd.api.types.is_numeric_dtype(df['Creneau']): df['Creneau'] = df['Creneau'].apply(format_slot)
        st.dataframe(df, hide_index=True)
    else:
        st.info("Pas de données (Optimisation requise).")
        
    conn.close()

def view_vice_dean():
    if not login_required("Vice-Doyen"): return
    
    conn = get_connection()
    st.title("📊 Espace Vice-Doyen (Stratégie & Validation)")
    
    # 1. Global KPIs (Moved from Admin as requested)
    st.subheader("1. Vue Stratégique Globale")
    
    has_data = pd.read_sql("SELECT COUNT(*) FROM exam_schedule_optimized", conn).iloc[0,0] > 0
    if not has_data:
        st.warning("Veuillez attendre que l'Administrateur génère le planning.")
        return

    # Stats
    k1, k2, k3 = st.columns(3)
    k1.metric("Examens Total", pd.read_sql("SELECT COUNT(*) FROM exam_schedule_optimized", conn).iloc[0,0])
    k2.metric("Salles Utilisées", pd.read_sql("SELECT COUNT(DISTINCT salle_id) FROM exam_schedule_optimized", conn).iloc[0,0])
    k3.metric("Jours Mobilisés", pd.read_sql("SELECT COUNT(DISTINCT date_exam) FROM exam_schedule_optimized", conn).iloc[0,0])

    # 2. Conflicts
    st.divider()
    st.subheader("2. Analyse des Conflits")
    
    nb_conflicts = pd.read_sql("""
        SELECT COUNT(*) FROM (
            SELECT etudiant_id, date_exam, time_slot FROM inscriptions i 
            JOIN examens e ON i.module_id=e.module_id 
            JOIN exam_schedule_optimized s ON s.exam_id=e.id 
            GROUP BY etudiant_id, date_exam, time_slot HAVING COUNT(*)>1
        ) as t
    """, conn).iloc[0,0]
    
    if nb_conflicts == 0:
        st.success("✅ 0 Conflits (Parfait)")
    else:
        st.error(f"🛑 {nb_conflicts} Conflits détectés")

    # 3. Validation Status per Dept
    st.divider()
    st.subheader("3. État des Validations Départements")
    
    depts = pd.read_sql("SELECT id, nom FROM departements", conn)
    all_validated = True
    
    cols = st.columns(4)
    for idx, row in depts.iterrows():
        did, dnom = row['id'], row['nom']
        status = get_config(f"dept_validated_{did}") == '1'
        if not status: all_validated = False
        
        with cols[idx % 4]:
            st.metric(label=dnom, value="✅ OK" if status else "⏳ En attente")

    # 4. Final Validation
    st.divider()
    st.subheader("4. Validation Finale")
    
    global_val = get_config("global_validated") == '1'
    
    if global_val:
        st.success("✅ PLANNING VALIDÉ PAR LE VICE-DOYEN")
        if st.button("Annuler Validation Globale"):
            set_config("global_validated", "0")
            st.rerun()
    else:
        if all_validated:
            st.info("Tous les départements ont validé. Vous pouvez procéder.")
            if st.button("✅ Valider le Planning Global"):
                set_config("global_validated", "1")
                st.balloons()
                st.rerun()
        else:
            st.warning("En attente de la validation de tous les chefs de département.")
            st.button("Valider le Planning Global", disabled=True, help="Attendre les départements")
            
    conn.close()

def view_public_consultation():
    # Student / Prof View
    st.title("🎓 Consultation des Plannings")
    
    connected = get_config("published") == '1'
    
    if not connected:
        st.warning("🔒 Le planning n'est pas encore publié par l'administration. Veuillez revenir plus tard.")
        st.info("Statut : En cours de validation.")
        return

    conn = get_connection()
    
    tab1, tab2 = st.tabs(["🔍 Recherche par ID", "📂 Filtrage par Formation"])
    
    with tab1:
        # Search by ID (Existing)
        col1, col2 = st.columns(2)
        user_type = col1.radio("Je suis :", ["Étudiant", "Professeur"])
        user_id = col2.text_input(f"Mon ID {user_type}", help="Ex: 1, 100...")
        
        if col2.button("Chercher"):
            if user_type == "Étudiant":
                q = f"""
                SELECT m.nom as Module, s.date_exam, s.time_slot, l.nom as Salle
                FROM inscriptions i
                JOIN examens e ON i.module_id = e.module_id
                JOIN exam_schedule_optimized s ON s.exam_id = e.id
                JOIN modules m ON e.module_id = m.id
                JOIN lieux_examen l ON s.salle_id = l.id
                WHERE i.etudiant_id = {user_id}
                ORDER BY s.date_exam, s.time_slot
                """
            else:
                q = f"""
                SELECT m.nom as Module, f.nom as Formation, s.date_exam, s.time_slot, l.nom as Salle
                FROM exam_schedule_optimized s
                JOIN examens e ON s.exam_id = e.id
                JOIN modules m ON e.module_id = m.id
                JOIN formations f ON m.formation_id = f.id
                JOIN lieux_examen l ON s.salle_id = l.id
                WHERE s.prof_id = {user_id}
                ORDER BY s.date_exam, s.time_slot
                """
            try:
                df = pd.read_sql(q, conn)
                if not df.empty:
                    st.success(f"Planning trouvé !")
                    if pd.api.types.is_numeric_dtype(df['time_slot']): df['time_slot'] = df['time_slot'].apply(format_slot)
                    st.table(df)
                else:
                    st.error("Aucun résultat.")
            except: st.error("Erreur ID")

    with tab2:
        # Filter by Formation (New Request)
        depts = pd.read_sql("SELECT id, nom FROM departements", conn)
        d_choice = st.selectbox("1. Choisir Département", depts['nom'])
        did = depts[depts['nom'] == d_choice]['id'].values[0]
        
        forms = pd.read_sql(f"SELECT id, nom FROM formations WHERE dept_id={did}", conn)
        f_choice = st.selectbox("2. Choisir Formation", forms['nom'])
        fid = forms[forms['nom'] == f_choice]['id'].values[0]
        
        if st.button("Voir le Planning de la Promo"):
            q = f"""
            SELECT m.nom as Module, s.date_exam, s.time_slot, l.nom as Salle
            FROM exam_schedule_optimized s
            JOIN examens e ON s.exam_id = e.id
            JOIN modules m ON e.module_id = m.id
            JOIN lieux_examen l ON s.salle_id = l.id
            WHERE m.formation_id = {fid}
            ORDER BY s.date_exam, s.time_slot
            """
            df = pd.read_sql(q, conn)
            if not df.empty:
                if pd.api.types.is_numeric_dtype(df['time_slot']): df['time_slot'] = df['time_slot'].apply(format_slot)
                st.dataframe(df, hide_index=True)
            else:
                st.info("Planning vide pour cette formation.")

    conn.close()

# ----------------- MAIN ROUTER -----------------
display_header()

# Sidebar Role Selection matches user request
roles = ["Administrateur", "Vice-Doyen", "Chef de Département", "Etudiant/Prof (Public)"]
st.sidebar.title("🔐 Rôle")
role = st.sidebar.radio("Navigation", roles)

if role == "Administrateur":
    view_admin()
elif role == "Vice-Doyen":
    view_vice_dean()
elif role == "Chef de Département":
    view_dept_head()
elif role == "Etudiant/Prof (Public)":
    view_public_consultation()
