from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from model.user import User
from typing import Optional

class UserRepository:
    """Repository pour gérer l'accès aux données utilisateur"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Récupérer un utilisateur par son email"""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalars().first() 