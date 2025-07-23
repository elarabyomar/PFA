-- Créer la table users avec les nouveaux champs
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    nom VARCHAR NOT NULL,
    prenom VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    date_naissance DATE NOT NULL,
    role VARCHAR NOT NULL
);

-- Insérer l'utilisateur admin par défaut
INSERT INTO users (nom, prenom, email, password, date_naissance, role) 
VALUES (
    'omar', 
    'elaraby', 
    'admin@gmail.com', 
    '$2b$12$CKQs0OA0wWxhglZFzVU/MeXxeTsOGlSlVOeq1ci51n0XPGjGiUPy.', 
    '2003-11-25',
    'admin'
) 
ON CONFLICT (email) DO NOTHING;

-- Créer la table roles (sans contrainte de clé étrangère pour l'instant)
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_by INTEGER,  -- Temporairement sans REFERENCES
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insérer les rôles par défaut
INSERT INTO roles (name, description, created_by) VALUES
('admin', 'Super administrateur avec tous les droits', 1),
('user', 'Utilisateur standard', 1)
ON CONFLICT (name) DO NOTHING;

-- Vérifier que les rôles ont été créés
SELECT 'Rôles créés avec succès' as message; 

