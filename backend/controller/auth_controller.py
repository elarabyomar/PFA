from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from config.database.database import async_session
from dto.user_dto import UserLoginDTO
from service.auth_service import get_user_by_email, authenticate_user
from security.auth_middleware import get_current_active_user
from passlib.hash import bcrypt
from jose import jwt
import os
from datetime import datetime, timedelta

router = APIRouter()

SECRET_KEY = os.getenv("JWT_SECRET", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def get_session():
    async with async_session() as session:
        yield session

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Crée un token JWT avec expiration"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login")
async def login(user: UserLoginDTO, session: AsyncSession = Depends(get_session)):
    """Endpoint de connexion utilisateur"""
    try:
        # Authentifier l'utilisateur
        authenticated_user = await authenticate_user(session, user.email, user.password)
        
        if not authenticated_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Email ou mot de passe incorrect"
            )
        
        # Vérifier si c'est la première connexion admin (mot de passe par défaut)
        default_password_hash = '$2b$12$CKQs0OA0wWxhglZFzVU/MeXxeTsOGlSlVOeq1ci51n0XPGjGiUPy.'
        is_first_login = authenticated_user.password == default_password_hash and authenticated_user.role == 'admin'
        
        # Créer le token d'accès
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token_data = {
            "sub": authenticated_user.email, 
            "user_id": authenticated_user.id, 
            "role": authenticated_user.role
        }
        
        access_token = create_access_token(
            data=token_data, 
            expires_delta=access_token_expires
        )
        
        response_data = {
            "access_token": access_token, 
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": authenticated_user.id,
                "nom": authenticated_user.nom,
                "prenom": authenticated_user.prenom,
                "email": authenticated_user.email,
                "date_naissance": str(authenticated_user.date_naissance),
                "role": authenticated_user.role
            }
        }
        
        # Ajouter un flag si c'est la première connexion admin
        if is_first_login:
            response_data["first_admin_login"] = True
            response_data["security_message"] = "Première connexion admin détectée. Veuillez changer le mot de passe par défaut."
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.get("/me")
async def get_current_user_info(current_user = Depends(get_current_active_user)):
    """Récupère les informations de l'utilisateur connecté"""
    return {
        "id": current_user.id,
        "nom": current_user.nom,
        "prenom": current_user.prenom,
        "email": current_user.email,
        "date_naissance": str(current_user.date_naissance),
        "role": current_user.role
    }

@router.get("/admin-info")
async def get_admin_info(session: AsyncSession = Depends(get_session)):
    """Récupère les informations de l'admin (sans le mot de passe)"""
    try:
        # Récupérer l'utilisateur admin
        admin_user = await get_user_by_email(session, "admin@gmail.com")
        
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur admin non trouvé"
            )
        
        return {
            "id": admin_user.id,
            "nom": admin_user.nom,
            "prenom": admin_user.prenom,
            "email": admin_user.email,
            "date_naissance": str(admin_user.date_naissance),
            "role": admin_user.role,
            "has_changed_password": admin_user.password != '$2b$12$CKQs0OA0wWxhglZFzVU/MeXxeTsOGlSlVOeq1ci51n0XPGjGiUPy.'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )
