from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging
from service.client_service import ClientService
from dto.client_dto import ClientResponse, ClientCreate, ClientUpdate
from config.database.database import get_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Client controller module imported")
logger.info(f"🔍 Logger name: {__name__}")
logger.info(f"🔍 Logger level: {logger.level}")

router = APIRouter(prefix="/api/clients", tags=["clients"])

# Log router creation
logger.info(f"🔍 Creating client router with prefix: {router.prefix}")
logger.info(f"🔍 Client router tags: {router.tags}")

# Test endpoint to verify router is working
@router.get("/test")
async def test_client_router():
    """Test endpoint to verify client router is working"""
    logger.info("🧪 Test endpoint called - client router is working!")
    return {"message": "Client router is working!", "status": "success"}

# Specific routes must come BEFORE parameterized routes
@router.get("/types/list", response_model=List[str])
async def get_client_types(session: AsyncSession = Depends(get_session)):
    """Get all available client types"""
    logger.info("🔍 get_client_types endpoint called")
    try:
        logger.info("📦 Creating ClientService instance")
        service = ClientService(session)
        logger.info("🔄 Calling service.get_client_types()")
        result = await service.get_client_types()
        logger.info(f"✅ get_client_types successful, returning: {result}")
        return result
    except Exception as e:
        logger.error(f"❌ get_client_types failed with error: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/importance/list", response_model=List[str])
async def get_client_importance_levels(session: AsyncSession = Depends(get_session)):
    """Get all available client importance levels"""
    try:
        service = ClientService(session)
        return await service.get_client_importance_levels()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=dict)
async def get_clients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term for filtering"),
    typeClient: Optional[str] = Query(None, description="Filter by client type"),
    importance: Optional[str] = Query(None, description="Filter by importance"),
    session: AsyncSession = Depends(get_session)
):
    """Get clients with pagination, search, and filtering"""
    logger.info("🔍 get_clients endpoint called")
    logger.info(f"🔍 Query parameters: skip={skip}, limit={limit}, search='{search}', typeClient='{typeClient}', importance='{importance}'")
    
    try:
        logger.info("📦 Creating ClientService instance")
        service = ClientService(session)
        logger.info("✅ ClientService instance created")
        
        # Build filters
        filters = {}
        if typeClient:
            filters['typeClient'] = typeClient
            logger.info(f"🔍 Added typeClient filter: {typeClient}")

        if importance:
            filters['importance'] = importance
            logger.info(f"🔍 Added importance filter: {importance}")
        
        logger.info(f"🔍 Final filters: {filters}")
        
        logger.info("🔄 Calling service.get_clients_paginated()")
        clients, total_count = await service.get_clients_paginated(
            skip=skip,
            limit=limit,
            search=search,
            filters=filters
        )
        logger.info(f"✅ get_clients successful, returning: {len(clients)} clients, total_count={total_count}")
        
        return {
            "clients": clients,
            "total_count": total_count,
            "has_more": skip + limit < total_count
        }
    except Exception as e:
        logger.error(f"❌ get_clients failed with error: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
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

@router.get("/{client_id}/details", response_model=dict)
async def get_client_details(client_id: int, session: AsyncSession = Depends(get_session)):
    """Get detailed client information including particulier/societe data"""
    try:
        service = ClientService(session)
        client_details = await service.get_client_details(client_id)
        
        if not client_details:
            raise HTTPException(status_code=404, detail="Client not found")
        
        return client_details
    except HTTPException:
        raise
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
    logger.info(f"🗑️ DELETE /clients/{client_id} endpoint called")
    try:
        logger.debug(f"🔄 Creating ClientService for client {client_id}")
        service = ClientService(session)
        
        logger.debug(f"🔄 Calling service.delete_client({client_id})")
        success = await service.delete_client(client_id)
        
        if not success:
            logger.warning(f"⚠️ Client {client_id} not found for deletion")
            raise HTTPException(status_code=404, detail="Client not found")
        
        logger.info(f"✅ Client {client_id} deleted successfully")
        return {"message": "Client deleted successfully"}
    except HTTPException:
        logger.debug(f"🔄 Re-raising HTTPException for client {client_id}")
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting client {client_id}: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{client_id}/verify-cleanup")
async def verify_client_cleanup(client_id: int, session: AsyncSession = Depends(get_session)):
    """Verify that a deleted client has been properly cleaned up"""
    try:
        service = ClientService(session)
        is_clean = await service.verify_client_cleanup(client_id)
        
        if is_clean:
            return {"message": "Client cleanup verified successfully", "clean": True}
        else:
            return {"message": "Client cleanup verification failed", "clean": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup-orphaned-relations")
async def cleanup_orphaned_relations(session: AsyncSession = Depends(get_session)):
    """Force cleanup of any orphaned client relations (for maintenance purposes)"""
    try:
        service = ClientService(session)
        deleted_count = await service.force_cleanup_orphaned_relations()
        
        return {
            "message": f"Cleanup completed successfully",
            "deleted_relations": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
