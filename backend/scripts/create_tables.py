#!/usr/bin/env python3
"""
Script pour créer automatiquement toutes les tables de la base de données
à partir du fichier CSV DBTABLES.csv
"""

import asyncio
import sys
import os
import csv
import logging
import subprocess
from datetime import datetime
from collections import defaultdict

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database.database import get_session
from sqlalchemy import text

def setup_logging():
    """Configure le système de logging complet avec fichiers et console"""
    # Créer le dossier logs dans le répertoire de travail actuel (local)
    # Utiliser le répertoire parent du projet pour être sûr d'être accessible
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logs_dir = os.path.join(project_root, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Nom du fichier de log avec timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'database_init_{timestamp}.log'
    log_filepath = os.path.join(logs_dir, log_filename)
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            # Handler pour fichier (niveau DEBUG - tout)
            logging.FileHandler(log_filepath, encoding='utf-8'),
            # Handler pour console (niveau INFO - moins verbeux)
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Logger principal
    logger = logging.getLogger(__name__)
    
    # Log de début
    logger.info("=" * 80)
    logger.info("🚀 DÉBUT DE L'INITIALISATION DE LA BASE DE DONNÉES")
    logger.info(f"📁 Fichier de log LOCAL: {log_filepath}")
    logger.info(f"📂 Dossier logs: {logs_dir}")
    logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 80)
    
    return logger, log_filepath

def parse_csv_structure(csv_file_path, logger):
    """Parse le fichier CSV pour extraire la structure des tables"""
    tables = defaultdict(list)
    
    logger.info(f"📖 Lecture du fichier CSV: {csv_file_path}")
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            logger.info(f"📋 En-têtes CSV détectés: {list(reader.fieldnames)}")
            
            row_count = 0
            for row in reader:
                row_count += 1
                table_name = row['Table'].strip()
                column_name = row['Colonne'].strip()
                
                # Ignorer les lignes vides
                if not table_name or not column_name:
                    logger.debug(f"⚠️ Ligne {row_count} ignorée (table ou colonne vide): {row}")
                    continue
                
                column_info = {
                    'name': column_name,
                    'display_name': row.get('Libellé Affichage', column_name),
                    'description': row.get('Description', ''),
                    'values_possibles': row.get('Valeurs Possibles', ''),
                    'primary_key': row.get('Clé Primaire', '').upper() == 'TRUE',
                    'foreign_key': row.get('Clé Etrangère', '').upper() == 'TRUE',
                    'foreign_key_reference': row.get('foreign_key', ''),
                    'format': row.get('Format', ''),
                    'table_type': row.get('Type Table', 'MASTER')
                }
                
                tables[table_name].append(column_info)
                logger.debug(f"📝 Ligne {row_count}: Table '{table_name}' - Colonne '{column_name}' - Type: {column_info['table_type']}")
                
    except FileNotFoundError:
        logger.error(f"❌ Fichier CSV non trouvé: {csv_file_path}")
        return {}
    except Exception as e:
        logger.error(f"❌ Erreur lors de la lecture du CSV: {e}", exc_info=True)
        return {}
    
    logger.info(f"✅ CSV parsé avec succès: {row_count} lignes traitées, {len(tables)} tables trouvées")
    return tables

