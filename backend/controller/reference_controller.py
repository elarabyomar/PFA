from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
from config.database.database import get_session
from service.reference_service import DureeService
from dto.reference_dto import DureeResponse
from service.reference_service import CompagnieService
from dto.reference_dto import CompagnieResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Reference controller module imported")
logger.info(f"🔍 Logger name: {__name__}")

router = APIRouter()

@router.get("/duree", response_model=List[DureeResponse], tags=["reference"])
async def get_all_durees(db: AsyncSession = Depends(get_session)):
    """Get all duration types"""
    try:
        logger.info("🔍 GET /duree endpoint called")
        service = DureeService(db)
        durees = await service.get_all_durees()
        logger.info(f"✅ Successfully retrieved {len(durees)} durees")
        return durees
    except Exception as e:
        logger.error(f"❌ Error in get_all_durees: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/duree/type/{type_duree}", response_model=DureeResponse, tags=["reference"])
async def get_duree_by_type(type_duree: str, db: AsyncSession = Depends(get_session)):
    """Get duration type by name"""
    try:
        logger.info(f"🔍 GET /duree/type/{type_duree} endpoint called")
        service = DureeService(db)
        duree = await service.get_duree_by_type(type_duree)
        
        if duree:
            logger.info(f"✅ Successfully retrieved duree: {duree}")
            return duree
        else:
            logger.warning(f"⚠️ No duree found with type: {type_duree}")
            raise HTTPException(status_code=404, detail=f"Duration type '{type_duree}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in get_duree_by_type: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/duree/months/{nbre_mois}", response_model=DureeResponse, tags=["reference"])
async def get_duree_by_months(nbre_mois: int, db: AsyncSession = Depends(get_session)):
    """Get duration type by number of months"""
    try:
        logger.info(f"🔍 GET /duree/months/{nbre_mois} endpoint called")
        service = DureeService(db)
        duree = await service.get_duree_by_months(nbre_mois)
        
        if duree:
            logger.info(f"✅ Successfully retrieved duree: {duree}")
            return duree
        else:
            logger.warning(f"⚠️ No duree found with months: {nbre_mois}")
            raise HTTPException(status_code=404, detail=f"Duration type with {nbre_mois} months not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in get_duree_by_months: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/compagnies", response_model=List[CompagnieResponse], tags=["reference"])
async def get_all_compagnies(db: AsyncSession = Depends(get_session)):
    """Get all insurance companies"""
    try:
        logger.info("🔍 GET /compagnies endpoint called")
        service = CompagnieService(db)
        compagnies = await service.get_all_compagnies()
        logger.info(f"✅ Successfully retrieved {len(compagnies)} compagnies")
        return compagnies
    except Exception as e:
        logger.error(f"❌ Error in get_all_compagnies: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
