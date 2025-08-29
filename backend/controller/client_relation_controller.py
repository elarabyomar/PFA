from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
from service.client_relation_service import ClientRelationService
from dto.client_relation_dto import ClientRelationResponse, ClientRelationCreate, ClientRelationUpdate, TypeRelationResponse, TypeRelationCreate
from config.database.database import get_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Client relation controller module imported")
logger.info(f"🔍 Logger name: {__name__}")

router = APIRouter(prefix="/api/client-relations", tags=["client-relations"])

@router.get("/client/{client_id}", response_model=List[ClientRelationResponse])
async def get_client_relations(client_id: int, session: AsyncSession = Depends(get_session)):
    """Get all relations for a specific client"""
    try:
        service = ClientRelationService(session)
        relations = await service.get_client_relations(client_id)
        return relations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=ClientRelationResponse)
async def create_client_relation(relation_data: ClientRelationCreate, session: AsyncSession = Depends(get_session)):
    """Create a new client relation"""
    try:
        service = ClientRelationService(session)
        relation = await service.create_client_relation(relation_data)
        return relation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{relation_id}", response_model=ClientRelationResponse)
async def update_client_relation(
    relation_id: int, 
    relation_data: ClientRelationUpdate, 
    session: AsyncSession = Depends(get_session)
):
    """Update an existing client relation"""
    try:
        service = ClientRelationService(session)
        relation = await service.update_client_relation(relation_id, relation_data)
        
        if not relation:
            raise HTTPException(status_code=404, detail="Client relation not found")
        
        return relation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{relation_id}")
async def delete_client_relation(relation_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a client relation"""
    try:
        service = ClientRelationService(session)
        success = await service.delete_client_relation(relation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Client relation not found")
        
        return {"message": "Client relation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{relation_id}", response_model=ClientRelationResponse)
async def get_client_relation(relation_id: int, session: AsyncSession = Depends(get_session)):
    """Get a single client relation by ID"""
    try:
        service = ClientRelationService(session)
        relation = await service.get_client_relation_by_id(relation_id)
        
        if not relation:
            raise HTTPException(status_code=404, detail="Client relation not found")
        
        return relation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/types/list", response_model=List[TypeRelationResponse])
async def get_type_relations(session: AsyncSession = Depends(get_session)):
    """Get all available type relations"""
    try:
        service = ClientRelationService(session)
        type_relations = await service.get_type_relations()
        return type_relations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/types/", response_model=TypeRelationResponse)
async def create_type_relation(type_relation_data: TypeRelationCreate, session: AsyncSession = Depends(get_session)):
    """Create a new type relation"""
    try:
        service = ClientRelationService(session)
        type_relation = await service.create_type_relation(type_relation_data)
        return type_relation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
