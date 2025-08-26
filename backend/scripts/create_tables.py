#!/usr/bin/env python3
"""
Script pour créer automatiquement toutes les tables de la base de données
à partir du fichier CSV DBTABLES.csv
"""

import asyncio
import sys
import os
import csv
from collections import defaultdict

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database.database import get_session
from sqlalchemy import text

def parse_csv_structure(csv_file_path):
    """Parse le fichier CSV pour extraire la structure des tables"""
    tables = defaultdict(list)
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                table_name = row['Table'].strip()
                column_name = row['Colonne'].strip()
                
                # Ignorer les lignes vides
                if not table_name or not column_name:
                    continue
                
                column_info = {
                    'name': column_name,
                    'display_name': row.get('Libellé Affichage', column_name),  # Utiliser le libellé d'affichage
                    'description': row.get('Description', ''),
                    'values_possibles': row.get('Valeurs Possibles', ''),
                    'primary_key': row.get('Clé Primaire', '').upper() == 'TRUE',
                    'foreign_key': row.get('Clé Etrangère', '').upper() == 'TRUE',
                    'format': row.get('Format', ''),
                    'table_type': row.get('Type Table', 'MASTER')
                }
                
                tables[table_name].append(column_info)
                
    except FileNotFoundError:
        print(f"❌ Fichier CSV non trouvé: {csv_file_path}")
        return {}
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du CSV: {e}")
        return {}
    
    return tables

def generate_create_table_sql(table_name, columns):
    """Génère le SQL CREATE TABLE pour une table donnée"""
    column_definitions = []
    primary_keys = []
    foreign_keys = []
    
    for col in columns:
        col_name = col['name']
        col_display_name = col.get('display_name', col_name)  # Utiliser le libellé d'affichage
        col_format = col['format']
        col_primary = col['primary_key']
        col_foreign = col['foreign_key']
        col_nullable = not col['primary_key']  # Les clés primaires ne peuvent pas être NULL
        
        # Définir le type de données
        if col_format.upper() == 'SERIAL':
            data_type = 'SERIAL'
        elif col_format.upper() == 'INT':
            data_type = 'INTEGER'
        elif col_format.upper().startswith('VARCHAR'):
            data_type = col_format
        elif col_format.upper().startswith('NUMERIC') or col_format.upper().startswith('DECIMAL'):
            data_type = col_format
        elif col_format.upper() == 'DATE':
            data_type = 'DATE'
        elif col_format.upper() == 'TIMESTAMP':
            data_type = 'TIMESTAMP'
        elif col_format.upper() == 'BOOLEAN':
            data_type = 'BOOLEAN'
        elif col_format.upper() == 'TEXT':
            data_type = 'TEXT'
        else:
            # Par défaut, utiliser VARCHAR(255)
            data_type = 'VARCHAR(255)'
        
        # Construire la définition de colonne (sans COMMENT dans CREATE TABLE)
        column_def = f"{col_name} {data_type}"
        
        if not col_nullable:
            column_def += " NOT NULL"
        
        if col_primary:
            primary_keys.append(col_name)
        
        if col_foreign:
            # Ajouter la contrainte de clé étrangère
            foreign_keys.append(col_name)
        
        column_definitions.append(column_def)
    
    # Ajouter la contrainte de clé primaire si nécessaire
    if primary_keys:
        column_definitions.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
    
    # Générer le SQL CREATE TABLE (sans COMMENT)
    separator = ',\n    '
    sql = f"""CREATE TABLE IF NOT EXISTS {table_name} (
    {separator.join(column_definitions)}
)"""
    
    return sql

