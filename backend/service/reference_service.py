from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from repository.reference_repository import DureeRepository, CompagnieRepository
from dto.reference_dto import DureeResponse, CompagnieResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Reference service module imported")
logger.info(f"🔍 Logger name: {__name__}")

class DureeService:
    def __init__(self, session: AsyncSession):
        self.repository = DureeRepository(session)
    
    async def get_all_durees(self) -> List[DureeResponse]:
        """Get all duration types"""
        try:
            logger.info("🔍 DureeService.get_all_durees() called")
            durees = await self.repository.get_all_durees()
            logger.info(f"✅ Found {len(durees)} durees")
            
            # Convert to DTOs
            duree_responses = []
            for duree in durees:
                duree_response = DureeResponse(
                    id=duree.id,
                    codeDuree=duree.codeDuree,
                    libelle=duree.libelle,
                    nbMois=duree.nbMois
                )
                duree_responses.append(duree_response)
            
            return duree_responses
        except Exception as e:
            logger.error(f"❌ DureeService.get_all_durees() failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise
    
    async def get_duree_by_type(self, type_duree: str) -> Optional[DureeResponse]:
        """Get duration type by name"""
        try:
            logger.info(f"🔍 DureeService.get_duree_by_type() called with type: {type_duree}")
            duree = await self.repository.get_duree_by_type(type_duree)
            
            if duree:
                duree_response = DureeResponse(
                    id=duree.id,
                    codeDuree=duree.codeDuree,
                    libelle=duree.libelle,
                    nbMois=duree.nbMois
                )
                logger.info(f"✅ Found duree: {duree_response}")
                return duree_response
            else:
                logger.info(f"ℹ️ No duree found with type: {type_duree}")
                return None
        except Exception as e:
            logger.error(f"❌ DureeService.get_duree_by_type() failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise
    
    async def get_duree_by_months(self, nbre_mois: int) -> Optional[DureeResponse]:
        """Get duration type by number of months"""
        try:
            logger.info(f"🔍 DureeService.get_duree_by_months() called with months: {nbre_mois}")
            duree = await self.repository.get_duree_by_months(nbre_mois)
            
            if duree:
                duree_response = DureeResponse(
                    id=duree.id,
                    codeDuree=duree.codeDuree,
                    libelle=duree.libelle,
                    nbMois=duree.nbMois
                )
                logger.info(f"✅ Found duree: {duree_response}")
                return duree_response
            else:
                logger.info(f"ℹ️ No duree found with months: {nbre_mois}")
                return None
        except Exception as e:
            logger.error(f"❌ DureeService.get_duree_by_months() failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise


class CompagnieService:
    def __init__(self, session: AsyncSession):
        self.repository = CompagnieRepository(session)
    
    async def get_all_compagnies(self) -> List[CompagnieResponse]:
        """Get all insurance companies"""
        try:
            logger.info("🔍 CompagnieService.get_all_compagnies() called")
            compagnies = await self.repository.get_all_compagnies()
            logger.info(f"✅ Found {len(compagnies)} compagnies")
            
            # Convert to DTOs
            compagnie_responses = []
            for compagnie in compagnies:
                compagnie_response = CompagnieResponse(
                    id=compagnie.id,
                    codeCIE=compagnie.codeCIE,
                    nom=compagnie.nom,
                    adresse=compagnie.adresse,
                    contact=compagnie.contact,
                    actif=compagnie.actif
                )
                compagnie_responses.append(compagnie_response)
            
            return compagnie_responses
        except Exception as e:
            logger.error(f"❌ CompagnieService.get_all_compagnies() failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise
