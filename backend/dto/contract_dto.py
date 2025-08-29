from pydantic import BaseModel, field_validator
from typing import Optional, Union
from datetime import date, datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Contract DTO module imported")
logger.info(f"🔍 Logger name: {__name__}")

class ContractBase(BaseModel):
    numPolice: str
    typeContrat: str = "Duree ferme"  # Default value: "Duree ferme" or "Duree campagne"
    dateDebut: date
    dateFin: Optional[date] = None
    idClient: int
    idProduit: Optional[int] = None
    
    @field_validator('dateDebut', 'dateFin', mode='before')
    @classmethod
    def validate_dates(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                try:
                    return datetime.fromisoformat(v).date()
                except ValueError:
                    raise ValueError(f'Invalid date format: {v}')
        elif isinstance(v, datetime):
            return v.date()
        elif isinstance(v, date):
            return v
        else:
            raise ValueError(f'Invalid date type: {type(v)}')
    
    class Config:
        from_attributes = True

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    numPolice: Optional[str] = None
    typeContrat: Optional[str] = None
    dateFin: Optional[date] = None
    idProduit: Optional[int] = None

class OpportunityTransformRequest(BaseModel):
    """DTO for transforming opportunity to contract"""
    typeContrat: str = "Duree ferme"
    dateFin: date  # Required field for transformation

class ContractResponse(ContractBase):
    id: int
    produit: Optional[dict] = None  # Include produit relationship data