async def create_tables_from_csv():
    """Crée toutes les tables à partir du fichier CSV"""
    
    # Chemin vers le fichier CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'DBTABLES.csv')
    
    # Parser la structure du CSV
    print("📖 Lecture du fichier CSV DBTABLES.csv...")
    tables_structure = parse_csv_structure(csv_path)
    
    if not tables_structure:
        print("❌ Aucune table trouvée dans le CSV")
        return False
    
    print(f"✅ {len(tables_structure)} tables trouvées dans le CSV")
    
    # Créer les tables dans l'ordre logique (d'abord les tables de référence)
    table_order = ['REFERENCE', 'MASTER', 'TRANSACTIONAL', 'LOG']
    
    async for session in get_session():
        try:
            # Créer les tables par ordre de priorité
            for table_type in table_order:
                for table_name, columns in tables_structure.items():
                    # Vérifier le type de table
                    if not columns or columns[0].get('table_type') != table_type:
                        continue
                    
                    print(f"🔧 Création de la table {table_name} ({table_type})...")
                    
                    # Générer le SQL CREATE TABLE
                    create_sql = generate_create_table_sql(table_name, columns)
                    
                    # Exécuter la création
                    await session.execute(text(create_sql))
                    print(f"  ✅ Table {table_name} créée")
                    
                    # Ajouter les commentaires sur la table et les colonnes
                    try:
                        # Commentaire sur la table (échapper les apostrophes)
                        table_comment = f"Table {table_name} avec libelles d'affichage".replace("'", "''")
                        await session.execute(text(f"COMMENT ON TABLE {table_name} IS '{table_comment}'"))
                        
                        # Commentaires sur les colonnes (échapper les apostrophes)
                        for col in columns:
                            col_name = col['name']
                            display_name = col.get('display_name', col_name)
                            # Échapper les apostrophes en les doublant
                            safe_display_name = display_name.replace("'", "''")
                            col_comment = f"COMMENT ON COLUMN {table_name}.{col_name} IS '{safe_display_name}'"
                            await session.execute(text(col_comment))
                        
                        print(f"  ✅ Commentaires ajoutés pour {table_name}")
                        
                    except Exception as e:
                        print(f"  ⚠️ Impossible d'ajouter les commentaires pour {table_name}: {e}")
                    
                    # Ajouter les contraintes de clés étrangères
                    try:
                        for col in columns:
                            if col['foreign_key']:
                                col_name = col['name']
                                # Déterminer la table référencée basée sur le nom de la colonne
                                referenced_table = None
                                if 'idCIE' in col_name:
                                    referenced_table = 'compagnies'
                                elif 'idUser' in col_name:
                                    referenced_table = 'users'
                                elif 'idClient' in col_name:
                                    referenced_table = 'clients'
                                elif 'idProduit' in col_name:
                                    referenced_table = 'produits'
                                elif 'idMarque' in col_name:
                                    referenced_table = 'marques'
                                elif 'idCarrosserie' in col_name:
                                    referenced_table = 'carrosseries'
                                
                                if referenced_table:
                                    # Créer la contrainte de clé étrangère
                                    fk_sql = f"""
                                        ALTER TABLE {table_name} 
                                        ADD CONSTRAINT fk_{table_name}_{col_name} 
                                        FOREIGN KEY ({col_name}) 
                                        REFERENCES {referenced_table}(id)
                                    """
                                    await session.execute(text(fk_sql))
                                    print(f"  ✅ Clé étrangère {col_name} → {referenced_table}.id créée")
                                else:
                                    print(f"  ⚠️ Impossible de déterminer la table référencée pour {col_name}")
                        
                    except Exception as e:
                        print(f"  ⚠️ Impossible d'ajouter les clés étrangères pour {table_name}: {e}")
            
            
            
            # Créer des vues pour afficher les libellés d'affichage
            print("🔧 Création des vues avec libellés d'affichage...")
            
            for table_name, columns in tables_structure.items():
                try:
                    # Créer une vue qui renomme les colonnes avec leurs libellés d'affichage
                    view_columns = []
                    for col in columns:
                        col_name = col['name']
                        display_name = col.get('display_name', col_name)
                        # Remplacer les caractères spéciaux pour le nom de colonne SQL
                        safe_display_name = display_name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
                        view_columns.append(f"{col_name} AS \"{safe_display_name}\"")
                    
                    if view_columns:
                        view_sql = f"""
                            CREATE OR REPLACE VIEW {table_name}_display AS
                            SELECT {', '.join(view_columns)}
                            FROM {table_name}
                        """
                        await session.execute(text(view_sql))
                        print(f"  ✅ Vue {table_name}_display créée")
                        
                except Exception as e:
                    print(f"  ⚠️ Impossible de créer la vue pour {table_name}: {e}")
            
            # Valider tous les changements
            await session.commit()
            
            print("✅ Toutes les tables ont été créées avec succès")
            print("✅ Contraintes de clés étrangères créées")
            print("✅ Vues avec libellés d'affichage créées")
            print("✅ Utilisateur admin sera créé par init.sql")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création des tables: {e}")
            await session.rollback()
            return False
        finally:
            await session.close()

async def show_table_summary():
    """Affiche un résumé des tables créées avec leurs libellés d'affichage"""
    async for session in get_session():
        try:
            # Récupérer la liste des tables
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            print(f"\n📊 Résumé: {len(tables)} tables créées dans la base de données")
            print("Tables disponibles avec libellés d'affichage:")
            
            for table in tables:
                print(f"\n  📋 {table}:")
                
                # Récupérer les colonnes avec leurs commentaires (libellés d'affichage)
                try:
                    columns_result = await session.execute(text(f"""
                        SELECT column_name, col_description((table_name)::regclass, ordinal_position) as comment
                        FROM information_schema.columns 
                        WHERE table_name = '{table}' 
                        AND table_schema = 'public'
                        ORDER BY ordinal_position
                    """))
                    
                    columns = columns_result.fetchall()
                    for col_name, comment in columns:
                        if comment:
                            print(f"    • {col_name} → {comment}")
                        else:
                            print(f"    • {col_name}")
                            
                except Exception as e:
                    print(f"    ⚠️ Impossible de récupérer les colonnes: {e}")
                
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du résumé: {e}")
        finally:
            await session.close()

if __name__ == "__main__":
    print("🚀 Initialisation de la base de données à partir du fichier CSV...")
    print("=" * 60)
    
    success = asyncio.run(create_tables_from_csv())
    
    if success:
        print("\n" + "=" * 60)
        asyncio.run(show_table_summary())
        print("✅ Initialisation terminée avec succès")
        sys.exit(0)
    else:
        print("❌ Échec de l'initialisation")
        sys.exit(1)
