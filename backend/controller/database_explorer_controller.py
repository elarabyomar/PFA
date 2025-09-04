from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, inspect
from config.database.database import get_session
from security.auth_middleware import require_role
from model.user import User
from typing import List, Dict, Any
import json

router = APIRouter()

@router.get("/tables")
async def get_all_tables(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """Récupère la liste de tous les tableaux de la base de données"""
    try:
        # Récupérer la liste des tables avec leur type depuis le CSV
        import csv
        import os
        from pathlib import Path
        
        # Chemin vers le fichier CSV
        csv_path = Path(__file__).parent.parent / "scripts" / "DBTABLES.csv"
        
        table_types = {}
        if csv_path.exists():
            with open(csv_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    table_name = row.get('Table', '').strip()
                    table_type = row.get('Type Table', '').strip()
                    if table_name and table_type:
                        table_types[table_name] = table_type
        
        # Récupérer la liste des tables depuis la base de données
        result = await session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """))
        
        # Tables sensibles à exclure
        sensitive_tables = {'users', 'roles', 'refprofiles', 'infos'}
        
        tables = []
        for row in result.fetchall():
            table_name = row[0]
            
            # Exclure les tables sensibles
            if table_name.lower() in sensitive_tables:
                continue
                
            table_type = table_types.get(table_name, 'REFERENCE')  # Par défaut REFERENCE
            tables.append({
                "name": table_name,
                "type": table_type
            })
        
        return {
            "tables": tables,
            "count": len(tables)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des tables: {str(e)}"
        )

@router.get("/tables/{table_name}/structure")
async def get_table_structure(
    table_name: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """Récupère la structure d'une table spécifique"""
    try:
        # SUPPRIMER: Vérification des tables sensibles
        # sensitive_tables = {'users', 'roles', 'refprofiles', 'infos'}
        # if table_name.lower() in sensitive_tables:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Accès interdit à cette table sensible"
        #     )
        
        # Récupérer les informations des colonnes
        result = await session.execute(text("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = :table_name
            ORDER BY ordinal_position
        """), {"table_name": table_name})
        
        columns = []
        for row in result.fetchall():
            # Debug: afficher les valeurs brutes
            print(f"DEBUG: Colonne {row[0]} - is_nullable brut: '{row[2]}' (type: {type(row[2])})")
            
            column_info = {
                "name": row[0],
                "type": row[1],
                "nullable": row[2] == "YES",
                "default": row[3],
                "max_length": row[4],
                "precision": row[5],
                "scale": row[6]
            }
            print(f"DEBUG: Colonne {row[0]} - nullable traité: {column_info['nullable']}")
            columns.append(column_info)
        
        # Récupérer les contraintes de clé primaire
        pk_result = await session.execute(text("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY' 
            AND tc.table_schema = 'public' 
            AND tc.table_name = :table_name
        """), {"table_name": table_name})
        
        primary_keys = [row[0] for row in pk_result.fetchall()]
        
        # Récupérer les contraintes de clé étrangère
        fk_result = await session.execute(text("""
            SELECT 
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_schema = 'public' 
            AND tc.table_name = :table_name
        """), {"table_name": table_name})
        
        foreign_keys = []
        for row in fk_result.fetchall():
            fk_info = {
                "column": row[0],
                "referenced_table": row[1],
                "referenced_column": row[2]
            }
            foreign_keys.append(fk_info)
        
        return {
            "table_name": table_name,
            "columns": columns,
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys,
            "column_count": len(columns)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de la structure: {str(e)}"
        )

@router.get("/tables/{table_name}/display-labels")
async def get_table_display_labels(
    table_name: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """Récupère les libellés d'affichage d'une table spécifique"""
    try:
        # SUPPRIMER: Vérification des tables sensibles
        
        # Récupérer les libellés d'affichage depuis les commentaires PostgreSQL
        result = await session.execute(text("""
            SELECT 
                column_name,
                col_description((table_name)::regclass, ordinal_position) as display_label
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = :table_name
            ORDER BY ordinal_position
        """), {"table_name": table_name})
        
        # Construire le dictionnaire des libellés
        labels = {}
        for row in result.fetchall():
            column_name = row[0]
            display_label = row[1] if row[1] else column_name  # Utiliser le nom de colonne si pas de libellé
            labels[column_name] = display_label
        
        return {
            "table_name": table_name,
            "labels": labels
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des libellés d'affichage: {str(e)}"
        )

@router.get("/tables/{table_name}/column-descriptions")
async def get_table_column_descriptions(
    table_name: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """Récupère les descriptions des colonnes d'une table depuis le fichier CSV"""
    try:
        
        
        # Lire le fichier CSV pour récupérer les descriptions
        import csv
        from pathlib import Path
        
        csv_path = Path(__file__).parent.parent / "scripts" / "DBTABLES.csv"
        
        if not csv_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fichier CSV DBTABLES.csv non trouvé"
            )
        
        descriptions = {}
        foreign_keys = {}
        found_columns = set()
        
        # Debug: afficher le nom de la table recherchée
        print(f"🔍 Recherche des descriptions pour la table: '{table_name}'")
        
        with open(csv_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                csv_table_name = row.get('Table', '').strip()
                column_name = row.get('Colonne', '').strip()
                description = row.get('Description', '').strip()
                is_foreign_key = row.get('Clé Etrangère', '').strip() == 'TRUE'
                
                # Normaliser les noms pour éviter les problèmes de casse/espaces
                normalized_table_name = csv_table_name.lower().strip()
                normalized_column_name = column_name.lower().strip()
                target_table_name_normalized = table_name.lower().strip()
                
                if normalized_table_name == target_table_name_normalized and normalized_column_name:
                    # Utiliser le nom original de la colonne (pas le nom normalisé)
                    descriptions[column_name] = description if description else f"Colonne {column_name}"
                    found_columns.add(column_name)
                    if is_foreign_key:
                        foreign_keys[column_name] = True
        
        # Log résumé simple et clair
        print(f"📋 Table '{table_name}': {len(descriptions)} descriptions trouvées")
        
        # Si aucune description trouvée, afficher un message d'erreur clair
        if not descriptions:
            print(f"❌ Aucune description trouvée pour la table '{table_name}'")
            print(f"   Vérifiez que la table existe dans le fichier DBTABLES.csv")
        
        return {
            "table_name": table_name,
            "descriptions": descriptions,
            "foreign_keys": foreign_keys
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des descriptions des colonnes: {str(e)}"
        )

@router.get("/tables/{table_name}/foreign-key-data")
async def get_foreign_key_data(
    table_name: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """Récupère les données des tables liées par clés étrangères en utilisant les métadonnées PostgreSQL"""
    try:
        # SUPPRIMER: Vérification des tables sensibles
        
        print(f"🔍 Récupération des clés étrangères pour la table: {table_name}")
        
        # SOLUTION CORRECTE: Utiliser information_schema pour récupérer les vraies contraintes FK
        fk_query = """
            SELECT 
                kcu.column_name,
                ccu.table_name AS referenced_table,
                ccu.column_name AS referenced_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_schema = 'public' 
            AND tc.table_name = :table_name
        """
        
        fk_result = await session.execute(text(fk_query), {"table_name": table_name})
        foreign_keys = fk_result.fetchall()
        
        print(f"🔍 {len(foreign_keys)} clés étrangères trouvées dans PostgreSQL")
        
        foreign_keys_info = {}
        
        for fk in foreign_keys:
            column_name = fk[0]
            referenced_table = fk[1]
            referenced_column = fk[2]
            
            print(f"🔍 FK détectée: {column_name} → {referenced_table}.{referenced_column}")
            
            try:
                # Récupérer les données de la table référencée
                data_query = f"""
                    SELECT id, * FROM {referenced_table} 
                    ORDER BY id 
                    LIMIT 100
                """
                
                print(f"🔍 Exécution de: {data_query}")
                
                result = await session.execute(text(data_query))
                rows = result.fetchall()
                
                print(f"✅ {len(rows)} lignes récupérées de {referenced_table}")
                
                # Convertir les données en format utilisable
                data = []
                for row in rows:
                    row_dict = {}
                    for key, value in row._mapping.items():
                        if hasattr(value, 'isoformat'):
                            row_dict[key] = value.isoformat()
                        else:
                            row_dict[key] = value
                    data.append(row_dict)
                
                foreign_keys_info[column_name] = {
                    "referenced_table": referenced_table,
                    "referenced_column": referenced_column,
                    "data": data,
                    "count": len(data)
                }
                
                print(f"✅ Clé étrangère {column_name} configurée avec {len(data)} valeurs")
                
            except Exception as e:
                print(f"❌ Erreur lors de la récupération des données de {referenced_table}: {e}")
                foreign_keys_info[column_name] = {
                    "referenced_table": referenced_table,
                    "referenced_column": referenced_column,
                    "data": [],
                    "count": 0,
                    "error": str(e)
                }
        
        return {
            "table_name": table_name,
            "foreign_keys_data": foreign_keys_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des données des clés étrangères: {str(e)}"
        )

@router.get("/test-fk/{table_name}")
async def test_foreign_keys(
    table_name: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """Endpoint de test pour déboguer les clés étrangères"""
    try:
        print(f"🧪 Test des clés étrangères pour la table: {table_name}")
        
        # Lire le CSV pour identifier les clés étrangères
        import csv
        from pathlib import Path
        
        csv_path = Path(__file__).parent.parent / "scripts" / "DBTABLES.csv"
        
        if not csv_path.exists():
            return {"error": "Fichier CSV non trouvé"}
        
        foreign_keys_info = {}
        
        with open(csv_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                csv_table_name = row.get('Table', '').strip()
                column_name = row.get('Colonne', '').strip()
                is_foreign_key = row.get('Clé Etrangère', '').strip() == 'TRUE'
                
                if csv_table_name == table_name and is_foreign_key:
                    print(f"🧪 Clé étrangère trouvée: {column_name}")
                    
                    # Appliquer la même logique de détection
                    column_lower = column_name.lower()
                    referenced_table = None
                    
                    if 'iduser' in column_lower:
                        referenced_table = 'users'
                    elif 'idclient' in column_lower:
                        referenced_table = 'clients'
                    elif 'idproduit' in column_lower:
                        referenced_table = 'produits'
                    elif 'idcie' in column_lower:
                        referenced_table = 'compagnies'
                    
                    if referenced_table:
                        # Vérifier l'existence et récupérer les données
                        table_exists = await session.execute(text("""
                            SELECT COUNT(*) 
                            FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = :table_name
                        """), {"table_name": referenced_table})
                        
                        if table_exists.scalar() > 0:
                            count = await session.execute(text(f"SELECT COUNT(*) FROM {referenced_table}"))
                            row_count = count.scalar()
                            
                            foreign_keys_info[column_name] = {
                                "referenced_table": referenced_table,
                                "exists": True,
                                "row_count": row_count
                            }
                            
                            print(f"🧪 {column_name} → {referenced_table}: {row_count} lignes")
                        else:
                            foreign_keys_info[column_name] = {
                                "referenced_table": referenced_table,
                                "exists": False,
                                "row_count": 0
                            }
                    else:
                        foreign_keys_info[column_name] = {
                            "referenced_table": None,
                            "exists": False,
                            "row_count": 0
                        }
        
        return {
            "table_name": table_name,
            "foreign_keys": foreign_keys_info
        }
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return {"error": str(e)}

@router.get("/tables/{table_name}/data")
async def get_table_data(
    table_name: str,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """Récupère les données d'une table spécifique avec pagination"""
    try:
        # SUPPRIMER: Vérification des tables sensibles
        
        # Vérifier que la table existe
        table_check = await session.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """), {"table_name": table_name})
        
        if table_check.scalar() == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table '{table_name}' non trouvée"
            )
        
        # Récupérer le nombre total de lignes
        count_result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        total_rows = count_result.scalar()
        
        # Récupérer les données avec pagination
        data_result = await session.execute(text(f"""
            SELECT * FROM {table_name} 
            ORDER BY 1 
            LIMIT :limit OFFSET :offset
        """), {"limit": limit, "offset": offset})
        
        # Récupérer les noms des colonnes
        columns = list(data_result.keys())
        
        # Récupérer les données
        rows = []
        for row in data_result.fetchall():
            row_dict = {}
            for i, value in enumerate(row):
                # Convertir les types non-sérialisables
                if hasattr(value, 'isoformat'):
                    row_dict[columns[i]] = value.isoformat()
                else:
                    row_dict[columns[i]] = value
            rows.append(row_dict)
        
        return {
            "table_name": table_name,
            "columns": columns,
            "data": rows,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total_rows": total_rows,
                "current_page": (offset // limit) + 1,
                "total_pages": (total_rows + limit - 1) // limit
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des données: {str(e)}"
        )

@router.get("/tables/{table_name}/count")
async def get_table_row_count(
    table_name: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """Récupère le nombre de lignes d'une table"""
    try:
        # SUPPRIMER: Vérification des tables sensibles
        
        result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
        
        return {
            "table_name": table_name,
            "row_count": count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du comptage des lignes: {str(e)}"
        )

@router.post("/tables/{table_name}/rows")
async def create_table_row(
    table_name: str,
    row_data: dict,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """Crée une nouvelle ligne dans une table"""
    try:
        # SUPPRIMER: Vérification des tables sensibles
        
        # Vérifier que la table existe
        table_check = await session.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND table_name = :table_name
        """), {"table_name": table_name})
        
        if table_check.scalar() == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table '{table_name}' non trouvée"
            )
        
        # CORRECTION: Convertir les dates automatiquement
        processed_data = {}
        for key, value in row_data.items():
            if isinstance(value, str):
                # Essayer de détecter et convertir les dates
                if key.lower() in ['datedebut', 'datefin', 'date_debut', 'date_fin', 'date', 'datecreation', 'datemodification']:
                    try:
                        from datetime import datetime
                        # Essayer différents formats de date
                        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']
                        converted_date = None
                        
                        for date_format in date_formats:
                            try:
                                converted_date = datetime.strptime(value, date_format)
                                break
                            except ValueError:
                                continue
                        
                        if converted_date:
                            processed_data[key] = converted_date
                            print(f"✅ Date convertie: {key} = '{value}' → {converted_date}")
                        else:
                            processed_data[key] = value
                            print(f"⚠️  Impossible de convertir la date: {key} = '{value}'")
                    except Exception as e:
                        print(f"❌ Erreur lors de la conversion de la date {key}: {e}")
                        processed_data[key] = value
                else:
                    processed_data[key] = value
            else:
                processed_data[key] = value
        
        # Construire la requête INSERT dynamiquement
        columns = list(processed_data.keys())
        values = list(processed_data.values())
        placeholders = [f":{col}" for col in columns]
        
        # CORRECTION: Quoter les noms de colonnes pour respecter la casse
        quoted_columns = [f'"{col}"' for col in columns]
        insert_sql = f"INSERT INTO {table_name} ({', '.join(quoted_columns)}) VALUES ({', '.join(placeholders)}) RETURNING *"
        
        print(f"🔍 SQL généré: {insert_sql}")
        print(f"🔍 Données traitées: {processed_data}")
        
        # Exécuter l'insertion
        result = await session.execute(text(insert_sql), processed_data)
        await session.commit()
        
        # Récupérer la ligne insérée
        inserted_row = result.fetchone()
        
        return {
            "message": "Ligne créée avec succès",
            "table_name": table_name,
            "row": dict(inserted_row._mapping) if inserted_row else {}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        print(f"❌ Erreur lors de la création: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de la ligne: {str(e)}"
        )

@router.put("/tables/{table_name}/rows/{row_id}")
async def update_table_row(
    table_name: str,
    row_id: int,
    row_data: dict,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """Met à jour une ligne existante dans une table"""
    try:
        # SUPPRIMER: Vérification des tables sensibles
        
        # Vérifier que la table existe
        table_check = await session.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = :table_name
        """), {"table_name": table_name})
        
        if table_check.scalar() == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table '{table_name}' non trouvée"
            )
        
        # Construire la requête UPDATE dynamiquement
        # CORRECTION: Quoter les noms de colonnes pour respecter la casse
        set_clauses = [f'"{col}" = :{col}' for col in row_data.keys()]
        update_sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE id = :row_id RETURNING *"
        
        # Ajouter l'ID à la requête
        update_data = {**row_data, "row_id": row_id}
        
        # Exécuter la mise à jour
        result = await session.execute(text(update_sql), update_data)
        await session.commit()
        
        # Vérifier si la ligne a été mise à jour
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ligne avec ID {row_id} non trouvée dans la table {table_name}"
            )
        
        # Récupérer la ligne mise à jour
        updated_row = result.fetchone()
        
        return {
            "message": "Ligne mise à jour avec succès",
            "table_name": table_name,
            "row": dict(updated_row._mapping) if updated_row else {}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour de la ligne: {str(e)}"
        )

@router.delete("/tables/{table_name}/rows/{row_id}")
async def delete_table_row(
    table_name: str,
    row_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """Supprime une ligne d'une table"""
    try:
        # SUPPRIMER: Vérification des tables sensibles
        
        # Vérifier que la table existe
        table_check = await session.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = :table_name
        """), {"table_name": table_name})
        
        if table_check.scalar() == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table '{table_name}' non trouvée"
            )
        
        # Construire la requête DELETE
        delete_sql = f"DELETE FROM {table_name} WHERE id = :row_id"
        
        # Exécuter la suppression
        result = await session.execute(text(delete_sql), {"row_id": row_id})
        await session.commit()
        
        # Vérifier si la ligne a été supprimée
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ligne avec ID {row_id} non trouvée dans la table {table_name}"
            )
        
        return {
            "message": "Ligne supprimée avec succès",
            "table_name": table_name,
            "deleted_id": row_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression de la ligne: {str(e)}"
        ) 

@router.get("/tables/{table_name}/master-tables-data")
async def get_master_tables_data(
    table_name: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """Récupère les données des tables master référencées par une table"""
    try:
        # SUPPRIMER: Vérification des tables sensibles
        
        print(f"🔍 Récupération des données des tables master pour: {table_name}")
        
        # Récupérer toutes les clés étrangères de cette table
        fk_query = """
            SELECT 
                kcu.column_name,
                ccu.table_name AS referenced_table,
                ccu.column_name AS referenced_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_schema = 'public' 
            AND tc.table_name = :table_name
        """
        
        fk_result = await session.execute(text(fk_query), {"table_name": table_name})
        foreign_keys = fk_result.fetchall()
        
        print(f"🔍 {len(foreign_keys)} clés étrangères trouvées")
        
        master_tables_data = {}
        
        for fk in foreign_keys:
            column_name = fk[0]
            referenced_table = fk[1]
            referenced_column = fk[2]
            
            print(f"🔍 Chargement des données de {referenced_table} pour {column_name}")
            
            try:
                # Récupérer les données de la table référencée
                data_query = f"""
                    SELECT id, * FROM {referenced_table} 
                    ORDER BY id 
                    LIMIT 100
                """
                
                result = await session.execute(text(data_query))
                rows = result.fetchall()
                
                # Convertir les données en format utilisable
                data = []
                for row in rows:
                    row_dict = {}
                    for key, value in row._mapping.items():
                        if hasattr(value, 'isoformat'):
                            row_dict[key] = value.isoformat()
                        else:
                            row_dict[key] = value
                    data.append(row_dict)
                
                master_tables_data[column_name] = {
                    "referenced_table": referenced_table,
                    "referenced_column": referenced_column,
                    "data": data,
                    "count": len(data)
                }
                
                print(f"✅ {referenced_table}: {len(data)} lignes chargées")
                
            except Exception as e:
                print(f"❌ Erreur lors du chargement de {referenced_table}: {e}")
                master_tables_data[column_name] = {
                    "referenced_table": referenced_table,
                    "referenced_column": referenced_column,
                    "data": [],
                    "count": 0,
                    "error": str(e)
                }
        
        return {
            "table_name": table_name,
            "master_tables_data": master_tables_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des données des tables master: {str(e)}"
        ) 