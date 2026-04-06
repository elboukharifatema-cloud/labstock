-- Données de démonstration

-- Catégories
INSERT INTO categories (name, description, color) VALUES
('Hématologie', 'Réactifs pour analyses sanguines', '#EF4444'),
('Biochimie', 'Réactifs biochimiques et enzymes', '#3B82F6'),
('Microbiologie', 'Milieux de culture et réactifs microbio', '#10B981'),
('Immunologie', 'Anticorps et réactifs immunologiques', '#8B5CF6'),
('Consommables', 'Tubes, pipettes, gants et matériel jetable', '#F59E0B');

-- Fournisseurs
INSERT INTO suppliers (name, contact_person, phone, email, address) VALUES
('BioMérieux Algérie', 'Ahmed Benali', '+213 21 45 67 89', 'a.benali@biomerieux.dz', '12 Rue des Sciences, Alger'),
('Sigma-Aldrich DZ', 'Fatima Hadj', '+213 23 12 34 56', 'f.hadj@sigma.dz', '45 Zone Industrielle, Oran'),
('MedLab Supply', 'Karim Meziane', '+213 25 98 76 54', 'k.meziane@medlab.dz', '8 Av. Pasteur, Constantine');

-- Produits
INSERT INTO products (name, reference, category_id, supplier_id, unit, quantity, min_threshold, location, expiry_date, notes) VALUES
('Hémoglobine A1c Kit', 'HEM-A1C-001', 1, 1, 'kit', 12, 5, 'Frigo A - Étagère 2', '2025-08-15', 'Conserver entre 2-8°C'),
('Réactif CBC - NFS', 'HEM-CBC-002', 1, 1, 'flacon', 8, 10, 'Frigo A - Étagère 1', '2025-06-30', 'Agiter avant utilisation'),
('Glucose Liquicolor', 'BIO-GLU-001', 2, 2, 'kit', 3, 5, 'Armoire B - Étagère 3', '2025-09-20', NULL),
('Créatinine Jaffe', 'BIO-CRE-002', 2, 2, 'kit', 15, 5, 'Armoire B - Étagère 2', '2025-12-10', NULL),
('Cholestérol Total', 'BIO-CHO-003', 2, 2, 'kit', 7, 5, 'Armoire B - Étagère 1', '2025-10-05', NULL),
('Gélose Columbia', 'MIC-GEL-001', 3, 1, 'boîte', 0, 10, 'Frigo C - Étagère 1', '2025-07-20', 'Stocker à 4°C'),
('Mueller Hinton Agar', 'MIC-MHA-002', 3, 1, 'sachet', 20, 8, 'Étagère sèche D-1', '2026-01-15', NULL),
('Anti-HBS Anticorps', 'IMM-HBS-001', 4, 3, 'kit', 4, 5, 'Frigo A - Étagère 3', '2025-11-30', 'Ne pas congeler'),
('ELISA HIV 1+2', 'IMM-HIV-002', 4, 3, 'kit', 2, 3, 'Frigo A - Étagère 4', '2025-08-01', 'Urgent: faible stock'),
('Tubes EDTA 4mL', 'CON-TUB-001', 5, 2, 'boîte', 45, 20, 'Stock général E-1', NULL, '100 tubes/boîte'),
('Pipettes Pasteur', 'CON-PIP-002', 5, 2, 'paquet', 30, 15, 'Stock général E-2', NULL, '500/paquet'),
('Gants Nitrile M', 'CON-GAN-003', 5, 2, 'boîte', 12, 10, 'Stock général E-3', NULL, '100 paires/boîte'),
('Lames à microscope', 'CON-LAM-004', 5, 3, 'boîte', 5, 8, 'Stock général E-4', NULL, '72 lames/boîte'),
('Transaminases ASAT', 'BIO-ASA-004', 2, 2, 'kit', 9, 5, 'Armoire B - Étagère 4', '2025-11-15', NULL),
('Bilirubine Totale', 'BIO-BIL-005', 2, 1, 'kit', 6, 5, 'Armoire B - Étagère 5', '2025-10-20', NULL);

-- Mouvements historiques (sans déclencher les triggers sur la quantité initiale)
INSERT INTO movements (product_id, movement_type, quantity, reason, user_name, movement_date) VALUES
(1, 'entry', 20, 'Commande fournisseur', 'Dr. Meriem', datetime('now', '-30 days')),
(1, 'exit', 8, 'Utilisation analyses', 'Tech. Samir', datetime('now', '-15 days')),
(2, 'entry', 15, 'Commande fournisseur', 'Dr. Meriem', datetime('now', '-25 days')),
(2, 'exit', 7, 'Utilisation analyses', 'Tech. Samir', datetime('now', '-10 days')),
(3, 'entry', 10, 'Commande fournisseur', 'Admin', datetime('now', '-20 days')),
(3, 'exit', 7, 'Utilisation analyses', 'Tech. Leila', datetime('now', '-5 days')),
(4, 'entry', 20, 'Commande fournisseur', 'Admin', datetime('now', '-35 days')),
(4, 'exit', 5, 'Utilisation analyses', 'Tech. Samir', datetime('now', '-12 days')),
(5, 'entry', 10, 'Commande fournisseur', 'Dr. Meriem', datetime('now', '-18 days')),
(5, 'exit', 3, 'Utilisation analyses', 'Tech. Leila', datetime('now', '-3 days')),
(8, 'entry', 10, 'Commande fournisseur', 'Admin', datetime('now', '-40 days')),
(8, 'exit', 6, 'Utilisation analyses', 'Tech. Samir', datetime('now', '-8 days')),
(9, 'entry', 5, 'Commande urgente', 'Dr. Meriem', datetime('now', '-15 days')),
(9, 'exit', 3, 'Utilisation analyses', 'Tech. Leila', datetime('now', '-2 days')),
(10, 'entry', 50, 'Commande fournisseur', 'Admin', datetime('now', '-60 days')),
(10, 'exit', 5, 'Utilisation quotidienne', 'Tech. Samir', datetime('now', '-1 days')),
(6, 'entry', 15, 'Commande fournisseur', 'Admin', datetime('now', '-45 days')),
(6, 'exit', 15, 'Utilisation analyses', 'Tech. Leila', datetime('now', '-5 days'));
