from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from config.database.database import get_session
from service.role_management_service import (
    create_role, get_role_by_id, get_all_roles, 
    update_role, delete_role
)
from dto.role_dto import RoleCreateDTO, RoleUpdateDTO, RoleResponseDTO
from security.auth_middleware import require_role
from model.user import User
from typing import List

router = APIRouter()

@router.post("/roles", response_model=RoleResponseDTO)
async def create_new_role(
    role_data: RoleCreateDTO,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """
    Créer un nouveau rôle
    Accessible uniquement par l'admin
    """
    try:
        # Préparer les données pour la création
        role_dict = role_data.dict()
        
        # Créer le rôle
        new_role = await create_role(session, role_dict, current_user.id)
        
        return RoleResponseDTO.from_orm(new_role)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du rôle: {str(e)}"
        )

@router.get("/roles", response_model=List[RoleResponseDTO])
async def get_roles(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """
    Lister tous les rôles
    Accessible uniquement par l'admin
    """
    try:
        roles = await get_all_roles(session)
        return [RoleResponseDTO.from_orm(role) for role in roles]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des rôles: {str(e)}"
        )

@router.get("/roles/{role_id}", response_model=RoleResponseDTO)
async def get_role(
    role_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """
    Récupérer les détails d'un rôle
    Accessible uniquement par l'admin
    """
    try:
        role = await get_role_by_id(session, role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rôle non trouvé"
            )
        
        return RoleResponseDTO.from_orm(role)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du rôle: {str(e)}"
        )

@router.put("/roles/{role_id}", response_model=RoleResponseDTO)
async def update_role_endpoint(
    role_id: int,
    role_data: RoleUpdateDTO,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """
    Modifier un rôle existant
    Accessible uniquement par l'admin
    """
    try:
        # Préparer les données pour la mise à jour
        role_dict = role_data.dict(exclude_unset=True)
        
        # Mettre à jour le rôle
        updated_role = await update_role(session, role_id, role_dict)
        
        return RoleResponseDTO.from_orm(updated_role)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la modification du rôle: {str(e)}"
        )

@router.delete("/roles/{role_id}")
async def delete_role_endpoint(
    role_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """
    Supprimer un rôle
    Accessible uniquement par l'admin
    """
    try:
        success = await delete_role(session, role_id)
        
        if success:
            return {
                "message": "Rôle supprimé avec succès",
                "status": "success"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la suppression du rôle"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression du rôle: {str(e)}"
        ) 