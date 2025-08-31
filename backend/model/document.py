from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, LargeBinary, MetaData
from sqlalchemy.orm import relationship
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Document model module imported")
logger.info(f"🔍 Logger name: {__name__}")

# Use the same Base as other models to ensure proper foreign key resolution
from model.client import Base
logger.info("🔍 Document using shared Base from client model")

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    typeEntite = Column(String(255))  # Type d'entité (societé, particulier, contrat..)
    idEntite = Column(Integer, nullable=True)  # ID Entité - can be client ID, contract ID, etc.
    idDocType = Column(Integer, nullable=True)  # Id de type de doc (logo, CIN, Permis..) - Optional for now
    fichierNom = Column(String(255))  # Nom du fichier
    fichierChemin = Column(String(255))  # Chemin du fichier
    instantTele = Column(DateTime)  # Instant de telechargement
    
    # Relationships - we'll handle these dynamically based on typeEntite
    # client = relationship("Client", foreign_keys=[idEntite])
    # contract = relationship("Contract", foreign_keys=[idEntite])

class Adherent(Base):
    __tablename__ = 'adherents_contrat'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    idClientSociete = Column(Integer, ForeignKey('clients.id'), nullable=False)  # Keep this FK - essential for data integrity
    idProduction = Column(Integer, nullable=True)  # Remove FK constraint - can be added later
    typeItemAssure = Column(String(255))  # VEHICULE/PERSONNE_SANTE
    idItemAssure = Column(Integer, nullable=True)  # Remove FK constraint - can be added later
    dateEntree = Column(Date)
    dateSortie = Column(Date)
    statut = Column(String(255))  # ACTIF/INACTIF
    
    # Relationship - temporarily removed to fix SQLAlchemy initialization (same as Document model)
    # client = relationship("Client", foreign_keys=[idClientSociete])
