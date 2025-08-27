from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from service.client_service import ClientService
from dto.client_dto import ClientResponse, ClientCreate, ClientUpdate
from config.database.database import get_session

router = APIRouter(prefix="/api/clients", tags=["clients"])

@router.get("/", response_model=dict)
async def get_clients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term for filtering"),
    typeClient: Optional[str] = Query(None, description="Filter by client type"),
    statut: Optional[str] = Query(None, description="Filter by status"),
    importance: Optional[str] = Query(None, description="Filter by importance"),
    session: AsyncSession = Depends(get_session)
):
    """Get clients with pagination, search, and filtering"""
    try:
        service = ClientService(session)
        
        # Build filters
        filters = {}
        if typeClient:
            filters['typeClient'] = typeClient
        if statut:
            filters['statut'] = statut
        if importance:
            filters['importance'] = importance
        
        clients, total_count = await service.get_clients_paginated(
            skip=skip,
            limit=limit,
            search=search,
            filters=filters
        )
        
        return {
            "clients": clients,
            "total_count": total_count,
            "has_more": skip + limit < total_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: int, session: AsyncSession = Depends(get_session)):
    """Get a single client by ID"""
    try:
        service = ClientService(session)
        client = await service.get_client_by_id(client_id)
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        return client
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=ClientResponse)
async def create_client(client_data: ClientCreate, session: AsyncSession = Depends(get_session)):
    """Create a new client"""
    try:
        service = ClientService(session)
        client = await service.create_client(client_data)
        return client
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int, 
    client_data: ClientUpdate, 
    session: AsyncSession = Depends(get_session)
):
    """Update an existing client"""
    try:
        service = ClientService(session)
        client = await service.update_client(client_id, client_data)
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        return client
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{client_id}")
async def delete_client(client_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a client"""
    try:
        service = ClientService(session)
        success = await service.delete_client(client_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Client not found")
        
        return {"message": "Client deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/types/list", response_model=List[str])
async def get_client_types(session: AsyncSession = Depends(get_session)):
    """Get all available client types"""
    try:
        service = ClientService(session)
        return service.get_client_types()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statuts/list", response_model=List[str])
async def get_client_statuts(session: AsyncSession = Depends(get_session)):
    """Get all available client statuses"""
    try:
        service = ClientService(session)
        return service.get_client_statuts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/importance/list", response_model=List[str])
async def get_client_importance_levels(session: AsyncSession = Depends(get_session)):
    """Get all available importance levels"""
    try:
        service = ClientService(session)
        return service.get_client_importance_levels()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
