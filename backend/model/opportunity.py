from sqlalchemy import Column, Integer, String, Numeric, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from model.client import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Opportunity model module imported")
logger.info(f"🔍 Logger name: {__name__}")

class Opportunity(Base):
    __tablename__ = 'opportunites'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    idClient = Column(Integer, ForeignKey('clients.id'), nullable=False)
    idUser = Column(Integer, ForeignKey('users.id'), nullable=False)
    idProduit = Column(Integer, ForeignKey('produits.id'), nullable=True)
    budgetEstime = Column(Numeric(12, 2))
    origine = Column(String(255))  # Prospection/Référencement/Campagne Marketing/Appel entrant
    etape = Column(String(255))  # Qualification/Analyse besoin/Proposition/Gagnée/Perdue
    dateCreation = Column(Date)
    dateEcheance = Column(Date)
    description = Column(Text)
    
    # Relationships
    client = relationship("Client", foreign_keys=[idClient])
    user = relationship("User", foreign_keys=[idUser])
    produit = relationship("Produit", foreign_keys=[idProduit])
