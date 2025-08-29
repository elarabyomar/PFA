from pydantic import BaseModel
from typing import Optional
from datetime import date
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Client relation DTO module imported")
logger.info(f"🔍 Logger name: {__name__}")

class ClientRelationBase(BaseModel):
    idClientPrincipal: int
    idClientLie: int
    idTypeRelation: Optional[int] = None
    dateDebut: Optional[date] = None
    dateFin: Optional[date] = None
    description: Optional[str] = None

class ClientRelationCreate(ClientRelationBase):
    pass

class ClientRelationUpdate(BaseModel):
    idTypeRelation: Optional[int] = None
    dateDebut: Optional[date] = None
    dateFin: Optional[date] = None
    description: Optional[str] = None

class ClientRelationResponse(ClientRelationBase):
    id: int
    client_principal: Optional[dict] = None
    client_lie: Optional[dict] = None
    type_relation: Optional[dict] = None
    
    class Config:
        from_attributes = True

class TypeRelationBase(BaseModel):
    codeTypeRelation: str
    libelle: str

class TypeRelationCreate(TypeRelationBase):
    pass

class TypeRelationResponse(TypeRelationBase):
    id: int
    
    class Config:
        from_attributes = True
