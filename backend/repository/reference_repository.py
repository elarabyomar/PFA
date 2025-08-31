from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import logging
from model.reference import Compagnie, Banque, Ville, Branche, Duree

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Reference repository module imported")
logger.info(f"🔍 Logger name: {__name__}")

class CompagnieRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_compagnies(self) -> List[Compagnie]:
        """Get all insurance companies"""
        try:
            result = await self.session.execute(select(Compagnie))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"❌ Error getting all compagnies: {e}")
            return []
    
    async def get_compagnie_by_code(self, code: str) -> Optional[Compagnie]:
        """Get compagnie by code"""
        try:
            result = await self.session.execute(
                select(Compagnie).where(Compagnie.codeCIE == code)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"❌ Error getting compagnie by code {code}: {e}")
            return None

class BanqueRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_banques(self) -> List[Banque]:
        """Get all banks"""
        try:
            result = await self.session.execute(select(Banque))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"❌ Error getting all banques: {e}")
            return []
    
    async def get_banque_by_code(self, code: str) -> Optional[Banque]:
        """Get banque by code"""
        try:
            result = await self.session.execute(
                select(Banque).where(Banque.codeBanques == code)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"❌ Error getting banque by code {code}: {e}")
            return None

class VilleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_villes(self) -> List[Ville]:
        """Get all cities"""
        try:
            result = await self.session.execute(select(Ville))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"❌ Error getting all villes: {e}")
            return []
    
    async def get_ville_by_code(self, code: str) -> Optional[Ville]:
        """Get ville by code"""
        try:
            result = await self.session.execute(
                select(Ville).where(Ville.codeVilles == code)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"❌ Error getting ville by code {code}: {e}")
            return None

class BrancheRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_branches(self) -> List[Branche]:
        """Get all branches"""
        try:
            result = await self.session.execute(select(Branche))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"❌ Error getting all branches: {e}")
            return []
    
    async def get_branche_by_code(self, code: str) -> Optional[Branche]:
        """Get branche by code"""
        try:
            result = await self.session.execute(
                select(Branche).where(Branche.codeBranche == code)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"❌ Error getting branche by code {code}: {e}")
            return None

class DureeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_durees(self) -> List[Duree]:
        """Get all duration types"""
        try:
            result = await self.session.execute(select(Duree))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"❌ Error getting all durees: {e}")
            return []
    
    async def get_duree_by_type(self, type_duree: str) -> Optional[Duree]:
        """Get duree by type"""
        try:
            result = await self.session.execute(
                select(Duree).where(Duree.libelle == type_duree)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"❌ Error getting duree by type {type_duree}: {e}")
            return None
    
    async def get_duree_by_months(self, nb_mois: int) -> Optional[Duree]:
        """Get duree by number of months"""
        try:
            result = await self.session.execute(
                select(Duree).where(Duree.nbMois == nb_mois)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"❌ Error getting duree by months {nb_mois}: {e}")
            return None
