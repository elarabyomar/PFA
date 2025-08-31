from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import logging
from model.opportunity import Opportunity
from model.client import Client
from dto.opportunity_dto import OpportunityResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Opportunity repository module imported")
logger.info(f"🔍 Logger name: {__name__}")

class OpportunityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_opportunities_by_client(self, client_id: int) -> List[Opportunity]:
        """Get all opportunities for a specific client"""
        from sqlalchemy.orm import selectinload
        result = await self.session.execute(
            select(Opportunity)
            .options(selectinload(Opportunity.produit), selectinload(Opportunity.contract))
            .where(Opportunity.idClient == client_id)
        )
        return result.scalars().all()

    async def get_all_opportunities(self) -> List[Opportunity]:
        """Get all opportunities with client, produit, and contract information"""
        from sqlalchemy.orm import selectinload
        result = await self.session.execute(
            select(Opportunity)
            .options(
                selectinload(Opportunity.produit), 
                selectinload(Opportunity.contract),
                selectinload(Opportunity.client).selectinload(Client.particulier),
                selectinload(Opportunity.client).selectinload(Client.societe)
            )
            .order_by(Opportunity.id.desc())  # Newest first
        )
        return result.scalars().all()

    async def create_opportunity(self, opportunity_data: dict) -> Opportunity:
        """Create a new opportunity"""
        opportunity = Opportunity(**opportunity_data)
        self.session.add(opportunity)
        await self.session.commit()
        await self.session.refresh(opportunity)
        return opportunity

    async def update_opportunity(self, opportunity_id: int, opportunity_data: dict) -> Optional[Opportunity]:
        """Update an existing opportunity"""
        opportunity = await self.get_opportunity_by_id(opportunity_id)
        if opportunity:
            for key, value in opportunity_data.items():
                if hasattr(opportunity, key):
                    setattr(opportunity, key, value)
            await self.session.commit()
            await self.session.refresh(opportunity)
        return opportunity

    async def delete_opportunity(self, opportunity_id: int) -> bool:
        """Delete an opportunity"""
        logger.info(f"🔍 Starting deletion of opportunity {opportunity_id}")
        
        opportunity = await self.get_opportunity_by_id(opportunity_id)
        if opportunity:
            logger.info(f"✅ Found opportunity {opportunity_id} to delete")
            logger.info(f"📋 Opportunity details: idClient={opportunity.idClient}, idUser={opportunity.idUser}, transformed={opportunity.transformed}")
            
            try:
                # Delete the opportunity
                logger.info(f"🗑️ Deleting opportunity {opportunity_id} from session...")
                await self.session.delete(opportunity)
                
                logger.info(f"💾 Committing deletion to database...")
                await self.session.commit()
                logger.info(f"✅ Commit completed successfully")
                
                # Verify the deletion actually worked by checking the database
                logger.info(f"🔍 Verifying deletion by checking database directly...")
                verification_result = await self.session.execute(
                    select(Opportunity).where(Opportunity.id == opportunity_id)
                )
                verification_opportunity = verification_result.scalars().first()
                
                if verification_opportunity:
                    logger.error(f"❌ CRITICAL: Opportunity {opportunity_id} still exists after deletion!")
                    logger.error(f"❌ This means the deletion was rolled back or failed silently")
                    logger.error(f"❌ Verification query returned: {verification_opportunity.id}")
                    return False
                else:
                    logger.info(f"✅ Verification successful: Opportunity {opportunity_id} no longer exists in database")
                
                logger.info(f"✅ Opportunity {opportunity_id} deleted successfully from database")
                return True
                
            except Exception as e:
                logger.error(f"❌ Error deleting opportunity {opportunity_id}: {e}")
                logger.error(f"❌ Error type: {type(e).__name__}")
                import traceback
                logger.error(f"❌ Full traceback: {traceback.format_exc()}")
                
                try:
                    await self.session.rollback()
                    logger.info(f"🔄 Session rolled back after error")
                except Exception as rollback_error:
                    logger.error(f"❌ Failed to rollback session: {rollback_error}")
                
                return False
        else:
            logger.warning(f"⚠️ Opportunity {opportunity_id} not found for deletion")
            return False

    async def get_opportunity_by_id(self, opportunity_id: int) -> Optional[Opportunity]:
        """Get a single opportunity by ID"""
        from sqlalchemy.orm import selectinload
        result = await self.session.execute(
            select(Opportunity)
            .options(selectinload(Opportunity.produit), selectinload(Opportunity.contract))
            .where(Opportunity.id == opportunity_id)
        )
        return result.scalars().first()
