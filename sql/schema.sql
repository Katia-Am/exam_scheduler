CREATE TABLE departements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;


CREATE TABLE formations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    dept_id INT NOT NULL,
    nb_modules INT NOT NULL,
    CONSTRAINT fk_formation_dept
        FOREIGN KEY (dept_id) REFERENCES departements(id)
) ENGINE=InnoDB;


CREATE TABLE etudiants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    formation_id INT NOT NULL,
    promo INT,
    CONSTRAINT fk_etudiant_formation
        FOREIGN KEY (formation_id) REFERENCES formations(id)
) ENGINE=InnoDB;


CREATE TABLE professeurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    dept_id INT NOT NULL,
    specialite VARCHAR(100),
    CONSTRAINT fk_prof_dept
        FOREIGN KEY (dept_id) REFERENCES departements(id)
) ENGINE=InnoDB;


CREATE TABLE modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    credits INT,
    formation_id INT NOT NULL,
    pre_req_id INT,
    CONSTRAINT fk_module_formation
        FOREIGN KEY (formation_id) REFERENCES formations(id),
    CONSTRAINT fk_module_prereq
        FOREIGN KEY (pre_req_id) REFERENCES modules(id)
) ENGINE=InnoDB;


CREATE TABLE lieux_examen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    capacite INT NOT NULL,
    type ENUM('salle','amphi') NOT NULL,
    batiment VARCHAR(50)
) ENGINE=InnoDB;


CREATE TABLE inscriptions (
    etudiant_id INT NOT NULL,
    module_id INT NOT NULL,
    note DECIMAL(4,2),
    PRIMARY KEY (etudiant_id, module_id),
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (module_id) REFERENCES modules(id)
) ENGINE=InnoDB;


--table examen pour les données initiales (avant optimisation)
CREATE TABLE examens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module_id INT NOT NULL,
    prof_id INT NOT NULL,
    salle_id INT NOT NULL,
    date_heure DATETIME NOT NULL,
    duree_minutes INT NOT NULL,
    FOREIGN KEY (module_id) REFERENCES modules(id),
    FOREIGN KEY (prof_id) REFERENCES professeurs(id),
    FOREIGN KEY (salle_id) REFERENCES lieux_examen(id)
) ENGINE=InnoDB;


CREATE INDEX idx_exam_date ON examens(date_heure);
CREATE INDEX idx_exam_prof ON examens(prof_id);
CREATE INDEX idx_exam_salle ON examens(salle_id);
CREATE INDEX idx_inscription_module ON inscriptions(module_id);


-- on a ajouter une table exam_schedule pour le résultat de l’algorithme (EDT généré / optimisé)
CREATE TABLE exam_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    date_exam DATE NOT NULL,
    time_slot INT NOT NULL,
    salle_id INT NOT NULL,
    prof_id INT NOT NULL,

    CONSTRAINT fk_sched_exam
        FOREIGN KEY (exam_id) REFERENCES examens(id),
    CONSTRAINT fk_sched_salle
        FOREIGN KEY (salle_id) REFERENCES lieux_examen(id),
    CONSTRAINT fk_sched_prof
        FOREIGN KEY (prof_id) REFERENCES professeurs(id)
) ENGINE=InnoDB;

CREATE INDEX idx_sched_date ON exam_schedule(date_exam);
CREATE INDEX idx_sched_prof ON exam_schedule(prof_id);
CREATE INDEX idx_sched_salle ON exam_schedule(salle_id);
