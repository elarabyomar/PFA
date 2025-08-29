from repository.adherent_repository import FlotteAutoRepository, AssureSanteRepository, MarqueRepository, CarrosserieRepository
from dto.adherent_dto import FlotteAutoCreate, FlotteAutoUpdate, AssureSanteCreate, AssureSanteUpdate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class FlotteAutoService:
    def __init__(self, db):
        self.db = db
        self.repository = FlotteAutoRepository(db)

    async def create_flotte_auto(self, flotte_auto: FlotteAutoCreate):
        return await self.repository.create(flotte_auto)

    async def get_flotte_auto_by_id(self, flotte_auto_id: int):
        return await self.repository.get_by_id(flotte_auto_id)

    async def get_flotte_auto_by_client_societe(self, client_societe_id: int):
        return await self.repository.get_by_client_societe(client_societe_id)

    async def update_flotte_auto(self, flotte_auto_id: int, flotte_auto: FlotteAutoUpdate):
        return await self.repository.update(flotte_auto_id, flotte_auto)

    async def delete_flotte_auto(self, flotte_auto_id: int):
        return await self.repository.delete(flotte_auto_id)

class AssureSanteService:
    def __init__(self, db):
        self.db = db
        self.repository = AssureSanteRepository(db)

    async def create_assure_sante(self, assure_sante: AssureSanteCreate):
        return await self.repository.create(assure_sante)

    async def get_assure_sante_by_id(self, assure_sante_id: int):
        return await self.repository.get_by_id(assure_sante_id)

    async def get_assure_sante_by_client_societe(self, client_societe_id: int):
        return await self.repository.get_by_client_societe(client_societe_id)

    async def update_assure_sante(self, assure_sante_id: int, assure_sante: AssureSanteUpdate):
        return await self.repository.update(assure_sante_id, assure_sante)

    async def delete_assure_sante(self, assure_sante_id: int):
        return await self.repository.delete(assure_sante_id)

class MarqueService:
    def __init__(self, db):
        self.db = db
        self.repository = MarqueRepository(db)

    async def get_all_marques(self):
        return await self.repository.get_all()

class CarrosserieService:
    def __init__(self, db):
        self.db = db
        self.repository = CarrosserieRepository(db)

    async def get_all_carrosseries(self):
        return await self.repository.get_all()
