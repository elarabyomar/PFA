from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
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

@router.get("/", response_model=List[ContractResponse])
async def get_all_contracts(session: AsyncSession = Depends(get_session)):
    """Get all contracts with client information"""
    try:
        service = ContractService(session)
        contracts = await service.get_all_contracts()
        return contracts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    dateDebut: str = Form(...),
    dateFin: str = Form(...),
    prime: Optional[str] = Form(None),
    idCompagnie: Optional[str] = Form(None),
    idTypeDuree: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session),
    document_0: Optional[UploadFile] = File(None),
    document_1: Optional[UploadFile] = File(None),
    document_2: Optional[UploadFile] = File(None),
    document_3: Optional[UploadFile] = File(None),
    document_4: Optional[UploadFile] = File(None)
):
    """Transform an opportunity to a contract"""
    try:
        # Build contract data
        from datetime import datetime
        
        # Convert string dates to date objects
        try:
            logger.info(f"📅 Converting dateDebut: '{dateDebut}' (type: {type(dateDebut)})")
            logger.info(f"📅 Converting dateFin: '{dateFin}' (type: {type(dateFin)})")
            
            date_debut = datetime.strptime(dateDebut, '%Y-%m-%d').date() if dateDebut else None
            date_fin = datetime.strptime(dateFin, '%Y-%m-%d').date() if dateFin else None
            
            logger.info(f"📅 Converted dateDebut: {date_debut} (type: {type(date_debut)})")
            logger.info(f"📅 Converted dateFin: {date_fin} (type: {type(date_fin)})")
        except ValueError as e:
            logger.error(f"❌ Date conversion error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD. Error: {str(e)}")
        
        contract_data = {
            'typeContrat': 'Duree ferme',  # Default contract type
            'dateDebut': date_debut,
            'dateFin': date_fin,
            'prime': float(prime) if prime else None,
            'idCompagnie': int(idCompagnie) if idCompagnie else None,
            'idTypeDuree': int(idTypeDuree) if idTypeDuree else None
        }
        
        logger.info(f"📋 Final contract_data: {contract_data}")
        
        # Convert files to document format
        document_files = []
        all_docs = [document_0, document_1, document_2, document_3, document_4]
        for doc in all_docs:
            if doc:
                document_files.append({
                    'name': doc.filename,
                    'file': doc  # Pass the actual file object instead of constructing path
                })
        
        service = ContractService(session)
        contract = await service.transform_opportunity_to_contract(opportunity_id, contract_data, document_files)
        return contract
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
