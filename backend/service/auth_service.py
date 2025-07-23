from sqlalchemy.ext.asyncio import AsyncSession
from repository.user_repository import UserRepository
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_email(session: AsyncSession, email: str):
    """Récupère un utilisateur par son email via le repository"""
    user_repo = UserRepository(session)
    return await user_repo.get_user_by_email(email)

async def authenticate_user(session: AsyncSession, email: str, password: str):
    """Authentifie un utilisateur avec email et mot de passe"""
    user_repo = UserRepository(session)
    user = await user_repo.get_user_by_email(email)
    if user and pwd_context.verify(password, user.password):
        return user
    return None

