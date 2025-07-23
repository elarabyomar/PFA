from sqlalchemy.ext.asyncio import AsyncSession
from repository.role_repository import RoleRepository
from model.role import Role
from typing import List, Optional
from fastapi import HTTPException, status

async def create_role(session: AsyncSession, role_data: dict, created_by: int) -> Role:
    """Créer un nouveau rôle"""
    role_repo = RoleRepository(session)
    
    # Vérifier si le nom du rôle existe déjà
    if await role_repo.role_exists(role_data["name"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Un rôle avec le nom '{role_data['name']}' existe déjà"
        )
    
    # Ajouter l'ID de l'utilisateur qui crée le rôle
    role_data["created_by"] = created_by
    
    # Créer le rôle
    return await role_repo.create_role(role_data)

async def get_role_by_id(session: AsyncSession, role_id: int) -> Optional[Role]:
    """Récupérer un rôle par son ID"""
    role_repo = RoleRepository(session)
    return await role_repo.get_role_by_id(role_id)

async def get_all_roles(session: AsyncSession) -> List[Role]:
    """Récupérer tous les rôles"""
    role_repo = RoleRepository(session)
    return await role_repo.get_all_roles()

async def get_active_roles(session: AsyncSession) -> List[Role]:
    """Récupérer tous les rôles actifs"""
    role_repo = RoleRepository(session)
    return await role_repo.get_active_roles()

async def update_role(session: AsyncSession, role_id: int, role_data: dict) -> Optional[Role]:
    """Mettre à jour un rôle"""
    role_repo = RoleRepository(session)
    
    # Vérifier si le rôle existe
    existing_role = await role_repo.get_role_by_id(role_id)
    if not existing_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rôle non trouvé"
        )
    
    # Si le nom est modifié, vérifier qu'il n'existe pas déjà
    if "name" in role_data and role_data["name"] != existing_role.name:
        if await role_repo.role_exists(role_data["name"], exclude_id=role_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Un rôle avec le nom '{role_data['name']}' existe déjà"
            )
    
    return await role_repo.update_role(role_id, role_data)

async def delete_role(session: AsyncSession, role_id: int) -> bool:
    """Supprimer un rôle"""
    role_repo = RoleRepository(session)
    
    # Vérifier si le rôle existe
    existing_role = await role_repo.get_role_by_id(role_id)
    if not existing_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rôle non trouvé"
        )
    
    # Empêcher la suppression des rôles système (admin, user)
    if existing_role.name in ["admin", "user"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer un rôle système"
        )
    
    return await role_repo.delete_role(role_id) 