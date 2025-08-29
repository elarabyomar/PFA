from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from model.client import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("🔍 Adherent model module imported")
logger.info(f"🔍 Logger name: {__name__}")

class FlotteAuto(Base):
    __tablename__ = 'flotte_auto'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    idClientSociete = Column(Integer, ForeignKey('clients.id'), nullable=False)
    matricule = Column(String(255), nullable=False)
    idMarque = Column(Integer, ForeignKey('marques.id'), nullable=True)
    modele = Column(String(255), nullable=False)
    idCarrosserie = Column(Integer, ForeignKey('carrosseries.id'), nullable=True)
    dateMiseCirculation = Column(Date, nullable=True)
    valeurNeuve = Column(Numeric(15, 2), nullable=True)
    valeurVenale = Column(Numeric(15, 2), nullable=True)
    
    # Relationships
    client_societe = relationship("Client", foreign_keys=[idClientSociete])
    marque = relationship("Marque", foreign_keys=[idMarque])
    carrosserie = relationship("Carrosserie", foreign_keys=[idCarrosserie])

class AssureSante(Base):
    __tablename__ = 'assure_sante'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    idClientSociete = Column(Integer, ForeignKey('clients.id'), nullable=False)
    idClientParticulier = Column(Integer, ForeignKey('clients.id'), nullable=True)
    nom = Column(String(255), nullable=False)
    prenom = Column(String(255), nullable=False)
    cin = Column(String(255), nullable=True)
    dateNaissance = Column(Date, nullable=True)
    numImmatriculation = Column(String(255), nullable=True)
    categorie = Column(String(255), nullable=True)  # CADRE/NON-CADRE/DIRIGEANT
    lienParente = Column(String(255), nullable=True)  # ASSURE_PRINCIPAL/CONJOINT/ENFANT
    
    # Relationships
    client_societe = relationship("Client", foreign_keys=[idClientSociete])
    client_particulier = relationship("Client", foreign_keys=[idClientParticulier])

class Marque(Base):
    __tablename__ = 'marques'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codeMarques = Column(String(50), unique=True, nullable=False)
    libelle = Column(String(255), nullable=False)

class Carrosserie(Base):
    __tablename__ = 'carrosseries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codeCarrosseries = Column(String(50), unique=True, nullable=False)
    libelle = Column(String(255), nullable=False)
