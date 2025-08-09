#!/usr/bin/env python3
"""
Script générique pour créer les tables à partir du fichier CSV
Exécuté automatiquement lors du premier lancement de Docker
"""

import csv
import os
import sys
import time
from pathlib import Path

# Ajouter le répertoire backend au path
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from sqlalchemy import create_engine, text
from config.database.database import DATABASE_URL

# Convertir l'URL async en URL sync pour SQLAlchemy
def get_sync_database_url():
    """Convertit l'URL async en URL sync pour SQLAlchemy"""
    async_url = DATABASE_URL
    # Remplacer asyncpg par psycopg2 pour les connexions sync
    sync_url = async_url.replace('postgresql+asyncpg://', 'postgresql://')
    return sync_url

def wait_for_database():
    """Attend que la base de données soit disponible"""
    print("⏳ Attente de la base de données...")
    
    max_attempts = 60  # Augmenter le nombre de tentatives
    attempt = 0
    
    while attempt < max_attempts:
        try:
            sync_url = get_sync_database_url()
            print(f"🔍 Tentative de connexion avec : {sync_url}")
            engine = create_engine(sync_url, echo=False)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                print("✅ Base de données disponible !")
                return True
        except Exception as e:
            attempt += 1
            print(f"⏳ Tentative {attempt}/{max_attempts} - Base de données non disponible... (Erreur: {e})")
            time.sleep(3)  # Augmenter le délai entre les tentatives
    
    print("❌ Impossible de se connecter à la base de données")
    return False

def clean_column_name(column_name):
    """Nettoie le nom de colonne des caractères invisibles"""
    if column_name:
        # Supprimer le BOM et autres caractères invisibles
        return column_name.strip().replace('\ufeff', '').replace('\u200b', '')
    return column_name

def read_csv_file():
    """Lit le fichier CSV et retourne les données des tables"""
    csv_path = Path(__file__).parent / "DBTABLES.csv"
    
    if not csv_path.exists():
        print(f"❌ Fichier CSV non trouvé : {csv_path}")
        return None
    
    print(f"✅ Fichier CSV trouvé : {csv_path}")
    
    tables = {}
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as file:  # utf-8-sig gère le BOM
            reader = csv.DictReader(file)
            print(f"📋 Colonnes détectées : {list(reader.fieldnames)}")
            
            for row_num, row in enumerate(reader, 1):
                # Nettoyer les noms de colonnes
                table_col = clean_column_name(row.get('Table', ''))
                colonne_col = clean_column_name(row.get('Colonne', ''))
                
                # Ignorer les lignes vides ou avec des colonnes vides
                if not table_col or not colonne_col:
                    print(f"⏭️ Ligne {row_num} ignorée (colonne vide)")
                    continue
                    
                table_name = table_col.strip()
                if table_name not in tables:
                    tables[table_name] = []
                
                tables[table_name].append({
                    'column': colonne_col.strip(),
                    'description': clean_column_name(row.get('Description', '')).strip(),
                    'possible_values': clean_column_name(row.get('Valeurs Possibles', '')).strip(),
                    'primary_key': clean_column_name(row.get('Clé Primaire', '')).strip() == 'TRUE',
                    'foreign_key': clean_column_name(row.get('Clé Etrangère', '')).strip() == 'TRUE',
                    'format': clean_column_name(row.get('Format', '')).strip() or 'VARCHAR(255)',
                    'table_type': clean_column_name(row.get('Type Table', '')).strip() or 'REFERENCE'
                })
                
                if row_num % 10 == 0:  # Log tous les 10 lignes
                    print(f"📝 Traitement ligne {row_num} - Table: {table_name}, Colonne: {row['Colonne'].strip()}")
        
        print(f"✅ {len(tables)} tables trouvées dans le CSV")
        return tables
        
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du CSV : {e}")
        return None

def convert_format_to_sql_type(format_str: str) -> str:
    """Convertit le format en type SQL PostgreSQL"""
    format_mapping = {
        'SERIAL': 'SERIAL',
        'INT': 'INTEGER',
        'VARCHAR(10)': 'VARCHAR(10)',
        'VARCHAR(20)': 'VARCHAR(20)',
        'VARCHAR(50)': 'VARCHAR(50)',
        'VARCHAR(100)': 'VARCHAR(100)',
        'VARCHAR(255)': 'VARCHAR(255)',
        'TEXT': 'TEXT',
        'DATE': 'DATE',
        'TIMESTAMP': 'TIMESTAMP',
        'BOOLEAN': 'BOOLEAN',
        'NUMERIC(15,2)': 'NUMERIC(15,2)',
        'NUMERIC(12,2)': 'NUMERIC(12,2)',
        'NUMERIC(10,2)': 'NUMERIC(10,2)',
        'NUMERIC(5,4)': 'NUMERIC(5,4)',
        'DECIMAL(12,2)': 'DECIMAL(12,2)',
        'DECIMAL(4,2)': 'DECIMAL(4,2)'
    }
    
    return format_mapping.get(format_str, 'VARCHAR(255)')

