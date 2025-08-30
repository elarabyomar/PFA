from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import logging
from model.opportunity import Opportunity
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
            .options(selectinload(Opportunity.produit))
            .where(Opportunity.idClient == client_id)
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
        opportunity = await self.get_opportunity_by_id(opportunity_id)
        if opportunity:
            self.session.delete(opportunity)
            await self.session.commit()
            return True
        return False

    async def get_opportunity_by_id(self, opportunity_id: int) -> Optional[Opportunity]:
        """Get a single opportunity by ID"""
        from sqlalchemy.orm import selectinload
        result = await self.session.execute(
            select(Opportunity)
            .options(selectinload(Opportunity.produit))
            .where(Opportunity.id == opportunity_id)
        )
        return result.scalars().first()
