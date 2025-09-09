from pydantic import BaseModel, field_validator, field_serializer
from typing import Optional, Union
from datetime import date, datetime
from decimal import Decimal
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
    idCompagnie: Optional[int] = None
    prime: Optional[Decimal] = None
    idTypeDuree: Optional[int] = None
    
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
    
    @field_serializer('prime')
    def serialize_prime(self, value):
        """Serialize Decimal to float for JSON response"""
        if value is None:
            return None
        return float(value)
    
    class Config:
        from_attributes = True

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    numPolice: Optional[str] = None
    typeContrat: Optional[str] = None
    dateFin: Optional[date] = None
    idProduit: Optional[int] = None
    idCompagnie: Optional[int] = None
    prime: Optional[Decimal] = None
    idTypeDuree: Optional[int] = None

class OpportunityTransformRequest(BaseModel):
    """DTO for transforming opportunity to contract"""
    typeContrat: str = "Duree ferme"
    dateDebut: date  # Required field for transformation
    dateFin: date  # Required field for transformation
    prime: Optional[Decimal] = None
    idCompagnie: Optional[int] = None
    idTypeDuree: Optional[int] = None

class ContractResponse(ContractBase):
    id: int
    produit: Optional[dict] = None  # Include produit relationship data
    compagnie: Optional[dict] = None  # Include compagnie relationship data
    duree: Optional[dict] = None  # Include duree relationship data
    client: Optional[dict] = None  # Include client relationship data
