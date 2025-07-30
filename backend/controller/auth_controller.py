from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from config.database.database import async_session
from dto.user_dto import UserLoginDTO, ChangePasswordDTO
from service.auth_service import authenticate_user, is_default_password, change_password
from security.auth_middleware import get_current_active_user, require_role
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
        
        # Vérifier si le mot de passe est la date de naissance (mot de passe par défaut)
        # Mais seulement si l'utilisateur n'a pas encore changé son mot de passe
        is_default = not authenticated_user.password_changed and is_default_password(authenticated_user, user.password)
        
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
                "role": authenticated_user.role,
                "password_changed": authenticated_user.password_changed
            },
            "requires_password_change": is_default
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )

@router.post("/change-password")
async def change_user_password(
    password_data: ChangePasswordDTO, 
    current_user = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session)
):
    """Endpoint pour changer le mot de passe"""
    try:
        # Vérifier que les mots de passe correspondent
        if password_data.new_password != password_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Les mots de passe ne correspondent pas"
            )
        
        # Changer le mot de passe
        success, message = await change_password(
            session, 
            current_user.id, 
            password_data.current_password, 
            password_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return {"message": message}
        
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
        "role": current_user.role,
        "password_changed": current_user.password_changed
    }

