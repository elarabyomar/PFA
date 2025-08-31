from sqlalchemy import Column, Integer, String, Date, ForeignKey, Numeric
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
    typeContrat = Column(String(255))  # Duree ferme / Duree campagne
    dateDebut = Column(Date, nullable=False)
    dateFin = Column(Date)
    idClient = Column(Integer, ForeignKey('clients.id'), nullable=False)
    idProduit = Column(Integer, ForeignKey('produits.id'), nullable=True)
    idCompagnie = Column(Integer, ForeignKey('compagnies.id'), nullable=True)  # Insurance company
    prime = Column(Numeric(15, 2), nullable=True)  # Annual premium
    idTypeDuree = Column(Integer, ForeignKey('duree.id'), nullable=True)  # Duration type
    
    # Relationships
    client = relationship("Client", foreign_keys=[idClient])
    produit = relationship("Produit", foreign_keys=[idProduit])
    compagnie = relationship("Compagnie", foreign_keys=[idCompagnie])
    duree = relationship("Duree", foreign_keys=[idTypeDuree])
    opportunity = relationship("Opportunity", back_populates="contract", uselist=False)
