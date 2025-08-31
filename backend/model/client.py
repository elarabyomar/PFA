from sqlalchemy import Column, Integer, String, Numeric, Text, Boolean, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Client model module imported")
logger.info(f"🔍 Logger name: {__name__}")

Base = declarative_base()
logger.info("🔍 Client Base declarative_base created")


class Client(Base):
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codeClient = Column(String(50), unique=True, nullable=False)
    typeClient = Column(String(20), nullable=False)  # PARTICULIER/SOCIETE
    adresse = Column(String(255))
    tel = Column(String(50))
    email = Column(String(100))
    importance = Column(String(255))
    budget = Column(Numeric(15, 2))
    proba = Column(String(255))
    
    # Relationships - explicitly specify foreign keys to avoid ambiguity
    particulier = relationship("Particulier", back_populates="client", uselist=False, foreign_keys="Particulier.idClient")
    societe = relationship("Societe", back_populates="client", uselist=False, foreign_keys="Societe.idClient")
    

    
    # Document and Adherent relationships - removed to avoid circular imports
    # These will be handled through foreign keys only

class Particulier(Base):
    __tablename__ = 'particuliers'
    
    idClient = Column(Integer, ForeignKey('clients.id'), primary_key=True)
    titre = Column(String(20))
    nom = Column(String(255), nullable=False)
    prenom = Column(String(255), nullable=False)
    sexe = Column(String(10))
    nationalite = Column(String(100))
    lieuNaissance = Column(String(100))
    dateNaissance = Column(Date)
    date_deces = Column(Date)
    datePermis = Column(Date)
    cin = Column(String(255))
    profession = Column(String(100))
    typeDocIdentite = Column(String(50))
    situationFamiliale = Column(String(20))
    nombreEnfants = Column(Integer)
    moyenContactPrefere = Column(String(20))
    optoutTelephone = Column(Boolean)
    optoutEmail = Column(Boolean)
    
    # Relationship
    client = relationship("Client", back_populates="particulier")

class Societe(Base):
    __tablename__ = 'societes'
    
    idClient = Column(Integer, ForeignKey('clients.id'), primary_key=True)
    nom = Column(String(255), nullable=False)
    formeJuridique = Column(String(255))
    capital = Column(Numeric(15, 2))
    registreCom = Column(String(20))
    taxePro = Column(String(20))
    idFiscal = Column(String(20))
    CNSS = Column(String(20))
    ICE = Column(String(20))
    siteWeb = Column(String(20))
    societeMere = Column(Integer, ForeignKey('clients.id'))
    raisonSociale = Column(String(255))
    sigle = Column(String(50))
    tribunalCommerce = Column(String(100))
    secteurActivite = Column(String(255))
    dateCreationSociete = Column(Date)
    nomContactPrincipal = Column(String(255))
    fonctionContactPrincipal = Column(String(255))
    
    # Relationships - be explicit about which foreign key to use
    client = relationship("Client", foreign_keys=[idClient], back_populates="societe")
    societe_mere = relationship("Client", foreign_keys=[societeMere], remote_side="Client.id")