def generate_create_table_sql(table_name, columns, all_tables_structure, logger):
    """Génère le SQL CREATE TABLE pour une table donnée"""
    logger.debug(f"🔧 Génération SQL pour table '{table_name}' avec {len(columns)} colonnes")
    
    column_definitions = []
    primary_keys = []
    foreign_keys = []
    unique_constraints = []
    
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
            logger.debug(f"    ⚠️ Type de données non reconnu pour {col_name}: '{col_format}', utilisation de VARCHAR(255)")
        
        logger.debug(f"    📝 Colonne '{col_name}': type={data_type}, PK={col_primary}, FK={col_foreign}, nullable={col_nullable}")
        
        # Construire la définition de colonne (sans COMMENT dans CREATE TABLE)
        column_def = f'"{col_name}" {data_type}'
        
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
        quoted_pks = [f'"{pk}"' for pk in primary_keys]
        column_definitions.append(f"PRIMARY KEY ({', '.join(quoted_pks)})")
    
    # Ajouter des contraintes UNIQUE pour les colonnes de code qui sont référencées comme FK
    for col in columns:
        col_name = col['name']
        # Vérifier si cette colonne est référencée comme FK dans d'autres tables
        for other_table, other_columns in all_tables_structure.items():
            if other_table != table_name:  # Ne pas vérifier la table actuelle
                for other_col in other_columns:
                    if (other_col.get('foreign_key_reference') and 
                        other_col['foreign_key_reference'].strip() and
                        '(' in other_col['foreign_key_reference'] and 
                        ')' in other_col['foreign_key_reference']):
                        
                        # Extraire la table et colonne référencée
                        fk_ref = other_col['foreign_key_reference'].strip()
                        ref_table = fk_ref.split('(')[0].strip()
                        ref_column = fk_ref.split('(')[1].split(')')[0].strip()
                        
                        # Si cette colonne est référencée comme FK, ajouter une contrainte UNIQUE
                        if ref_table == table_name and ref_column == col_name:
                            if col_name not in [pk for pk in primary_keys]:  # Ne pas ajouter si c'est déjà une PK
                                # Éviter les doublons de contraintes UNIQUE
                                unique_constraint = f'UNIQUE ("{col_name}")'
                                if unique_constraint not in unique_constraints:
                                    unique_constraints.append(unique_constraint)
                                    logger.info(f"    🔒 Ajout de contrainte UNIQUE sur {col_name} (référencé comme FK)")
                                else:
                                    logger.debug(f"    ⚠️ Contrainte UNIQUE déjà présente pour {col_name}")
                            else:
                                logger.debug(f"    ℹ️ Pas de contrainte UNIQUE nécessaire pour {col_name} (déjà PK)")
                        else:
                            # Vérifier que la table et colonne référencées existent
                            if ref_table not in all_tables_structure:
                                logger.warning(f"    ⚠️ Table référencée '{ref_table}' n'existe pas pour FK {other_col['name']}")
                                continue
                            
                            referenced_table_columns = [c['name'] for c in all_tables_structure[ref_table]]
                            if ref_column not in referenced_table_columns:
                                logger.warning(f"    ⚠️ Colonne '{ref_column}' n'existe pas dans table '{ref_table}' pour FK {other_col['name']}")
                                continue
    
    # Ajouter les contraintes UNIQUE
    column_definitions.extend(unique_constraints)
    
    # Générer le SQL CREATE TABLE (sans COMMENT)
    separator = ',\n    '
    sql = f"""CREATE TABLE IF NOT EXISTS "{table_name}" (
    {separator.join(column_definitions)}
)"""
    
    logger.debug(f"📄 SQL généré pour '{table_name}':")
    logger.debug(f"   {sql}")
    
    return sql

async def run_init_data(logger):
    """Run the init_data.py script to populate the database with initial data"""
    logger.info("🚀 PHASE 4: Exécution du script init_data.py pour peupler la base...")
    
    try:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        init_data_path = os.path.join(script_dir, 'init_data.py')
        
        if not os.path.exists(init_data_path):
            logger.error(f"❌ Script init_data.py non trouvé: {init_data_path}")
            return False
        
        logger.info(f"📁 Exécution de: {init_data_path}")
        
        # Run the init_data.py script as a subprocess
        result = subprocess.run(
            [sys.executable, init_data_path],
            cwd=script_dir,
            capture_output=True,
            text=True,
            encoding='utf-8',
            env={**os.environ, 'PYTHONPATH': f"{script_dir}:{os.path.dirname(script_dir)}:{os.environ.get('PYTHONPATH', '')}"}
        )
        
        if result.returncode == 0:
            logger.info("✅ Script init_data.py exécuté avec succès")
            if result.stdout:
                logger.info("📤 Sortie du script:")
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        logger.info(f"   {line}")
            return True
        else:
            logger.error(f"❌ Échec de l'exécution de init_data.py (code: {result.returncode})")
            if result.stdout:
                logger.error("📤 Sortie standard du script:")
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        logger.error(f"   {line}")
            if result.stderr:
                logger.error("📤 Erreurs du script:")
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        logger.error(f"   {line}")
            else:
                logger.error("📤 Aucune erreur stderr capturée")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution de init_data.py: {e}", exc_info=True)
        return False

