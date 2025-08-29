from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
from service.contract_service import ContractService
from dto.contract_dto import ContractResponse, ContractCreate, ContractUpdate, OpportunityTransformRequest
from config.database.database import get_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Contract controller module imported")
logger.info(f"🔍 Logger name: {__name__}")

router = APIRouter(prefix="/api/contracts", tags=["contracts"])

@router.get("/client/{client_id}", response_model=List[ContractResponse])
async def get_contracts_by_client(client_id: int, session: AsyncSession = Depends(get_session)):
    """Get all contracts for a specific client"""
    try:
        service = ContractService(session)
        contracts = await service.get_contracts_by_client(client_id)
        return contracts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=ContractResponse)
async def create_contract(contract_data: ContractCreate, session: AsyncSession = Depends(get_session)):
    """Create a new contract"""
    try:
        service = ContractService(session)
        contract = await service.create_contract(contract_data)
        return contract
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: int, 
    contract_data: ContractUpdate, 
    session: AsyncSession = Depends(get_session)
):
    """Update an existing contract"""
    try:
        service = ContractService(session)
        contract = await service.update_contract(contract_id, contract_data)
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        return contract
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{contract_id}")
async def delete_contract(contract_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a contract"""
    try:
        service = ContractService(session)
        success = await service.delete_contract(contract_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        return {"message": "Contract deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(contract_id: int, session: AsyncSession = Depends(get_session)):
    """Get a single contract by ID"""
    try:
        service = ContractService(session)
        contract = await service.get_contract_by_id(contract_id)
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        return contract
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transform-opportunity/{opportunity_id}", response_model=ContractResponse)
async def transform_opportunity_to_contract(
    opportunity_id: int, 
    contract_data: OpportunityTransformRequest, 
    session: AsyncSession = Depends(get_session)
):
    """Transform an opportunity to a contract"""
    try:
        service = ContractService(session)
        contract = await service.transform_opportunity_to_contract(opportunity_id, contract_data.dict())
        return contract
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
