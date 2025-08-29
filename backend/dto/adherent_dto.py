from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

class FlotteAutoBase(BaseModel):
    idClientSociete: int
    matricule: str
    idMarque: Optional[int] = None
    modele: str
    idCarrosserie: Optional[int] = None
    dateMiseCirculation: Optional[date] = None
    valeurNeuve: Optional[Decimal] = None
    valeurVenale: Optional[Decimal] = None

class FlotteAutoCreate(FlotteAutoBase):
    pass

class FlotteAutoUpdate(BaseModel):
    matricule: Optional[str] = None
    idMarque: Optional[int] = None
    modele: Optional[str] = None
    idCarrosserie: Optional[int] = None
    dateMiseCirculation: Optional[date] = None
    valeurNeuve: Optional[Decimal] = None
    valeurVenale: Optional[Decimal] = None

class FlotteAuto(FlotteAutoBase):
    id: int
    
    class Config:
        from_attributes = True

class AssureSanteBase(BaseModel):
    idClientSociete: int
    idClientParticulier: Optional[int] = None
    nom: str
    prenom: str
    cin: Optional[str] = None
    dateNaissance: Optional[date] = None
    numImmatriculation: Optional[str] = None
    categorie: Optional[str] = None
    lienParente: Optional[str] = None

class AssureSanteCreate(AssureSanteBase):
    pass

class AssureSanteUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    cin: Optional[str] = None
    dateNaissance: Optional[date] = None
    numImmatriculation: Optional[str] = None
    categorie: Optional[str] = None
    lienParente: Optional[str] = None

class AssureSante(AssureSanteBase):
    id: int
    
    class Config:
        from_attributes = True

class MarqueBase(BaseModel):
    codeMarques: str
    libelle: str

class MarqueCreate(MarqueBase):
    pass

class Marque(MarqueBase):
    id: int
    
    class Config:
        from_attributes = True

class CarrosserieBase(BaseModel):
    codeCarrosseries: str
    libelle: str

class CarrosserieCreate(CarrosserieBase):
    pass

class Carrosserie(CarrosserieBase):
    id: int
    
    class Config:
        from_attributes = True
