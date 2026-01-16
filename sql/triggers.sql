DELIMITER $$

-- Empêcher prof > 3 examens / jour
CREATE TRIGGER trg_prof_exam_limit
BEFORE INSERT ON examens
FOR EACH ROW
BEGIN
    DECLARE nb INT;

    SELECT COUNT(*) INTO nb
    FROM examens
    WHERE prof_id = NEW.prof_id
      AND DATE(date_heure) = DATE(NEW.date_heure);

    IF nb >= 3 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Professeur déjà assigné à 3 examens ce jour';
    END IF;
END$$

DELIMITER ;
