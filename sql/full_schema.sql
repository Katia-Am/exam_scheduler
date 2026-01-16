-- Tables de base (existantes, rappel)
CREATE TABLE IF NOT EXISTS departements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS formations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    dept_id INT NOT NULL,
    nb_modules INT NOT NULL,
    FOREIGN KEY (dept_id) REFERENCES departements(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS etudiants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    formation_id INT NOT NULL,
    promo INT,
    FOREIGN KEY (formation_id) REFERENCES formations(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    credits INT,
    formation_id INT NOT NULL,
    pre_req_id INT,
    FOREIGN KEY (formation_id) REFERENCES formations(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS lieux_examen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    capacite INT NOT NULL,
    type ENUM('salle','amphi') NOT NULL,
    batiment VARCHAR(50)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS professeurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    dept_id INT NOT NULL,
    specialite VARCHAR(100),
    FOREIGN KEY (dept_id) REFERENCES departements(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS inscriptions (
    etudiant_id INT NOT NULL,
    module_id INT NOT NULL,
    note DECIMAL(4,2),
    PRIMARY KEY (etudiant_id, module_id),
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (module_id) REFERENCES modules(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS examens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module_id INT NOT NULL,
    prof_id INT NOT NULL,
    salle_id INT NOT NULL,
    date_heure DATETIME, -- Peut etre NULL si pas encore planifie
    duree_minutes INT NOT NULL,
    FOREIGN KEY (module_id) REFERENCES modules(id),
    FOREIGN KEY (prof_id) REFERENCES professeurs(id),
    FOREIGN KEY (salle_id) REFERENCES lieux_examen(id)
) ENGINE=InnoDB;

-- Tables pour les résultats
-- 1. Resultat BRUT (avec conflits)
DROP TABLE IF EXISTS exam_schedule_raw;
CREATE TABLE exam_schedule_raw (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    prof_id INT NOT NULL,
    salle_id INT NOT NULL,
    date_exam DATE NOT NULL,
    time_slot VARCHAR(20) NOT NULL, -- "08:00-10:00"
    FOREIGN KEY (exam_id) REFERENCES examens(id),
    FOREIGN KEY (prof_id) REFERENCES professeurs(id),
    FOREIGN KEY (salle_id) REFERENCES lieux_examen(id)
) ENGINE=InnoDB;

-- 2. Resultat OPTIMISE
DROP TABLE IF EXISTS exam_schedule_optimized;
CREATE TABLE exam_schedule_optimized (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    prof_id INT NOT NULL,
    salle_id INT NOT NULL,
    date_exam DATE NOT NULL,
    time_slot INT NOT NULL, -- 1, 2, 3, 4
    FOREIGN KEY (exam_id) REFERENCES examens(id),
    FOREIGN KEY (prof_id) REFERENCES professeurs(id),
    FOREIGN KEY (salle_id) REFERENCES lieux_examen(id)
) ENGINE=InnoDB;

-- Index pour performance
CREATE INDEX idx_raw_prof ON exam_schedule_raw(prof_id, date_exam, time_slot);
CREATE INDEX idx_raw_salle ON exam_schedule_raw(salle_id, date_exam, time_slot);

CREATE INDEX idx_opt_prof ON exam_schedule_optimized(prof_id, date_exam, time_slot);
CREATE INDEX idx_opt_salle ON exam_schedule_optimized(salle_id, date_exam, time_slot);
