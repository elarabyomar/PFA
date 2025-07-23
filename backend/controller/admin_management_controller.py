from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from config.database.database import async_session
from dto.admin_password_dto import AdminPasswordChangeDTO
from service.admin_management_service import change_admin_default_password, verify_admin_password_strength
from security.auth_middleware import get_current_active_user, require_role
from model.user import User
from pydantic import BaseModel

router = APIRouter()

class PasswordTestDTO(BaseModel):
    password: str

async def get_session():
    async with async_session() as session:
        yield session

@router.post("/test-password-strength")
async def test_admin_password_strength(
    password_data: PasswordTestDTO,
    current_user: User = Depends(require_role("admin"))
):
    """
    Teste la force d'un mot de passe admin selon les nouvelles règles strictes
    Accessible uniquement par l'admin
    """
    try:
        is_valid, message = verify_admin_password_strength(password_data.password)
        
        return {
            "is_valid": is_valid,
            "message": message,
            "password_length": len(password_data.password),
            "requirements": {
                "length": "Minimum 12 caractères",
                "categories": "Au moins 3 catégories parmi : majuscules, minuscules, chiffres, caractères spéciaux",
                "consecutive": "Pas plus de 2 caractères identiques consécutifs",
                "dictionary": "Pas de mots du dictionnaire commun",
                "sequences": "Pas de séquences communes (123, abc, etc.)",
                "repetition": "Pas de répétitions excessives de caractères"
            },
            "special_characters": "~!@#$%^&*_-+=`|\\(){}[]:;\"\"'<>,.?/",
            "tested_by": {
                "id": current_user.id,
                "email": current_user.email,
                "role": current_user.role
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du test de force du mot de passe: {str(e)}"
        )

@router.post("/change-admin-default-password")
async def change_admin_default_password_endpoint(
    password_data: AdminPasswordChangeDTO,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role("admin"))
):
    """
    Endpoint pour changer le mot de passe admin par défaut après le premier lancement
    Nécessite un token JWT valide d'un utilisateur admin
    """
    try:
        # Vérifier que les nouveaux mots de passe correspondent
        if password_data.new_admin_password != password_data.confirm_new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Les nouveaux mots de passe ne correspondent pas"
            )
        
        # Vérifier la force du nouveau mot de passe avec les nouvelles règles strictes
        is_valid, error_message = verify_admin_password_strength(password_data.new_admin_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        # Changer le mot de passe
        success = await change_admin_default_password(
            session,
            password_data.current_admin_password,
            password_data.new_admin_password
        )
        
        if success:
            return {
                "message": "Mot de passe admin changé avec succès",
                "status": "success"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du changement de mot de passe admin"
        ) 