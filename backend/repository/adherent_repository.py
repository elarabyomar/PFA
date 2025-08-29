from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from model.adherent import FlotteAuto, AssureSante, Marque, Carrosserie
from dto.adherent_dto import FlotteAutoCreate, FlotteAutoUpdate, AssureSanteCreate, AssureSanteUpdate
import logging

logger = logging.getLogger(__name__)

class FlotteAutoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, flotte_auto: FlotteAutoCreate) -> FlotteAuto:
        db_flotte_auto = FlotteAuto(**flotte_auto.dict())
        self.db.add(db_flotte_auto)
        await self.db.commit()
        await self.db.refresh(db_flotte_auto)
        return db_flotte_auto

    async def get_by_id(self, flotte_auto_id: int) -> Optional[FlotteAuto]:
        result = await self.db.execute(select(FlotteAuto).where(FlotteAuto.id == flotte_auto_id))
        return result.scalar_one_or_none()

    async def get_by_client_societe(self, client_societe_id: int) -> List[FlotteAuto]:
        result = await self.db.execute(
            select(FlotteAuto).where(FlotteAuto.idClientSociete == client_societe_id)
        )
        return result.scalars().all()

    async def update(self, flotte_auto_id: int, flotte_auto: FlotteAutoUpdate) -> Optional[FlotteAuto]:
        db_flotte_auto = await self.get_by_id(flotte_auto_id)
        if not db_flotte_auto:
            return None
        
        update_data = flotte_auto.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_flotte_auto, field, value)
        
        await self.db.commit()
        await self.db.refresh(db_flotte_auto)
        return db_flotte_auto

    async def delete(self, flotte_auto_id: int) -> bool:
        db_flotte_auto = await self.get_by_id(flotte_auto_id)
        if not db_flotte_auto:
            return False
        
        await self.db.delete(db_flotte_auto)
        await self.db.commit()
        return True

class AssureSanteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, assure_sante: AssureSanteCreate) -> AssureSante:
        db_assure_sante = AssureSante(**assure_sante.dict())
        self.db.add(db_assure_sante)
        await self.db.commit()
        await self.db.refresh(db_assure_sante)
        return db_assure_sante

    async def get_by_id(self, assure_sante_id: int) -> Optional[AssureSante]:
        result = await self.db.execute(select(AssureSante).where(AssureSante.id == assure_sante_id))
        return result.scalar_one_or_none()

    async def get_by_client_societe(self, client_societe_id: int) -> List[AssureSante]:
        result = await self.db.execute(
            select(AssureSante).where(AssureSante.idClientSociete == client_societe_id)
        )
        return result.scalars().all()

    async def update(self, assure_sante_id: int, assure_sante: AssureSanteUpdate) -> Optional[AssureSante]:
        db_assure_sante = await self.get_by_id(assure_sante_id)
        if not db_assure_sante:
            return None
        
        update_data = assure_sante.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_assure_sante, field, value)
        
        await self.db.commit()
        await self.db.refresh(db_assure_sante)
        return db_assure_sante

    async def delete(self, assure_sante_id: int) -> bool:
        db_assure_sante = await self.get_by_id(assure_sante_id)
        if not db_assure_sante:
            return False
        
        await self.db.delete(db_assure_sante)
        await self.db.commit()
        return True

class MarqueRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Marque]:
        result = await self.db.execute(select(Marque))
        return result.scalars().all()

class CarrosserieRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Carrosserie]:
        result = await self.db.execute(select(Carrosserie))
        return result.scalars().all()
