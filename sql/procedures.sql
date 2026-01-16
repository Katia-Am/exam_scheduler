DELIMITER $$


-- 1. Conflits étudiants (2 examens même jour)
CREATE PROCEDURE detect_student_conflicts()
BEGIN
    SELECT e.id AS etudiant_id,
           DATE(ex.date_heure) AS jour,
           COUNT(*) AS nb_examens
    FROM inscriptions i
    JOIN examens ex ON i.module_id = ex.module_id
    JOIN etudiants e ON i.etudiant_id = e.id
    GROUP BY e.id, DATE(ex.date_heure)
    HAVING COUNT(*) > 1;
END$$



-- 2. Professeurs > 3 examens / jour
CREATE PROCEDURE detect_prof_overload()
BEGIN
    SELECT p.id AS prof_id,
           DATE(e.date_heure) AS jour,
           COUNT(*) AS nb_examens
    FROM examens e
    JOIN professeurs p ON e.prof_id = p.id
    GROUP BY p.id, DATE(e.date_heure)
    HAVING COUNT(*) > 3;
END$$



-- 3. Occupation salles
CREATE PROCEDURE salle_occupation()
BEGIN
    SELECT l.nom,
           COUNT(e.id) AS nb_examens
    FROM lieux_examen l
    LEFT JOIN examens e ON l.id = e.salle_id
    GROUP BY l.id;
END$$



-- 4. Charge de surveillance professeurs
CREATE PROCEDURE prof_exam_load()
BEGIN
    SELECT p.nom,
           COUNT(e.id) AS total_examens
    FROM professeurs p
    LEFT JOIN examens e ON p.id = e.prof_id
    GROUP BY p.id;
END$$

DELIMITER ;
