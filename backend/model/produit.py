from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from model.client import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Produit model module imported")
logger.info(f"🔍 Logger name: {__name__}")

class Produit(Base):
    __tablename__ = 'produits'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codeProduit = Column(String(50), unique=True, nullable=False)
    libelle = Column(String(255), nullable=False)
    codeGarantie = Column(String(50), ForeignKey('garanties.codeGarantie'), nullable=True)  # Fixed: was INT, should be VARCHAR(50)
    codeSousGarantie = Column(String(50), ForeignKey('sous_garanties.codeSousGarantie'), nullable=True)  # Fixed: was INT, should be VARCHAR(50)
    description = Column(Text)
    
    # No back_populates relationships to avoid circular dependencies

class Garantie(Base):
    __tablename__ = 'garanties'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codeGarantie = Column(String(50), unique=True, nullable=False)  # Fixed: was INT, should be VARCHAR(50)
    libelle = Column(String(255), nullable=False)
    # Removed idProduit as it creates circular dependency and isn't in the CSV structure
    
    # No back_populates relationships to avoid circular dependencies

class SousGarantie(Base):
    __tablename__ = 'sous_garanties'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codeSousGarantie = Column(String(50), unique=True, nullable=False)  # Fixed: was INT, should be VARCHAR(50)
    libelle = Column(String(255), nullable=False)
    idGarantie = Column(Integer, ForeignKey('garanties.id'), nullable=True)  # Fixed: was idGarantie, should be idGarantie
    
    # Relationships
    garantie = relationship("Garantie")
