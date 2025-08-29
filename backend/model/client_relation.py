from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from model.client import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Client relation model module imported")
logger.info(f"🔍 Logger name: {__name__}")

class ClientRelation(Base):
    __tablename__ = 'clients_relations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    idClientPrincipal = Column(Integer, ForeignKey('clients.id'), nullable=False)
    idClientLie = Column(Integer, ForeignKey('clients.id'), nullable=False)
    idTypeRelation = Column(Integer, ForeignKey('type_relation.id'), nullable=True)
    dateDebut = Column(Date)
    dateFin = Column(Date)
    description = Column(Text)
    
    # Relationships
    client_principal = relationship("Client", foreign_keys=[idClientPrincipal])
    client_lie = relationship("Client", foreign_keys=[idClientLie])
    type_relation = relationship("TypeRelation", foreign_keys=[idTypeRelation])

class TypeRelation(Base):
    __tablename__ = 'type_relation'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codeTypeRelation = Column(String(50))
    libelle = Column(String(255))
