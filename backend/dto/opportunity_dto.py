from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Opportunity DTO module imported")
logger.info(f"🔍 Logger name: {__name__}")

class OpportunityBase(BaseModel):
    idClient: int
    idUser: int
    idProduit: Optional[int] = None
    budgetEstime: Optional[Decimal] = None
    origine: Optional[str] = None
    etape: Optional[str] = None
    dateCreation: Optional[date] = None
    dateEcheance: Optional[date] = None
    description: Optional[str] = None

class OpportunityCreate(OpportunityBase):
    pass

class OpportunityUpdate(BaseModel):
    idProduit: Optional[int] = None
    budgetEstime: Optional[Decimal] = None
    origine: Optional[str] = None
    etape: Optional[str] = None
    dateEcheance: Optional[date] = None
    description: Optional[str] = None

class OpportunityResponse(OpportunityBase):
    id: int
    produit: Optional[dict] = None  # Include produit relationship data
