
-- Résumé des requetes qu'on a utilisé dans le Dashboard : 

-- KPI
SELECT COUNT(*) AS nb_departements FROM departements;
SELECT COUNT(*) AS nb_formations FROM formations;
SELECT COUNT(*) AS nb_etudiants FROM etudiants;
SELECT COUNT(*) AS nb_examens FROM examens;

-- Conflits étudiants
SELECT e1.etudiant_id, DATE(ex.date_heure) AS jour, COUNT(*) AS nb_examens
FROM inscriptions e1
JOIN examens ex ON e1.module_id = ex.module_id
GROUP BY e1.etudiant_id, DATE(ex.date_heure)
HAVING nb_examens > 1;

-- Conflits professeurs
SELECT prof_id, DATE(date_heure) AS jour, COUNT(*) AS nb_examens
FROM examens
GROUP BY prof_id, DATE(date_heure)
HAVING nb_examens > 3;

-- Conflits salles
SELECT salle_id, date_heure, COUNT(*) AS nb
FROM examens
GROUP BY salle_id, date_heure
HAVING nb > 1;

-- Filtres
SELECT id, nom FROM departements;
SELECT id, nom FROM formations WHERE dept_id = ?;

-- Planning des examens
SELECT
  e.id,
  m.nom AS module,
  f.nom AS formation,
  d.nom AS departement,
  p.nom AS professeur,
  l.nom AS salle,
  e.date_heure
FROM examens e
JOIN modules m ON e.module_id = m.id
JOIN formations f ON m.formation_id = f.id
JOIN departements d ON f.dept_id = d.id
JOIN professeurs p ON e.prof_id = p.id
JOIN lieux_examen l ON e.salle_id = l.id;
