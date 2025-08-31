from pydantic import BaseModel
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Reference DTO module imported")
logger.info(f"🔍 Logger name: {__name__}")

class CompagnieBase(BaseModel):
    codeCIE: str
    nom: str
    adresse: Optional[str] = None
    contact: Optional[str] = None
    actif: bool = True

class CompagnieCreate(CompagnieBase):
    pass

class CompagnieUpdate(BaseModel):
    codeCIE: Optional[str] = None
    nom: Optional[str] = None
    adresse: Optional[str] = None
    contact: Optional[str] = None
    actif: Optional[bool] = None

class CompagnieResponse(CompagnieBase):
    id: int
    
    class Config:
        from_attributes = True

class BanqueBase(BaseModel):
    codeBanques: str
    libelle: str

class BanqueCreate(BanqueBase):
    pass

class BanqueUpdate(BaseModel):
    codeBanques: Optional[str] = None
    libelle: Optional[str] = None

class BanqueResponse(BanqueBase):
    id: int
    
    class Config:
        from_attributes = True

class VilleBase(BaseModel):
    codeVilles: str
    libelle: str

class VilleCreate(VilleBase):
    pass

class VilleUpdate(BaseModel):
    codeVilles: Optional[str] = None
    libelle: Optional[str] = None

class VilleResponse(VilleBase):
    id: int
    
    class Config:
        from_attributes = True

class BrancheBase(BaseModel):
    codeBranche: str
    libelle: str

class BrancheCreate(BrancheBase):
    pass

class BrancheUpdate(BaseModel):
    codeBranche: Optional[str] = None
    libelle: Optional[str] = None

class BrancheResponse(BrancheBase):
    id: int
    
    class Config:
        from_attributes = True

class DureeBase(BaseModel):
    codeDuree: str
    libelle: str
    nbMois: int

class DureeCreate(DureeBase):
    pass

class DureeUpdate(BaseModel):
    codeDuree: Optional[str] = None
    libelle: Optional[str] = None
    nbMois: Optional[int] = None

class DureeResponse(DureeBase):
    id: int
    
    class Config:
        from_attributes = True
