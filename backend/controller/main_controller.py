from fastapi import APIRouter, Depends
from security.auth_middleware import get_current_active_user
from model.user import User

router = APIRouter()

@router.get("/home")
async def get_home_page(current_user: User = Depends(get_current_active_user)):
    """Page principale - accessible uniquement avec un token JWT valide"""
    return {
        "message": "Bienvenue sur la page principale !",
        "user": {
            "id": current_user.id,
            "nom": current_user.nom,
            "prenom": current_user.prenom,
            "email": current_user.email,
            "date_naissance": str(current_user.date_naissance),
            "role": current_user.role
        },
        "page_content": {
            "title": "Page Principale",
            "description": "Cette page est protégée par authentification JWT",
            "status": "connecté"
        }
    } 