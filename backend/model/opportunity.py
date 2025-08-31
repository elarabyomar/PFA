from sqlalchemy import Column, Integer, String, Numeric, Text, Date, ForeignKey, Boolean
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
    budgetEstime = Column(Numeric(15, 2), nullable=True)
    origine = Column(String(255), nullable=True)
    etape = Column(String(255), nullable=True)
    dateCreation = Column(Date, nullable=True)
    dateEcheance = Column(Date, nullable=True)
    description = Column(Text)
    transformed = Column(Boolean, default=False)  # Track if opportunity has been transformed to contract
    idContrat = Column(Integer, ForeignKey('contrats.id'), nullable=True)  # Reference to the created contract
    dateTransformation = Column(Date, nullable=True)  # Date when opportunity was transformed
    
    # Relationships
    client = relationship("Client", foreign_keys=[idClient])
    user = relationship("User", foreign_keys=[idUser])
    produit = relationship("Produit", foreign_keys=[idProduit])
    contract = relationship("Contract", foreign_keys=[idContrat], back_populates="opportunity")
