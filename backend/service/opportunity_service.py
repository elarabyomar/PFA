from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from repository.opportunity_repository import OpportunityRepository
from dto.opportunity_dto import OpportunityResponse, OpportunityCreate, OpportunityUpdate
from datetime import date

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Opportunity service module imported")
logger.info(f"🔍 Logger name: {__name__}")

class OpportunityService:
    def __init__(self, session: AsyncSession):
        self.repository = OpportunityRepository(session)

    async def get_opportunities_by_client(self, client_id: int) -> List[OpportunityResponse]:
        """Get all opportunities for a specific client"""
        opportunities = await self.repository.get_opportunities_by_client(client_id)
        opportunity_responses = []
        
        for opp in opportunities:
            # Convert to dict first to avoid async relationship issues
            opp_dict = {
                'id': opp.id,
                'idClient': opp.idClient,
                'idUser': opp.idUser,
                'idProduit': opp.idProduit,
                'budgetEstime': opp.budgetEstime,
                'origine': opp.origine,
                'etape': opp.etape,
                'dateCreation': opp.dateCreation,
                'dateEcheance': opp.dateEcheance,
                'description': opp.description
            }
            
            # Add produit data if available
            if hasattr(opp, 'produit') and opp.produit:
                opp_dict['produit'] = {
                    'id': opp.produit.id,
                    'codeProduit': opp.produit.codeProduit,
                    'libelle': opp.produit.libelle,
                    'description': opp.produit.description
                }
            
            opportunity_responses.append(OpportunityResponse(**opp_dict))
        
        return opportunity_responses

    async def create_opportunity(self, opportunity_data: OpportunityCreate) -> OpportunityResponse:
        """Create a new opportunity"""
        # Set default date if not provided
        if not opportunity_data.dateCreation:
            opportunity_data.dateCreation = date.today()
        
        opportunity = await self.repository.create_opportunity(opportunity_data.dict())
        
        # Convert to dict first to avoid async relationship issues
        opportunity_dict = {
            'id': opportunity.id,
            'idClient': opportunity.idClient,
            'idUser': opportunity.idUser,
            'idProduit': opportunity.idProduit,
            'budgetEstime': opportunity.budgetEstime,
            'origine': opportunity.origine,
            'etape': opportunity.etape,
            'dateCreation': opportunity.dateCreation,
            'dateEcheance': opportunity.dateEcheance,
            'description': opportunity.description
        }
        
        return OpportunityResponse(**opportunity_dict)

    async def update_opportunity(self, opportunity_id: int, opportunity_data: OpportunityUpdate) -> Optional[OpportunityResponse]:
        """Update an existing opportunity"""
        opportunity = await self.repository.update_opportunity(opportunity_id, opportunity_data.dict(exclude_unset=True))
        if opportunity:
            # Convert to dict first to avoid async relationship issues
            opportunity_dict = {
                'id': opportunity.id,
                'idClient': opportunity.idClient,
                'idUser': opportunity.idUser,
                'idProduit': opportunity.idProduit,
                'budgetEstime': opportunity.budgetEstime,
                'origine': opportunity.origine,
                'etape': opportunity.etape,
                'dateCreation': opportunity.dateCreation,
                'dateEcheance': opportunity.dateEcheance,
                'description': opportunity.description
            }
            return OpportunityResponse(**opportunity_dict)
        return None

    async def delete_opportunity(self, opportunity_id: int) -> bool:
        """Delete an opportunity"""
        return await self.repository.delete_opportunity(opportunity_id)

    async def get_opportunity_by_id(self, opportunity_id: int) -> Optional[OpportunityResponse]:
        """Get a single opportunity by ID"""
        opportunity = await self.repository.get_opportunity_by_id(opportunity_id)
        if opportunity:
            # Convert to dict first to avoid async relationship issues
            opportunity_dict = {
                'id': opportunity.id,
                'idClient': opportunity.idClient,
                'idUser': opportunity.idUser,
                'idProduit': opportunity.idProduit,
                'budgetEstime': opportunity.budgetEstime,
                'origine': opportunity.origine,
                'etape': opportunity.etape,
                'dateCreation': opportunity.dateCreation,
                'dateEcheance': opportunity.dateEcheance,
                'description': opportunity.description
            }
            return OpportunityResponse(**opportunity_dict)
        return None
