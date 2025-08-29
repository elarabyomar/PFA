from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from service.csv_service import CSVService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/csv", tags=["csv"])

@router.get("/flotte-auto", response_model=List[Dict[str, Any]])
async def get_flotte_auto_csv():
    """Get all flotte_auto data from CSV"""
    try:
        csv_service = CSVService()
        return csv_service.load_flotte_auto_data()
    except Exception as e:
        logger.error(f"Error getting flotte_auto CSV data: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des données CSV")

@router.get("/flotte-auto/client/{client_societe_id}", response_model=List[Dict[str, Any]])
async def get_flotte_auto_by_client_csv(client_societe_id: int):
    """Get flotte_auto data from CSV filtered by client societe ID"""
    try:
        csv_service = CSVService()
        return csv_service.get_flotte_auto_by_client(client_societe_id)
    except Exception as e:
        logger.error(f"Error getting flotte_auto CSV data by client: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des données CSV")

@router.get("/assure-sante", response_model=List[Dict[str, Any]])
async def get_assure_sante_csv():
    """Get all assure_sante data from CSV"""
    try:
        csv_service = CSVService()
        return csv_service.load_assure_sante_data()
    except Exception as e:
        logger.error(f"Error getting assure_sante CSV data: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des données CSV")

@router.get("/assure-sante/client/{client_societe_id}", response_model=List[Dict[str, Any]])
async def get_assure_sante_by_client_csv(client_societe_id: int):
    """Get assure_sante data from CSV filtered by client societe ID"""
    try:
        csv_service = CSVService()
        return csv_service.get_assure_sante_by_client(client_societe_id)
    except Exception as e:
        logger.error(f"Error getting assure_sante CSV data by client: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des données CSV")
