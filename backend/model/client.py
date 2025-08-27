from sqlalchemy import Column, Integer, String, Numeric, Text, Boolean, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Client(Base):
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codeClient = Column(String(50), unique=True, nullable=False)
    typeClient = Column(String(20), nullable=False)  # PARTICULIER/SOCIETE
    adresse = Column(String(255))
    tel = Column(String(50))
    email = Column(String(100))
    statut = Column(String(255))  # Opportunite/vrai client/ancien client
    importance = Column(String(255))
    budget = Column(String(255))
    proba = Column(String(255))
    
    # Relationships
    particulier = relationship("Particulier", back_populates="client", uselist=False)
    societe = relationship("Societe", back_populates="client", uselist=False)

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
    valeurTiers = Column(Integer)
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
    valeurTiers = Column(Integer)
    nomContactPrincipal = Column(String(255))
    fonctionContactPrincipal = Column(String(255))
    
    # Relationship
    client = relationship("Client", back_populates="societe")