def get_referenced_table_and_key(column_name: str) -> tuple:
    """Détermine la table référencée et sa clé primaire"""
    column_mapping = {
        # Clés primaires standard (id)
        'idUser': ('users', 'id'),
        'idProfile': ('profiles', 'id'),
        'idProduit': ('produits', 'id'),
        'idGarantie': ('garanties', 'id'),
        'idSousGarantie': ('sous_garanties', 'id'),
        'idBranche': ('branches', 'id'),
        'idUsage': ('usage', 'id'),
        'idAvenant': ('avenant', 'id'),
        'idSousTypeAvenant': ('avenant_soustype', 'id'),
        'idCIE': ('compagnies', 'id'),
        'idQuittance': ('quittance', 'id'),
        'idProduction': ('production', 'id'),
        'idSinistre': ('sinistre', 'id'),
        'idCommission': ('commission', 'id'),
        'idTaxes': ('taxe', 'id'),
        'idPaiement': ('paiement', 'id'),
        'idRDV': ('rdv', 'id'),
        'idDocType': ('document_type', 'id'),
        'idCommissionType': ('commission_type', 'id'),
        
        # Clés primaires personnalisées
        'idClient': ('clients', 'id'),  # clients a 'id' comme PK
        'idEntite': ('clients', 'id'),  # clients a 'id' comme PK
        'societeMere': ('societes', 'idClient'),  # societes a 'idClient' comme PK
        'idDroit': ('droits', 'id'),  # droits a 'id' comme PK
        
        # Références par code (pas par id)
        'codeGarantie': ('garanties', 'codeGarantie'),  # Référence par code
        'codeSousGarantie': ('sous_garanties', 'codeSousGarantie'),  # Référence par code
        'codeBranche': ('branches', 'codeBranche'),  # Référence par code
        'codeProduit': ('produits', 'codeProduit'),  # Référence par code
        'codeUsage': ('usage', 'codeUsage'),  # Référence par code
        'codeAvenant': ('avenant', 'codeAvenant'),  # Référence par code
        'codeQuittance': ('quittance', 'codeQuittance'),  # Référence par code
        'codeDocType': ('document_type', 'codeDocType'),  # Référence par code
    }
    
    return column_mapping.get(column_name, ('clients', 'id'))

def generate_create_table_sql(table_name: str, columns: list, skip_foreign_keys: bool = False) -> str:
    """Génère le SQL de création de table"""
    
    sql_parts = [f"CREATE TABLE IF NOT EXISTS {table_name} ("]
    
    # Identifier les colonnes de clé primaire
    primary_keys = [col['column'] for col in columns if col['primary_key']]
    
    for i, col in enumerate(columns):
        column_name = col['column']
        format_str = col['format']
        is_primary = col['primary_key']
        is_foreign = col['foreign_key']
        
        # Convertir le format en type SQL
        sql_type = convert_format_to_sql_type(format_str)
        
        # Construire la ligne de colonne
        column_def = f"    {column_name} {sql_type}"
        
        # Gérer les clés primaires et étrangères
        if is_primary and is_foreign:
            # Clé primaire + étrangère (ex: particuliers.idClient)
            if len(primary_keys) == 1:
                column_def += " PRIMARY KEY"
            if not skip_foreign_keys:
                referenced_table, primary_key = get_referenced_table_and_key(column_name)
                column_def += f" REFERENCES {referenced_table}({primary_key})"
        elif is_primary:
            # Clé primaire simple
            if len(primary_keys) == 1:
                column_def += " PRIMARY KEY"
            # Sinon, on gère la clé composite à la fin
        elif is_foreign and not skip_foreign_keys:
            # Clé étrangère simple
            referenced_table, primary_key = get_referenced_table_and_key(column_name)
            column_def += f" REFERENCES {referenced_table}({primary_key})"
        
        # Ajouter une virgule si ce n'est pas la dernière colonne OU s'il y a une clé composite
        if i < len(columns) - 1 or len(primary_keys) > 1:
            column_def += ","
        
        sql_parts.append(column_def)
    
    # Ajouter la clé primaire composite si nécessaire
    if len(primary_keys) > 1:
        sql_parts.append(f"    PRIMARY KEY ({', '.join(primary_keys)})")
    elif len(primary_keys) == 1:
        # La clé primaire simple est déjà ajoutée dans la colonne
        pass
    
    sql_parts.append(");")
    
    return "\n".join(sql_parts)

