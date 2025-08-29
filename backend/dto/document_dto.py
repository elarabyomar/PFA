from pydantic import BaseModel, field_validator
from typing import Optional, List, Union
from datetime import date, datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Document DTO module imported")
logger.info(f"🔍 Logger name: {__name__}")

class DocumentBase(BaseModel):
    fichierNom: str
    typeEntite: Optional[str] = None
    idEntite: Optional[int] = None
    idDocType: Optional[int] = None
    fichierChemin: Optional[str] = None
    instantTele: Optional[datetime] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    fichierNom: Optional[str] = None
    typeEntite: Optional[str] = None
    idEntite: Optional[int] = None
    idDocType: Optional[int] = None
    fichierChemin: Optional[str] = None
    instantTele: Optional[datetime] = None

class DocumentResponse(DocumentBase):
    id: int
    
    class Config:
        from_attributes = True

class AdherentBase(BaseModel):
    idClientSociete: Optional[int] = None  # Link to client
    typeItemAssure: Optional[str] = None  # VEHICULE/PERSONNE_SANTE or CSV_IMPORT
    idItemAssure: Optional[int] = None  # FK to flotte_auto(id) or assure_sante(id)
    dateEntree: Optional[date] = None
    dateSortie: Optional[date] = None
    statut: Optional[str] = None  # ACTIF/INACTIF

class AdherentCreate(AdherentBase):
    pass

class AdherentUpdate(BaseModel):
    idClientSociete: Optional[int] = None  # Link to client
    typeItemAssure: Optional[str] = None  # VEHICULE/PERSONNE_SANTE or CSV_IMPORT
    idItemAssure: Optional[int] = None  # FK to flotte_auto(id) or assure_sante(id)
    dateEntree: Optional[date] = None
    dateSortie: Optional[date] = None
    statut: Optional[str] = None  # ACTIF/INACTIF

class AdherentResponse(AdherentBase):
    id: int
    
    class Config:
        from_attributes = True

class ClientCreateWithDocuments(BaseModel):
    # Client fields
    codeClient: str
    typeClient: str
    adresse: Optional[str] = None
    tel: Optional[str] = None
    email: Optional[str] = None
    statut: Optional[str] = None
    importance: Optional[str] = None
    budget: Optional[str] = None
    proba: Optional[str] = None
    
    # Particulier fields (if applicable)
    titre: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    sexe: Optional[str] = None
    nationalite: Optional[str] = None
    lieuNaissance: Optional[str] = None
    dateNaissance: Optional[date] = None
    date_deces: Optional[date] = None
    datePermis: Optional[date] = None
    cin: Optional[str] = None
    profession: Optional[str] = None
    typeDocIdentite: Optional[str] = None
    situationFamiliale: Optional[str] = None
    nombreEnfants: Optional[int] = None
    moyenContactPrefere: Optional[str] = None
    optoutTelephone: Optional[bool] = None
    optoutEmail: Optional[bool] = None
    
    # Societe fields (if applicable)
    nom: Optional[str] = None  # SOCIETE name field
    formeJuridique: Optional[str] = None
    capital: Optional[float] = None
    registreCom: Optional[str] = None
    taxePro: Optional[str] = None
    idFiscal: Optional[str] = None
    CNSS: Optional[str] = None
    ICE: Optional[str] = None
    siteWeb: Optional[str] = None
    societeMere: Optional[int] = None
    raisonSociale: Optional[str] = None
    sigle: Optional[str] = None
    tribunalCommerce: Optional[str] = None
    secteurActivite: Optional[str] = None
    dateCreationSociete: Optional[date] = None
    nomContactPrincipal: Optional[str] = None
    fonctionContactPrincipal: Optional[str] = None
    
    # Documents
    documents: Optional[List[Union[str, dict]]] = []  # List of document names or objects with originalName and filePath
    adherentsFile: Optional[str] = None  # CSV file name for adherents
    adherentsFilePath: Optional[str] = None  # CSV file path after upload
    

    
    @field_validator('dateNaissance', 'date_deces', 'datePermis', 'dateCreationSociete', mode='before')
    @classmethod
    def validate_date_fields(cls, v):
        if v is None or v == '':
            return None
        if isinstance(v, str):
            try:
                # Try to parse the date string
                if len(v) == 10:  # YYYY-MM-DD format
                    return datetime.strptime(v, '%Y-%m-%d').date()
                else:
                    return None
            except ValueError:
                return None
        return v
    
    @field_validator('nombreEnfants', 'societeMere', mode='before')
    @classmethod
    def validate_integer_fields(cls, v):
        if v is None or v == '':
            return None
        if isinstance(v, str):
            try:
                return int(v) if v.strip() else None
            except ValueError:
                return None
        return v
    
    @field_validator('capital', mode='before')
    @classmethod
    def validate_float_fields(cls, v):
        if v is None or v == '':
            return None
        if isinstance(v, str):
            try:
                return float(v) if v.strip() else None
            except ValueError:
                return None
        return v
