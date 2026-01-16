CREATE INDEX idx_exam_date_prof ON examens(date_heure, prof_id);
CREATE INDEX idx_exam_salle_date ON examens(salle_id, date_heure);
CREATE INDEX idx_inscription_etudiant ON inscriptions(etudiant_id);
CREATE INDEX idx_module_formation ON modules(formation_id);