def analyze_dependencies(tables):
    """Analyse les dépendances entre les tables"""
    dependencies = {}
    
    for table_name, columns in tables.items():
        dependencies[table_name] = set()
        for col in columns:
            if col['foreign_key']:
                referenced_table, _ = get_referenced_table_and_key(col['column'])
                if referenced_table != table_name:  # Éviter les auto-références
                    dependencies[table_name].add(referenced_table)
                    print(f"🔗 {table_name}.{col['column']} → {referenced_table}")
    
    return dependencies

def get_creation_order(tables):
    """Détermine l'ordre de création basé sur les dépendances"""
    dependencies = analyze_dependencies(tables)
    created = set()
    order = []
    
    while len(created) < len(tables):
        for table_name in tables:
            if table_name not in created:
                # Vérifier si toutes les dépendances sont créées
                if dependencies[table_name].issubset(created):
                    order.append(table_name)
                    created.add(table_name)
        
        # Si aucun progrès, il y a une dépendance circulaire
        if len(created) == len(order):
            # Ajouter les tables restantes
            for table_name in tables:
                if table_name not in created:
                    order.append(table_name)
                    created.add(table_name)
            break
    
    return order

def create_tables(tables):
    """Crée toutes les tables dans la base de données"""
    print("📝 Création des tables...")
    
    try:
        sync_url = get_sync_database_url()
        engine = create_engine(sync_url, echo=False)
        
        # Déterminer l'ordre de création automatiquement
        table_order = get_creation_order(tables)
        print(f"📋 Ordre de création : {table_order}")
        
        # Ordre manuel pour les tables critiques (en cas de problème avec l'ordre automatique)
        manual_order = [
            # Tables MASTER (sans dépendances)
            'compagnies', 'clients', 'particuliers', 'societes', 
            'users', 'infos', 'avenant', 'quittance', 'document_type',
            
            # Tables REFERENCE (sans dépendances)
            'branches', 'garanties', 'sous_garanties', 'produits',
            'commission_type', 'commission_taux', 'commission_plage', 'commission_forfait',
            'taxe', 'usage', 'rdv', 'droits', 'profiles', 'refProfiles',
            'marques', 'carrosseries', 'villes', 'banques', 'bonus_auto', 'paiement',
            
            # Tables avec dépendances
            'commission', 'documents',
            
            # Tables TRANSACTIONAL
            'devis', 'production', 'sinistre', 'sinistre_vue',
            'attestation', 'reglement', 'agenda', 'userProfiles', 'avenant_soustype'
        ]
        
        # Filtrer pour ne garder que les tables qui existent
        table_order = [table for table in manual_order if table in tables]
        print(f"📋 Ordre de création (manuel) : {table_order}")
        
        created_tables = []
        
        # Première passe : créer toutes les tables sans clés étrangères
        print("📝 Première passe : création des tables sans clés étrangères...")
        for table_name in table_order:
            if table_name in tables:
                columns = tables[table_name]
                print(f"✅ Création de la table : {table_name}")
                
                # Générer le SQL de création de table sans clés étrangères
                create_table_sql = generate_create_table_sql(table_name, columns, skip_foreign_keys=True)
                
                # Exécuter la création
                with engine.connect() as connection:
                    connection.execute(text(create_table_sql))
                    connection.commit()
                
                created_tables.append(table_name)
        
        # Deuxième passe : ajouter les clés étrangères
        print("📝 Deuxième passe : ajout des clés étrangères...")
        for table_name in table_order:
            if table_name in tables:
                columns = tables[table_name]
                foreign_keys = [col for col in columns if col['foreign_key']]
                
                if foreign_keys:
                    print(f"🔗 Ajout des clés étrangères pour : {table_name}")
                    
                    for col in foreign_keys:
                        referenced_table, primary_key = get_referenced_table_and_key(col['column'])
                        add_fk_sql = f"ALTER TABLE {table_name} ADD CONSTRAINT fk_{table_name}_{col['column']} FOREIGN KEY ({col['column']}) REFERENCES {referenced_table}({primary_key});"
                        
                        try:
                            with engine.connect() as connection:
                                connection.execute(text(add_fk_sql))
                                connection.commit()
                            print(f"  ✅ Ajouté : {col['column']} → {referenced_table}({primary_key})")
                        except Exception as e:
                            print(f"  ⚠️ Erreur ajout FK {col['column']}: {e}")
        
        print(f"✅ {len(created_tables)} tables créées avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables : {e}")
        return False

