from sqlalchemy.ext.asyncio import AsyncSession
from repository.user_repository import UserRepository
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_email(session: AsyncSession, email: str):
    """Récupère un utilisateur par son email via le repository"""
    user_repo = UserRepository(session)
    return await user_repo.get_user_by_email(email)

async def authenticate_user(session: AsyncSession, email: str, password: str):
    """Authentifie un utilisateur avec email et mot de passe"""
    user_repo = UserRepository(session)
    user = await user_repo.get_user_by_email(email)
    
    if not user:
        return None
    
    # Vérifier d'abord si c'est un mot de passe par défaut
    # Mais seulement si l'utilisateur n'a pas encore changé son mot de passe
    if not user.password_changed and is_default_password(user, password):
        return user
    
    # Sinon, vérifier avec bcrypt
    if pwd_context.verify(password, user.password):
        return user
    
    return None

def is_default_password(user, password: str) -> bool:
    """Vérifie si le mot de passe est la date de naissance ou 'admin' (mots de passe par défaut)"""
    if not user:
        return False
    
    # Vérifier si c'est le mot de passe "admin"
    if password == "admin":
        return True
    
    # Vérifier si c'est la date de naissance au format YYYYMMDD
    if user.date_naissance:
        date_str = user.date_naissance.strftime("%Y%m%d")  # Format YYYYMMDD sans tirets
        if password == date_str:
            return True
    
    return False

async def change_password(session: AsyncSession, user_id: int, current_password: str, new_password: str):
    """Change le mot de passe d'un utilisateur"""
    user_repo = UserRepository(session)
    user = await user_repo.get_user_by_id(user_id)
    
    if not user:
        return False, "Utilisateur non trouvé"
    
    # Vérifier le mot de passe actuel
    # Si c'est un mot de passe par défaut, on l'accepte directement
    if is_default_password(user, current_password):
        # Le mot de passe par défaut est valide
        pass
    elif not pwd_context.verify(current_password, user.password):
        return False, "Mot de passe actuel incorrect"
    
    # Hasher le nouveau mot de passe
    hashed_password = pwd_context.hash(new_password)
    
    # Mettre à jour le mot de passe et marquer comme changé
    user_data = {
        "password": hashed_password,
        "password_changed": True,
        "updated_at": datetime.utcnow()
    }
    
    await user_repo.update_user(user_id, user_data)
    return True, "Mot de passe changé avec succès"

