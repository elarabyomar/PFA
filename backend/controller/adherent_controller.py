from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.database.database import get_session
from service.adherent_service import FlotteAutoService, AssureSanteService, MarqueService, CarrosserieService
from dto.adherent_dto import (
    FlotteAuto, FlotteAutoCreate, FlotteAutoUpdate,
    AssureSante, AssureSanteCreate, AssureSanteUpdate,
    Marque, Carrosserie
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/adherents", tags=["adherents"])

# Flotte Auto endpoints
@router.post("/flotte-auto", response_model=FlotteAuto, status_code=status.HTTP_201_CREATED)
async def create_flotte_auto(
    flotte_auto: FlotteAutoCreate,
    db: AsyncSession = Depends(get_session)
):
    try:
        service = FlotteAutoService(db)
        return await service.create_flotte_auto(flotte_auto)
    except Exception as e:
        logger.error(f"Error creating flotte auto: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création de la flotte auto")

@router.get("/flotte-auto/{flotte_auto_id}", response_model=FlotteAuto)
async def get_flotte_auto(
    flotte_auto_id: int,
    db: AsyncSession = Depends(get_session)
):
    try:
        service = FlotteAutoService(db)
        flotte_auto = await service.get_flotte_auto_by_id(flotte_auto_id)
        if not flotte_auto:
            raise HTTPException(status_code=404, detail="Flotte auto non trouvée")
        return flotte_auto
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting flotte auto: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération de la flotte auto")

@router.get("/flotte-auto/client/{client_societe_id}", response_model=List[FlotteAuto])
async def get_flotte_auto_by_client(
    client_societe_id: int,
    db: AsyncSession = Depends(get_session)
):
    try:
        service = FlotteAutoService(db)
        return await service.get_flotte_auto_by_client_societe(client_societe_id)
    except Exception as e:
        logger.error(f"Error getting flotte auto by client: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération de la flotte auto")

@router.put("/flotte-auto/{flotte_auto_id}", response_model=FlotteAuto)
async def update_flotte_auto(
    flotte_auto_id: int,
    flotte_auto: FlotteAutoUpdate,
    db: AsyncSession = Depends(get_session)
):
    try:
        service = FlotteAutoService(db)
        updated = await service.update_flotte_auto(flotte_auto_id, flotte_auto)
        if not updated:
            raise HTTPException(status_code=404, detail="Flotte auto non trouvée")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating flotte auto: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour de la flotte auto")

@router.delete("/flotte-auto/{flotte_auto_id}")
async def delete_flotte_auto(
    flotte_auto_id: int,
    db: AsyncSession = Depends(get_session)
):
    try:
        service = FlotteAutoService(db)
        success = await service.delete_flotte_auto(flotte_auto_id)
        if not success:
            raise HTTPException(status_code=404, detail="Flotte auto non trouvée")
        return {"message": "Flotte auto supprimée avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting flotte auto: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression de la flotte auto")

# Assure Sante endpoints
@router.post("/assure-sante", response_model=AssureSante, status_code=status.HTTP_201_CREATED)
async def create_assure_sante(
    assure_sante: AssureSanteCreate,
    db: AsyncSession = Depends(get_session)
):
    try:
        service = AssureSanteService(db)
        return await service.create_assure_sante(assure_sante)
    except Exception as e:
        logger.error(f"Error creating assure sante: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création de l'assuré santé")

@router.get("/assure-sante/{assure_sante_id}", response_model=AssureSante)
async def get_assure_sante(
    assure_sante_id: int,
    db: AsyncSession = Depends(get_session)
):
    try:
        service = AssureSanteService(db)
        assure_sante = await service.get_assure_sante_by_id(assure_sante_id)
        if not assure_sante:
            raise HTTPException(status_code=404, detail="Assuré santé non trouvé")
        return assure_sante
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting assure sante: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération de l'assuré santé")

@router.get("/assure-sante/client/{client_societe_id}", response_model=List[AssureSante])
async def get_assure_sante_by_client(
    client_societe_id: int,
    db: AsyncSession = Depends(get_session)
):
    try:
        service = AssureSanteService(db)
        return await service.get_assure_sante_by_client_societe(client_societe_id)
    except Exception as e:
        logger.error(f"Error getting assure sante by client: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération de l'assuré santé")

@router.put("/assure-sante/{assure_sante_id}", response_model=AssureSante)
async def update_assure_sante(
    assure_sante_id: int,
    assure_sante: AssureSanteUpdate,
    db: AsyncSession = Depends(get_session)
):
    try:
        service = AssureSanteService(db)
        updated = await service.update_assure_sante(assure_sante_id, assure_sante)
        if not updated:
            raise HTTPException(status_code=404, detail="Assuré santé non trouvé")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating assure sante: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour de l'assuré santé")

@router.delete("/assure-sante/{assure_sante_id}")
async def delete_assure_sante(
    assure_sante_id: int,
    db: AsyncSession = Depends(get_session)
):
    try:
        service = AssureSanteService(db)
        success = await service.delete_assure_sante(assure_sante_id)
        if not success:
            raise HTTPException(status_code=404, detail="Assuré santé non trouvé")
        return {"message": "Assuré santé supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting assure sante: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression de l'assuré santé")

# Reference data endpoints
@router.get("/marques", response_model=List[Marque])
async def get_marques(db: AsyncSession = Depends(get_session)):
    try:
        service = MarqueService(db)
        return await service.get_all_marques()
    except Exception as e:
        logger.error(f"Error getting marques: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des marques")

@router.get("/carrosseries", response_model=List[Carrosserie])
async def get_carrosseries(db: AsyncSession = Depends(get_session)):
    try:
        service = CarrosserieService(db)
        return await service.get_all_carrosseries()
    except Exception as e:
        logger.error(f"Error getting carrosseries: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des carrosseries")
