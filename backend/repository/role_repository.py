from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from model.role import Role
from typing import Optional, List
from datetime import datetime

class RoleRepository:
    """Repository pour gérer l'accès aux données des rôles"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """Récupérer un rôle par son ID"""
        result = await self.session.execute(select(Role).where(Role.id == role_id))
        return result.scalars().first()
    
    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """Récupérer un rôle par son nom"""
        result = await self.session.execute(select(Role).where(Role.name == name))
        return result.scalars().first()
    
    async def get_all_roles(self) -> List[Role]:
        """Récupérer tous les rôles"""
        result = await self.session.execute(select(Role).order_by(Role.name))
        return result.scalars().all()
    
    async def get_active_roles(self) -> List[Role]:
        """Récupérer tous les rôles actifs"""
        result = await self.session.execute(select(Role).where(Role.is_active == True).order_by(Role.name))
        return result.scalars().all()
    
    async def create_role(self, role_data: dict) -> Role:
        """Créer un nouveau rôle"""
        role = Role(**role_data)
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return role
    
    async def update_role(self, role_id: int, role_data: dict) -> Optional[Role]:
        """Mettre à jour un rôle"""
        # Ajouter la date de mise à jour
        role_data["updated_at"] = datetime.utcnow()
        
        await self.session.execute(
            update(Role).where(Role.id == role_id).values(**role_data)
        )
        await self.session.commit()
        
        # Récupérer le rôle mis à jour
        return await self.get_role_by_id(role_id)
    
    async def delete_role(self, role_id: int) -> bool:
        """Supprimer un rôle"""
        result = await self.session.execute(delete(Role).where(Role.id == role_id))
        await self.session.commit()
        return result.rowcount > 0
    
    async def role_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """Vérifier si un rôle existe déjà"""
        query = select(Role).where(Role.name == name)
        if exclude_id:
            query = query.where(Role.id != exclude_id)
        
        result = await self.session.execute(query)
        return result.scalars().first() is not None 