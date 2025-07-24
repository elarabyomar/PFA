from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from passlib.context import CryptContext
from fastapi import HTTPException, status
from repository.user_repository import UserRepository
from repository.role_repository import RoleRepository
from typing import List, Optional
from datetime import datetime
from dto.user_dto import UserCreateDTO, UserUpdateDTO, UserResponseDTO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_password_from_date(date_naissance) -> str:
    """Génère un mot de passe au format YYYYMMDD à partir de la date de naissance"""
    return date_naissance.strftime("%Y%m%d")

def hash_password(password: str) -> str:
    """Hashe un mot de passe avec bcrypt"""
    return pwd_context.hash(password)

async def create_user(session: AsyncSession, user_data: UserCreateDTO) -> UserResponseDTO:
    """Créer un nouvel utilisateur"""
    user_repo = UserRepository(session)
    role_repo = RoleRepository(session)
    
    # Vérifier si l'email existe déjà
    if await user_repo.user_exists(user_data.email):
        raise ValueError("Un utilisateur avec cet email existe déjà")
    
    # Vérifier que tous les rôles existent
    for role_name in user_data.roles:
        role = await role_repo.get_role_by_name(role_name)
        if not role:
            raise ValueError(f"Le rôle '{role_name}' n'existe pas")
    
    # Générer le mot de passe si aucun n'est fourni
    if not user_data.password:
        generated_password = generate_password_from_date(user_data.date_naissance)
        hashed_password = pwd_context.hash(generated_password)
    else:
        generated_password = user_data.password
        hashed_password = pwd_context.hash(user_data.password)
    
    # Préparer les données utilisateur
    user_dict = user_data.dict()
    user_dict["password"] = hashed_password
    user_dict["role"] = user_data.roles[0] if user_data.roles else "user"  # Premier rôle comme rôle principal
    user_dict["roles"] = ",".join(user_data.roles)  # Rôles multiples séparés par des virgules
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    user_dict["password_changed"] = False  # L'utilisateur devra changer son mot de passe
    
    # Créer l'utilisateur
    user = await user_repo.create_user(user_dict)
    
    # Retourner l'utilisateur avec le mot de passe généré
    response = UserResponseDTO.from_orm(user)
    response.password = generated_password  # Ajouter le mot de passe en clair pour l'affichage
    
    return response

async def get_all_users(session: AsyncSession) -> List[UserResponseDTO]:
    """Récupérer tous les utilisateurs"""
    user_repo = UserRepository(session)
    users = await user_repo.get_all_users()
    return [UserResponseDTO.from_orm(user) for user in users]

async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[UserResponseDTO]:
    """Récupérer un utilisateur par son ID"""
    user_repo = UserRepository(session)
    user = await user_repo.get_user_by_id(user_id)
    return UserResponseDTO.from_orm(user) if user else None

async def update_user(session: AsyncSession, user_id: int, user_data: UserUpdateDTO) -> Optional[UserResponseDTO]:
    """Mettre à jour un utilisateur"""
    user_repo = UserRepository(session)
    role_repo = RoleRepository(session)
    
    # Vérifier si l'utilisateur existe
    existing_user = await user_repo.get_user_by_id(user_id)
    if not existing_user:
        return None
    
    # Vérifier si l'email existe déjà (sauf pour cet utilisateur)
    if user_data.email and await user_repo.user_exists(user_data.email, exclude_id=user_id):
        raise ValueError("Un utilisateur avec cet email existe déjà")
    
    # Préparer les données de mise à jour
    update_data = user_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    # Gérer les rôles si modifiés
    if "roles" in update_data and update_data["roles"]:
        # Vérifier que tous les rôles existent
        for role_name in update_data["roles"]:
            role = await role_repo.get_role_by_name(role_name)
            if not role:
                raise ValueError(f"Le rôle '{role_name}' n'existe pas")
        
        update_data["role"] = update_data["roles"][0]  # Premier rôle comme rôle principal
        update_data["roles"] = ",".join(update_data["roles"])  # Convertir en chaîne
    
    # Mettre à jour l'utilisateur
    updated_user = await user_repo.update_user(user_id, update_data)
    return UserResponseDTO.from_orm(updated_user) if updated_user else None

async def delete_user(session: AsyncSession, user_id: int) -> bool:
    """Supprimer un utilisateur"""
    user_repo = UserRepository(session)
    
    # Vérifier si l'utilisateur existe
    existing_user = await user_repo.get_user_by_id(user_id)
    if not existing_user:
        return False
    
    # Empêcher la suppression de l'admin principal
    if existing_user.email == "admin@gmail.com":
        raise ValueError("Impossible de supprimer l'administrateur principal")
    
    # Supprimer l'utilisateur
    return await user_repo.delete_user(user_id)

async def reset_user_password(session: AsyncSession, user_id: int) -> tuple[bool, str]:
    """Réinitialiser le mot de passe d'un utilisateur à sa date de naissance"""
    user_repo = UserRepository(session)
    
    # Récupérer l'utilisateur
    user = await user_repo.get_user_by_id(user_id)
    if not user:
        return False, "Utilisateur non trouvé"
    
    # Générer le nouveau mot de passe basé sur la date de naissance
    if not user.date_naissance:
        return False, "L'utilisateur n'a pas de date de naissance définie"
    
    # Format YYYYMMDD
    new_password = user.date_naissance.strftime("%Y%m%d")
    hashed_password = pwd_context.hash(new_password)
    
    # Mettre à jour le mot de passe
    update_data = {
        "password": hashed_password,
        "password_changed": False,  # L'utilisateur devra changer son mot de passe
        "updated_at": datetime.utcnow()
    }
    
    await user_repo.update_user(user_id, update_data)
    
    return True, f"Mot de passe réinitialisé avec succès. Le nouveau mot de passe est : {new_password}"

 