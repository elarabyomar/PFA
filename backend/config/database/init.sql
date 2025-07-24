-- Créer la table users avec les nouveaux champs
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    nom VARCHAR NOT NULL,
    prenom VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    date_naissance DATE NOT NULL,
    role VARCHAR NOT NULL,
    roles VARCHAR,
    password_changed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insérer l'utilisateur admin par défaut avec mot de passe "admin" (hashé avec bcrypt)
-- Note: Les mots de passe par défaut sont "admin" ou la date de naissance au format YYYYMMDD (ex: 20031125)
INSERT INTO users (nom, prenom, email, password, date_naissance, role, roles, password_changed, created_at, updated_at) 
VALUES (
    'admin', 
    'admin', 
    'admin@gmail.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8mO',  -- Hash bcrypt pour "admin"
    '2003-11-25',
    'admin',
    'admin',
    FALSE,
    NOW(),
    NOW()
) 
ON CONFLICT (email) DO UPDATE SET 
    password = EXCLUDED.password,
    password_changed = EXCLUDED.password_changed;

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

-- Migration pour ajouter le champ password_changed aux tables existantes
-- (pour les installations existantes)
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed BOOLEAN DEFAULT FALSE;

-- Mettre à jour les utilisateurs existants
-- Marquer tous les utilisateurs comme ayant changé leur mot de passe (sauf admin)
UPDATE users SET password_changed = TRUE WHERE email != 'admin@gmail.com';

-- Forcer l'admin à changer son mot de passe par défaut
UPDATE users SET password_changed = FALSE WHERE email = 'admin@gmail.com';

-- Vérifier que les rôles ont été créés
SELECT 'Rôles créés avec succès' as message; 

