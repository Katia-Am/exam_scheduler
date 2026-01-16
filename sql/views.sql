--Vues pour Streamlit
--Vue de lecture des planning global(ancien script) 
CREATE VIEW v_exam_schedule AS
SELECT
    e.id,
    m.nom AS module,
    f.nom AS formation,
    d.nom AS departement,
    p.nom AS professeur,
    l.nom AS salle,
    e.date_heure,
    e.duree_minutes
FROM examens e
JOIN modules m ON e.module_id = m.id
JOIN formations f ON m.formation_id = f.id
JOIN departements d ON f.dept_id = d.id
JOIN professeurs p ON e.prof_id = p.id
JOIN lieux_examen l ON e.salle_id = l.id;

-- Vue de lecture des planning global utilisé : on a remplacer le script en haut  par celui la , a cause de l'ajout de la table examen_scheduel 
CREATE OR REPLACE VIEW v_exam_schedule AS
SELECT
    es.id AS schedule_id,
    d.nom AS departement,
    f.nom AS formation,
    m.nom AS module,
    p.nom AS professeur,
    l.nom AS salle,
    es.date_exam,
    es.time_slot
FROM exam_schedule es
JOIN examens e ON es.exam_id = e.id
JOIN modules m ON e.module_id = m.id
JOIN formations f ON m.formation_id = f.id
JOIN departements d ON f.dept_id = d.id
JOIN professeurs p ON es.prof_id = p.id
JOIN lieux_examen l ON es.salle_id = l.id;



-- Vue de détection des conflits étudiants 
CREATE VIEW v_student_conflicts AS
SELECT etudiant_id, jour, nb_examens
FROM (
    SELECT e.id AS etudiant_id,
           DATE(ex.date_heure) AS jour,
           COUNT(*) AS nb_examens
    FROM inscriptions i
    JOIN examens ex ON i.module_id = ex.module_id
    JOIN etudiants e ON i.etudiant_id = e.id
    GROUP BY e.id, DATE(ex.date_heure)
) t
WHERE nb_examens > 1;
