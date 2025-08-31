from sqlalchemy import Column, Integer, String, Text, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from model.client import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Reference models module imported")
logger.info(f"🔍 Logger name: {__name__}")

class Compagnie(Base):
    __tablename__ = 'compagnies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codeCIE = Column(String(10), unique=True, nullable=False)  # Fixed: was codeCompagnie, should be codeCIE
    nom = Column(String(255), nullable=False)  # Fixed: was libelle, should be nom
    adresse = Column(String(255), nullable=True)
    contact = Column(String(255), nullable=True)  # Fixed: was tel, should be contact
    actif = Column(Boolean, nullable=False, default=True)  # Added: missing column
    # Removed email and siteWeb as they don't exist in the actual database structure

class Banque(Base):
    __tablename__ = 'banques'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codeBanques = Column(String(50), unique=True, nullable=False)  # Fixed: was codeBanque, should be codeBanques
    libelle = Column(String(255), nullable=False)
    # Removed adresse, tel, email, siteWeb as they don't exist in the actual database structure

class Ville(Base):
    __tablename__ = 'villes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codeVilles = Column(String(50), unique=True, nullable=False)  # Fixed: was codeVille, should be codeVilles
    libelle = Column(String(255), nullable=False)
    # Removed codePays and region as they don't exist in the actual database structure

class Branche(Base):
    __tablename__ = 'branches'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codeBranche = Column(String(50), unique=True, nullable=False)
    libelle = Column(String(255), nullable=False)
    # Removed description as it doesn't exist in the actual database structure
    
    # Relationships - will be added later if needed

class Duree(Base):
    __tablename__ = 'duree'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codeDuree = Column(String(50), unique=True, nullable=False)  # Code type de duree
    libelle = Column(String(50), nullable=False)  # Type de duree
    nbMois = Column(Integer, nullable=False)  # Nombre de mois
