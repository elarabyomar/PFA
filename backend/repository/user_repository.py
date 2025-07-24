from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from model.user import User
from typing import Optional, List
from datetime import datetime

class UserRepository:
    """Repository pour gérer l'accès aux données utilisateur"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Récupérer un utilisateur par son email"""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Récupérer un utilisateur par son ID"""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()
    
    async def get_all_users(self) -> List[User]:
        """Récupérer tous les utilisateurs"""
        result = await self.session.execute(select(User).order_by(User.created_at.desc()))
        return result.scalars().all()
    
    async def create_user(self, user_data: dict) -> User:
        """Créer un nouvel utilisateur"""
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        """Mettre à jour un utilisateur"""
        # Ajouter la date de mise à jour
        user_data["updated_at"] = datetime.utcnow()
        
        await self.session.execute(
            update(User).where(User.id == user_id).values(**user_data)
        )
        await self.session.commit()
        
        # Récupérer l'utilisateur mis à jour
        return await self.get_user_by_id(user_id)
    
    async def delete_user(self, user_id: int) -> bool:
        """Supprimer un utilisateur"""
        result = await self.session.execute(delete(User).where(User.id == user_id))
        await self.session.commit()
        return result.rowcount > 0
    
    async def user_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Vérifier si un utilisateur existe déjà"""
        query = select(User).where(User.email == email)
        if exclude_id:
            query = query.where(User.id != exclude_id)
        
        result = await self.session.execute(query)
        return result.scalars().first() is not None 