def insert_initial_data():
    """Insère des données initiales dans les tables de référence"""
    print("📝 Insertion de données initiales...")
    
    try:
        sync_url = get_sync_database_url()
        engine = create_engine(sync_url, echo=False)
        
        # Données initiales
        initial_data = [
            # Branches d'assurance
            ("INSERT INTO branches (codeBranche, libelle) VALUES ('AUTO', 'Assurance Automobile') ON CONFLICT DO NOTHING;"),
            ("INSERT INTO branches (codeBranche, libelle) VALUES ('HAB', 'Assurance Habitation') ON CONFLICT DO NOTHING;"),
            ("INSERT INTO branches (codeBranche, libelle) VALUES ('PRO', 'Assurance Professionnelle') ON CONFLICT DO NOTHING;"),
            
            # Villes
            ("INSERT INTO villes (codeVille, libelle) VALUES ('RABAT', 'Rabat') ON CONFLICT DO NOTHING;"),
            ("INSERT INTO villes (codeVille, libelle) VALUES ('CASA', 'Casablanca') ON CONFLICT DO NOTHING;"),
            ("INSERT INTO villes (codeVille, libelle) VALUES ('FES', 'Fès') ON CONFLICT DO NOTHING;"),
            
            # Marques
            ("INSERT INTO marques (codeMarques, libelle) VALUES ('MERCEDES', 'Mercedes') ON CONFLICT DO NOTHING;"),
            ("INSERT INTO marques (codeMarques, libelle) VALUES ('BMW', 'BMW') ON CONFLICT DO NOTHING;"),
            ("INSERT INTO marques (codeMarques, libelle) VALUES ('AUDI', 'Audi') ON CONFLICT DO NOTHING;"),
            
            # Carrosseries
            ("INSERT INTO carrosseries (codeCarrosseries, libelle) VALUES ('BERLINE', 'Berline') ON CONFLICT DO NOTHING;"),
            ("INSERT INTO carrosseries (codeCarrosseries, libelle) VALUES ('SUV', 'SUV') ON CONFLICT DO NOTHING;"),
            ("INSERT INTO carrosseries (codeCarrosseries, libelle) VALUES ('BREAK', 'Break') ON CONFLICT DO NOTHING;"),
            
            # Banques
            ("INSERT INTO banques (codeBanques, libelle) VALUES ('BMCE', 'BMCE') ON CONFLICT DO NOTHING;"),
            ("INSERT INTO banques (codeBanques, libelle) VALUES ('CIH', 'CIH') ON CONFLICT DO NOTHING;"),
            ("INSERT INTO banques (codeBanques, libelle) VALUES ('ATW', 'Attijariwafa Bank') ON CONFLICT DO NOTHING;"),
            
            # Modes de paiement
            ("INSERT INTO paiement (codePaiement, libelle) VALUES ('VIREMENT', 'Virement bancaire') ON CONFLICT DO NOTHING;"),
            ("INSERT INTO paiement (codePaiement, libelle) VALUES ('CHEQUE', 'Chèque') ON CONFLICT DO NOTHING;"),
            ("INSERT INTO paiement (codePaiement, libelle) VALUES ('ESPECES', 'Espèces') ON CONFLICT DO NOTHING;"),
        ]
        
        with engine.connect() as connection:
            for sql in initial_data:
                connection.execute(text(sql))
            connection.commit()
        
        print("✅ Données initiales insérées !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion des données : {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Initialisation de la base de données")
    print("=" * 50)
    
    # Attendre que la base de données soit disponible
    if not wait_for_database():
        return False
    
    # Lire le fichier CSV
    tables = read_csv_file()
    if not tables:
        return False
    
    # Créer les tables
    if not create_tables(tables):
        return False
    
    # Insérer les données initiales
    if not insert_initial_data():
        return False
    
    print("\n🎉 Initialisation terminée avec succès !")
    print("✅ Base de données prête pour l'application")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 