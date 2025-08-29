from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from model.client import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Contract model module imported")
logger.info(f"🔍 Logger name: {__name__}")

class Contract(Base):
    __tablename__ = 'contrats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    numPolice = Column(String(255), nullable=False)
    typeContrat = Column(String(255))  # Duree ferme / Duree compagne
    dateDebut = Column(Date, nullable=False)
    dateFin = Column(Date)
    idClient = Column(Integer, ForeignKey('clients.id'), nullable=False)
    idProduit = Column(Integer, ForeignKey('produits.id'), nullable=True)
    
    # Relationships
    client = relationship("Client", foreign_keys=[idClient])
    produit = relationship("Produit", foreign_keys=[idProduit])
