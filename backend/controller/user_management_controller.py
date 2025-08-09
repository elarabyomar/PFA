from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from config.database.database import get_session
from dto.user_dto import UserCreateDTO, UserUpdateDTO, UserResponseDTO
from service.user_management_service import (
    create_user, 
    get_all_users, 
    get_user_by_id, 
    update_user, 
    delete_user,
    reset_user_password
)
from security.auth_middleware import get_current_active_user, require_role
from typing import List

router = APIRouter()

@router.post("/users", response_model=UserResponseDTO)
async def create_new_user(
    user: UserCreateDTO, 
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_role("admin"))
):
    """Créer un nouvel utilisateur"""
    try:
        created_user = await create_user(session, user)
        return created_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/users", response_model=List[UserResponseDTO])
async def get_users(
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_role("admin"))
):
    """Récupérer tous les utilisateurs"""
    try:
        users = await get_all_users(session)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des utilisateurs"
        )

@router.get("/users/{user_id}", response_model=UserResponseDTO)
async def get_user(
    user_id: int, 
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_role("admin"))
):
    """Récupérer un utilisateur par son ID"""
    try:
        user = await get_user_by_id(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de l'utilisateur"
        )

@router.put("/users/{user_id}", response_model=UserResponseDTO)
async def update_existing_user(
    user_id: int, 
    user_data: UserUpdateDTO, 
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_role("admin"))
):
    """Mettre à jour un utilisateur"""
    try:
        updated_user = await update_user(session, user_id, user_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/users/{user_id}")
async def delete_existing_user(
    user_id: int, 
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_role("admin"))
):
    """Supprimer un utilisateur"""
    try:
        success = await delete_user(session, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        return {"message": "Utilisateur supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression de l'utilisateur"
        )

@router.post("/users/{user_id}/reset-password")
async def reset_user_password_endpoint(
    user_id: int, 
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_role("admin"))
):
    """Réinitialiser le mot de passe d'un utilisateur"""
    try:
        success, message = await reset_user_password(session, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message
            )
        return {"message": message}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la réinitialisation du mot de passe"
        )

 