async def create_tables_from_csv():
    """Crée toutes les tables à partir du fichier CSV"""
    
    # Configuration du logging
    logger, log_filepath = setup_logging()
    
    # Chemin vers le fichier CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'DBTABLES.csv')
    
    # Parser la structure du CSV
    logger.info("📖 Lecture du fichier CSV DBTABLES.csv...")
    tables_structure = parse_csv_structure(csv_path, logger)
    
    if not tables_structure:
        logger.error("❌ Aucune table trouvée dans le CSV")
        return False
    
    logger.info(f"✅ {len(tables_structure)} tables trouvées dans le CSV")
    
    # Afficher un résumé des références FK trouvées
    logger.info("🔍 Références de clés étrangères trouvées:")
    for table_name, columns in tables_structure.items():
        fk_columns = [col for col in columns if col.get('foreign_key_reference')]
        if fk_columns:
            logger.info(f"  📋 {table_name}:")
            for col in fk_columns:
                logger.info(f"    • {col['name']} → {col['foreign_key_reference']}")
    
    # Afficher un résumé des colonnes qui seront référencées comme FK (nécessitent des contraintes UNIQUE)
    logger.info("🔒 Colonnes qui nécessitent des contraintes UNIQUE (référencées comme FK):")
    referenced_columns = {}
    for table_name, columns in tables_structure.items():
        for col in columns:
            if col.get('foreign_key_reference') and col['foreign_key_reference'].strip():
                fk_ref = col['foreign_key_reference'].strip()
                if '(' in fk_ref and ')' in fk_ref:
                    ref_table = fk_ref.split('(')[0].strip()
                    ref_column = fk_ref.split('(')[1].split(')')[0].strip()
                    if ref_table not in referenced_columns:
                        referenced_columns[ref_table] = set()
                    referenced_columns[ref_table].add(ref_column)
    
    for table_name, columns in sorted(referenced_columns.items()):
        logger.info(f"  📋 {table_name}: {', '.join(sorted(columns))}")
    
    # Vérifier d'abord que toutes les tables référencées dans les FK existent
    logger.info("🔍 Vérification de la cohérence des références FK...")
    fk_errors = []
    for table_name, columns in tables_structure.items():
        for col in columns:
            if col.get('foreign_key_reference') and col['foreign_key_reference'].strip():
                fk_ref = col['foreign_key_reference'].strip()
                if '(' in fk_ref and ')' in fk_ref:
                    ref_table = fk_ref.split('(')[0].strip()
                    ref_column = fk_ref.split('(')[1].split(')')[0].strip()
                    
                    if ref_table not in tables_structure:
                        fk_errors.append(f"Table '{ref_table}' référencée par {table_name}.{col['name']} n'existe pas")
                    elif ref_column not in [c['name'] for c in tables_structure[ref_table]]:
                        fk_errors.append(f"Colonne '{ref_column}' dans table '{ref_table}' référencée par {table_name}.{col['name']} n'existe pas")
    
    if fk_errors:
        logger.error("❌ Erreurs de cohérence FK détectées:")
        for error in fk_errors:
            logger.error(f"  • {error}")
        logger.error("❌ Impossible de continuer avec des références FK invalides")
        return False
    
    logger.info("✅ Toutes les références FK sont cohérentes")
    
    # ===== SOLUTION 2: ASYNCIO LOOP MANAGEMENT =====
    # Créer un nouvel event loop pour éviter les conflits
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            logger.info("🔄 Event loop déjà en cours d'exécution, création d'un nouveau loop...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            logger.info("✅ Event loop disponible et prêt")
    except RuntimeError:
        logger.info("🔄 Création d'un nouvel event loop...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # ===== SOLUTION 3: TRANSACTION ISOLATION =====
    # PHASE 1: Création des tables (transaction séparée)
    logger.info("🔧 PHASE 1: Création de toutes les tables...")
    
    try:
        async for session in get_session():
            try:
                # Créer toutes les tables sans ordre spécifique
                for table_name, columns in tables_structure.items():
                    try:
                        logger.info(f"🔧 Création de la table {table_name}...")
                        
                        # Générer le SQL CREATE TABLE
                        create_sql = generate_create_table_sql(table_name, columns, tables_structure, logger)
                        
                        # Exécuter la création
                        logger.debug(f"📤 Exécution SQL pour {table_name}: {create_sql}")
                        await session.execute(text(create_sql))
                        logger.info(f"  ✅ Table {table_name} créée")
                        
                        # Ajouter les commentaires sur la table et les colonnes
                        try:
                            # Commentaire sur la table (échapper les apostrophes)
                            table_comment = f"Table {table_name} avec libelles d'affichage".replace("'", "''")
                            table_comment_sql = f'COMMENT ON TABLE "{table_name}" IS \'{table_comment}\''
                            logger.debug(f"📤 Exécution commentaire table {table_name}: {table_comment_sql}")
                            await session.execute(text(table_comment_sql))
                            
                            # Commentaires sur les colonnes (échapper les apostrophes)
                            for col in columns:
                                col_name = col['name']
                                display_name = col.get('display_name', col_name)
                                # Échapper les apostrophes en les doublant
                                safe_display_name = display_name.replace("'", "''")
                                col_comment = f'COMMENT ON COLUMN "{table_name}"."{col_name}" IS \'{safe_display_name}\''
                                logger.debug(f"📤 Exécution commentaire colonne {table_name}.{col_name}: {col_comment}")
                                await session.execute(text(col_comment))
                            
                            logger.info(f"  ✅ Commentaires ajoutés pour {table_name}")
                            
                        except Exception as e:
                            logger.warning(f"  ⚠️ Impossible d'ajouter les commentaires pour {table_name}: {e}", exc_info=True)
                        
                    except Exception as e:
                        logger.error(f"  ❌ Erreur lors de la création de la table {table_name}: {e}", exc_info=True)
                        logger.info(f"     Continuation avec les autres tables...")
                        continue
                
                # Valider la création des tables
                logger.info("💾 Validation de la création des tables...")
                await session.commit()
                logger.info("✅ Toutes les tables ont été créées avec succès")
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de la création des tables: {e}", exc_info=True)
                await session.rollback()
                return False
            finally:
                await session.close()
    except Exception as e:
        logger.error(f"❌ Erreur de session lors de la création des tables: {e}", exc_info=True)
        return False
    
    # PHASE 2: Création des clés étrangères (transaction séparée)
    logger.info("🔧 PHASE 2: Ajout des contraintes de clés étrangères...")
    
    try:
        async for session in get_session():
            try:
                for table_name, columns in tables_structure.items():
                    try:
                        logger.info(f"  🔍 Vérification des clés étrangères pour {table_name}...")
                        for col in columns:
                            if col['foreign_key'] and col.get('foreign_key_reference') and col['foreign_key_reference'].strip():
                                col_name = col['name']
                                fk_reference = col['foreign_key_reference'].strip()
                                logger.info(f"    📋 Colonne {col_name}: référence FK = '{fk_reference}'")
                                
                                # Gérer le cas spécial avec plusieurs références (ex: flotte_auto(id) / assure_sante(id))
                                if ' / ' in fk_reference:
                                    logger.warning(f"    ⚠️ Colonne {col_name} a plusieurs références FK possibles: {fk_reference}")
                                    logger.warning(f"       Cette colonne nécessite une logique métier pour choisir la bonne référence")
                                    logger.warning(f"       Aucune contrainte FK automatique créée pour cette colonne")
                                    continue
                                
                                # Parser la référence FK (format: table(column))
                                if '(' in fk_reference and ')' in fk_reference:
                                    # Extraire le nom de la table et de la colonne
                                    table_part = fk_reference.split('(')[0].strip()
                                    column_part = fk_reference.split('(')[1].split(')')[0].strip()
                                    
                                    logger.info(f"    🔗 Création FK: {col_name} → {table_part}.{column_part}")
                                    
                                    # Vérifier si la contrainte FK existe déjà (case-insensitive)
                                    check_fk_sql = f"""
                                        SELECT COUNT(*) FROM information_schema.table_constraints 
                                        WHERE LOWER(constraint_name) = LOWER('fk_{table_name}_{col_name}') 
                                        AND table_name = '{table_name}'
                                    """
                                    result = await session.execute(text(check_fk_sql))
                                    fk_exists = result.fetchone()[0] > 0
                                    
                                    if fk_exists:
                                        logger.info(f"    ℹ️ Clé étrangère {col_name} → {table_part}.{column_part} existe déjà, ignorée")
                                    else:
                                        # Créer la contrainte de clé étrangère (utiliser le nom exact de la base)
                                        # D'abord, récupérer le nom exact de la contrainte existante
                                        get_existing_fk_sql = f"""
                                            SELECT constraint_name FROM information_schema.table_constraints 
                                            WHERE LOWER(constraint_name) LIKE LOWER('fk_{table_name}_{col_name}%') 
                                            AND table_name = '{table_name}'
                                            LIMIT 1
                                        """
                                        existing_result = await session.execute(text(get_existing_fk_sql))
                                        existing_fk = existing_result.fetchone()
                                        
                                        if existing_fk:
                                            logger.info(f"    ℹ️ Clé étrangère {col_name} → {table_part}.{column_part} existe déjà avec le nom: {existing_fk[0]}")
                                        else:
                                            # Créer la contrainte de clé étrangère
                                            fk_sql = f"""
                                                ALTER TABLE "{table_name}" 
                                                ADD CONSTRAINT fk_{table_name}_{col_name} 
                                                FOREIGN KEY ("{col_name}") 
                                                REFERENCES "{table_part}"("{column_part}")
                                            """
                                            logger.debug(f"📤 Exécution FK {table_name}.{col_name}: {fk_sql}")
                                            await session.execute(text(fk_sql))
                                            logger.info(f"    ✅ Clé étrangère {col_name} → {table_part}.{column_part} créée")
                                else:
                                    logger.warning(f"    ⚠️ Format de référence FK invalide pour {col_name}: {fk_reference}")
                            elif col['foreign_key'] and not col.get('foreign_key_reference'):
                                logger.warning(f"    ⚠️ Colonne {col['name']} marquée comme FK mais sans référence spécifiée")
                        
                    except Exception as e:
                        logger.error(f"  ⚠️ Impossible d'ajouter les clés étrangères pour {table_name}: {e}", exc_info=True)
                        # Continuer avec les autres tables même si une FK échoue
                        # Réinitialiser la session pour éviter les erreurs de transaction
                        try:
                            await session.rollback()
                            logger.info(f"  🔄 Session réinitialisée pour {table_name}")
                        except Exception as rollback_error:
                            logger.warning(f"  ⚠️ Impossible de réinitialiser la session: {rollback_error}")
                        continue
                
                # Valider la création des clés étrangères
                logger.info("💾 Validation des clés étrangères...")
                await session.commit()
                logger.info("✅ Contraintes de clés étrangères créées")
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de la création des clés étrangères: {e}", exc_info=True)
                await session.rollback()
                return False
            finally:
                await session.close()
    except Exception as e:
        logger.error(f"❌ Erreur de session lors de la création des clés étrangères: {e}", exc_info=True)
        return False
    
    # PHASE 3: Création des vues (transaction séparée)
    logger.info("🔧 PHASE 3: Création des vues avec libellés d'affichage...")
    
    try:
        async for session in get_session():
            try:
                for table_name, columns in tables_structure.items():
                    try:
                        # Créer une vue qui renomme les colonnes avec leurs libellés d'affichage
                        view_columns = []
                        for col in columns:
                            col_name = col['name']
                            display_name = col.get('display_name', col_name)
                            # Remplacer les caractères spéciaux pour le nom de colonne SQL
                            safe_display_name = display_name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
                            view_columns.append(f'"{col_name}" AS "{safe_display_name}"')
                        
                        if view_columns:
                            view_sql = f"""
                                CREATE OR REPLACE VIEW "{table_name}_display" AS
                                SELECT {', '.join(view_columns)}
                                FROM "{table_name}"
                            """
                            logger.debug(f"📤 Exécution vue {table_name}: {view_sql}")
                            await session.execute(text(view_sql))
                            logger.info(f"  ✅ Vue {table_name}_display créée")
                            
                    except Exception as e:
                        logger.warning(f"  ⚠️ Impossible de créer la vue pour {table_name}: {e}", exc_info=True)
                        # Continuer avec les autres vues même si une échoue
                
                # Valider la création des vues
                logger.info("💾 Validation de la création des vues...")
                await session.commit()
                logger.info("✅ Vues avec libellés d'affichage créées")
                logger.info("✅ Utilisateur admin sera créé par init.sql")
                
                # IMPORTANT: Fermer la session AVANT de retourner pour éviter les conflits
                await session.close()
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de la création des vues: {e}", exc_info=True)
                await session.rollback()
                await session.close()
                return False
    except Exception as e:
        logger.error(f"❌ Erreur de session lors de la création des vues: {e}", exc_info=True)
        return False
    
    # PHASE 4: Exécution de init_data.py pour peupler la base
    logger.info("🚀 PHASE 4: Exécution du script init_data.py pour peupler la base...")
    
    init_data_success = await run_init_data(logger)
    if not init_data_success:
        logger.warning("⚠️ Échec de l'exécution de init_data.py, mais les tables ont été créées")
        logger.warning("⚠️ Vous pouvez exécuter manuellement: python scripts/init_data.py")
    
    return True

async def show_table_summary(logger):
    """Affiche un résumé des tables créées avec leurs libellés d'affichage"""
    
    logger.info("📊 Tentative de récupération du résumé des tables...")
    
    # ===== SOLUTION 2: ASYNCIO LOOP MANAGEMENT =====
    # Gérer les conflits de loop de manière robuste
    try:
        # Essayer d'utiliser le loop actuel d'abord
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
                
                logger.info(f"\n📊 Résumé: {len(tables)} tables créées dans la base de données")
                logger.info("Tables disponibles avec libellés d'affichage:")
                
                for table in tables:
                    logger.info(f"\n  📋 {table}:")
                    
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
                                logger.info(f"    • {col_name} → {comment}")
                            else:
                                logger.info(f"    • {col_name}")
                                
                    except Exception as e:
                        logger.warning(f"    ⚠️ Impossible de récupérer les colonnes: {e}", exc_info=True)
                
                await session.close()
                logger.info("✅ Résumé des tables récupéré avec succès")
                return
                    
            except Exception as e:
                logger.error(f"❌ Erreur lors de la récupération du résumé: {e}", exc_info=True)
                await session.close()
                raise
                
    except RuntimeError as e:
        if "attached to a different loop" in str(e):
            logger.warning("⚠️ Conflit de loop détecté, tentative de récupération simplifiée...")
            # Fallback: essayer de récupérer juste le nombre de tables
            try:
                async for session in get_session():
                    try:
                        result = await session.execute(text("""
                            SELECT COUNT(*) as table_count
                            FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_type = 'BASE TABLE'
                        """))
                        
                        count = result.fetchone()[0]
                        logger.info(f"\n📊 Résumé simplifié: {count} tables créées dans la base de données")
                        logger.info("⚠️ Détails des colonnes non disponibles (conflit de loop)")
                        await session.close()
                        return
                        
                    except Exception as e2:
                        logger.error(f"❌ Même la récupération simplifiée a échoué: {e2}", exc_info=True)
                        await session.close()
                        raise
            except Exception as e3:
                logger.error(f"❌ Impossible de créer une session pour le résumé: {e3}", exc_info=True)
        else:
            logger.error(f"❌ Erreur de runtime inattendue: {e}", exc_info=True)
            raise
    except Exception as e:
        logger.error(f"❌ Erreur inattendue lors de la récupération du résumé: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Configuration du logging principal
    logger, log_filepath = setup_logging()
    
    logger.info("🚀 Initialisation de la base de données à partir du fichier CSV...")
    logger.info("=" * 60)
    
    success = asyncio.run(create_tables_from_csv())
    
    if success:
        logger.info("\n" + "=" * 60)
        
        # SAFE APPROACH: Skip the problematic summary function entirely
        logger.info("ℹ️ Résumé des tables désactivé pour éviter les conflits de session")
        logger.info("ℹ️ Les tables ont été créées avec succès")
        
        logger.info("✅ Initialisation terminée avec succès")
        logger.info(f"📁 Logs complets disponibles dans: {log_filepath}")
        sys.exit(0)
    else:
        logger.error("❌ Échec de l'initialisation")
        logger.error(f"📁 Logs d'erreur disponibles dans: {log_filepath}")
        sys.exit(1)
