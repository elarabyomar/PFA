from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class ClientBase(BaseModel):
    codeClient: str
    typeClient: str  # PARTICULIER/SOCIETE
    adresse: Optional[str] = None
    tel: Optional[str] = None
    email: Optional[str] = None
    statut: Optional[str] = None
    importance: Optional[str] = None
    budget: Optional[str] = None
    proba: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    codeClient: Optional[str] = None
    typeClient: Optional[str] = None
    adresse: Optional[str] = None
    tel: Optional[str] = None
    email: Optional[str] = None
    statut: Optional[str] = None
    importance: Optional[str] = None
    budget: Optional[str] = None
    proba: Optional[str] = None

class ClientResponse(ClientBase):
    id: int
    nom: str  # Computed field: nom+prenom for particulier, nom for societe
    
    class Config:
        from_attributes = True

class ParticulierBase(BaseModel):
    titre: Optional[str] = None
    nom: str
    prenom: str
    sexe: Optional[str] = None
    nationalite: Optional[str] = None
    lieuNaissance: Optional[str] = None
    dateNaissance: Optional[str] = None
    date_deces: Optional[str] = None
    datePermis: Optional[str] = None
    cin: Optional[str] = None
    profession: Optional[str] = None
    typeDocIdentite: Optional[str] = None
    situationFamiliale: Optional[str] = None
    nombreEnfants: Optional[int] = None
    valeurTiers: Optional[int] = None
    moyenContactPrefere: Optional[str] = None
    optoutTelephone: Optional[bool] = None
    optoutEmail: Optional[bool] = None

class ParticulierCreate(ParticulierBase):
    pass

class ParticulierUpdate(BaseModel):
    titre: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    sexe: Optional[str] = None
    nationalite: Optional[str] = None
    lieuNaissance: Optional[str] = None
    dateNaissance: Optional[str] = None
    date_deces: Optional[str] = None
    datePermis: Optional[str] = None
    cin: Optional[str] = None
    profession: Optional[str] = None
    typeDocIdentite: Optional[str] = None
    situationFamiliale: Optional[str] = None
    nombreEnfants: Optional[int] = None
    valeurTiers: Optional[int] = None
    moyenContactPrefere: Optional[str] = None
    optoutTelephone: Optional[bool] = None
    optoutEmail: Optional[bool] = None

class ParticulierResponse(ParticulierBase):
    idClient: int
    
    class Config:
        from_attributes = True

class SocieteBase(BaseModel):
    nom: str
    formeJuridique: Optional[str] = None
    capital: Optional[Decimal] = None
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
    dateCreationSociete: Optional[str] = None
    valeurTiers: Optional[int] = None
    nomContactPrincipal: Optional[str] = None
    fonctionContactPrincipal: Optional[str] = None

class SocieteCreate(SocieteBase):
    pass

class SocieteUpdate(BaseModel):
    nom: Optional[str] = None
    formeJuridique: Optional[str] = None
    capital: Optional[Decimal] = None
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
    dateCreationSociete: Optional[str] = None
    valeurTiers: Optional[int] = None
    nomContactPrincipal: Optional[str] = None
    fonctionContactPrincipal: Optional[str] = None

class SocieteResponse(SocieteBase):
    idClient: int
    
    class Config:
        from_attributes = True
