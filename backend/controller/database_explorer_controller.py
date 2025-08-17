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
        # Vérifier que la table n'est pas sensible
        sensitive_tables = {'users', 'roles', 'refprofiles', 'infos'}
        if table_name.lower() in sensitive_tables:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès interdit à cette table sensible"
            )
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
            column_info = {
                "name": row[0],
                "type": row[1],
                "nullable": row[2] == "YES",
                "default": row[3],
                "max_length": row[4],
                "precision": row[5],
                "scale": row[6]
            }
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
        # Vérifier que la table n'est pas sensible
        sensitive_tables = {'users', 'roles', 'refprofiles', 'infos'}
        if table_name.lower() in sensitive_tables:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès interdit à cette table sensible"
            )
        
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
        # Vérifier que la table n'est pas sensible
        sensitive_tables = {'users', 'roles', 'refprofiles', 'infos'}
        if table_name.lower() in sensitive_tables:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès interdit à cette table sensible"
            )
        
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
        # Vérifier que la table n'est pas sensible
        sensitive_tables = {'users', 'roles', 'refprofiles', 'infos'}
        if table_name.lower() in sensitive_tables:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès interdit à cette table sensible"
            )
        
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
        
        # Construire la requête INSERT dynamiquement
        columns = list(row_data.keys())
        values = list(row_data.values())
        placeholders = [f":{col}" for col in columns]
        
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING *"
        
        # Exécuter l'insertion
        result = await session.execute(text(insert_sql), row_data)
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
        # Vérifier que la table n'est pas sensible
        sensitive_tables = {'users', 'roles', 'refprofiles', 'infos'}
        if table_name.lower() == 'users':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès interdit à cette table sensible"
            )
        
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
        set_clauses = [f"{col} = :{col}" for col in row_data.keys()]
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
        # Vérifier que la table n'est pas sensible
        sensitive_tables = {'users', 'roles', 'refprofiles', 'infos'}
        if table_name.lower() in sensitive_tables:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès interdit à cette table sensible"
            )
        
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