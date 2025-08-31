from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
from service.opportunity_service import OpportunityService
from dto.opportunity_dto import OpportunityResponse, OpportunityCreate, OpportunityUpdate
from config.database.database import get_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Opportunity controller module imported")
logger.info(f"🔍 Logger name: {__name__}")

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])

@router.get("/", response_model=List[OpportunityResponse])
async def get_all_opportunities(session: AsyncSession = Depends(get_session)):
    """Get all opportunities with client information"""
    try:
        service = OpportunityService(session)
        opportunities = await service.get_all_opportunities()
        return opportunities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/client/{client_id}", response_model=List[OpportunityResponse])
async def get_opportunities_by_client(client_id: int, session: AsyncSession = Depends(get_session)):
    """Get all opportunities for a specific client"""
    try:
        service = OpportunityService(session)
        opportunities = await service.get_opportunities_by_client(client_id)
        return opportunities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=OpportunityResponse)
async def create_opportunity(opportunity_data: OpportunityCreate, session: AsyncSession = Depends(get_session)):
    """Create a new opportunity"""
    try:
        service = OpportunityService(session)
        opportunity = await service.create_opportunity(opportunity_data)
        return opportunity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: int, 
    opportunity_data: OpportunityUpdate, 
    session: AsyncSession = Depends(get_session)
):
    """Update an existing opportunity"""
    try:
        service = OpportunityService(session)
        opportunity = await service.update_opportunity(opportunity_id, opportunity_data)
        
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        return opportunity
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{opportunity_id}")
async def delete_opportunity(opportunity_id: int, session: AsyncSession = Depends(get_session)):
    """Delete an opportunity"""
    try:
        service = OpportunityService(session)
        success = await service.delete_opportunity(opportunity_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        return {"message": "Opportunity deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(opportunity_id: int, session: AsyncSession = Depends(get_session)):
    """Get a single opportunity by ID"""
    try:
        service = OpportunityService(session)
        opportunity = await service.get_opportunity_by_id(opportunity_id)
        
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        return opportunity
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
