from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, text
from typing import List, Optional, Tuple
import logging
from model.document import Document, Adherent
from dto.document_dto import DocumentResponse, AdherentResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Document repository module imported")
logger.info(f"🔍 Logger name: {__name__}")

class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_document(self, document_data: dict) -> Document:
        """Create a new document"""
        logger.info("🔍 DocumentRepository.create_document() called")
        logger.info(f"📥 Document data received: {document_data}")
        logger.info(f"📥 Document data type: {type(document_data)}")
        
        try:
            logger.info("🔍 About to create Document instance...")
            logger.info(f"🔍 Document class: {Document}")
            logger.info(f"🔍 Document __module__: {Document.__module__}")
            logger.info(f"🔍 Document __name__: {Document.__name__}")
            
            # Check if the session can see the clients table
            try:
                result = await self.session.execute(text("SELECT COUNT(*) FROM clients"))
                client_count = result.scalar()
                logger.info(f"🔍 Clients table accessible, count: {client_count}")
            except Exception as table_error:
                logger.error(f"❌ Cannot access clients table: {table_error}")
                raise
            
            # Check if the session can see the documents table
            try:
                result = await self.session.execute(text("SELECT COUNT(*) FROM documents"))
                doc_count = result.scalar()
                logger.info(f"🔍 Documents table accessible, count: {doc_count}")
                
                # Also check the actual table structure
                result = await self.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'documents'"))
                columns = [row[0] for row in result.fetchall()]
                logger.info(f"🔍 Documents table columns: {columns}")
            except Exception as table_error:
                logger.error(f"❌ Cannot access documents table: {table_error}")
                raise
            
            logger.info("🔍 Creating Document instance with data...")
            document = Document(**document_data)
            logger.info(f"✅ Document instance created: {document}")
            
            logger.info("🔍 Adding document to session...")
            self.session.add(document)
            logger.info("✅ Document added to session")
            
            logger.info("🔍 Committing session...")
            await self.session.commit()
            logger.info("✅ Session committed")
            
            logger.info("🔍 Refreshing document...")
            await self.session.refresh(document)
            logger.info(f"✅ Document refreshed with ID: {document.id}")
            
            return document
        except Exception as e:
            logger.error(f"❌ DocumentRepository.create_document() failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            await self.session.rollback()
            raise

    async def create_adherent(self, adherent_data: dict) -> Adherent:
        """Create a new adherent"""
        logger.info("🔍 DocumentRepository.create_adherent() called")
        try:
            adherent = Adherent(**adherent_data)
            self.session.add(adherent)
            await self.session.commit()
            await self.session.refresh(adherent)
            logger.info(f"✅ Adherent created with ID: {adherent.id}")
            return adherent
        except Exception as e:
            logger.error(f"❌ DocumentRepository.create_adherent() failed: {str(e)}")
            await self.session.rollback()
            raise

    async def get_documents_by_client(self, client_id: int) -> List[Document]:
        """Get all documents for a specific client"""
        logger.info(f"🔍 DocumentRepository.get_documents_by_client() called for client_id: {client_id}")
        try:
            result = await self.session.execute(
                select(Document).where(Document.idEntite == client_id)  # CORRECTED: Use idEntite
            )
            documents = result.scalars().all()
            logger.info(f"✅ Found {len(documents)} documents for client {client_id}")
            return documents
        except Exception as e:
            logger.error(f"❌ DocumentRepository.get_documents_by_client() failed: {str(e)}")
            raise

    async def get_adherents_by_client(self, client_id: int) -> List[Adherent]:
        """Get all adherents for a specific client"""
        logger.info(f"🔍 DocumentRepository.get_adherents_by_client() called for client_id: {client_id}")
        try:
            result = await self.session.execute(
                select(Adherent).where(Adherent.idClientSociete == client_id)  # Use correct field name
            )
            adherents = result.scalars().all()
            logger.info(f"✅ Found {len(adherents)} adherents for client {client_id}")
            return adherents
        except Exception as e:
            logger.error(f"❌ DocumentRepository.get_adherents_by_client() failed: {str(e)}")
            raise

    async def delete_document(self, document_id: int) -> bool:
        """Delete a document"""
        logger.info(f"🔍 DocumentRepository.delete_document() called for document_id: {document_id}")
        try:
            result = await self.session.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()
            
            if document:
                await self.session.delete(document)
                await self.session.commit()
                logger.info(f"✅ Document {document_id} deleted successfully")
                return True
            else:
                logger.warning(f"⚠️ Document {document_id} not found")
                return False
        except Exception as e:
            logger.error(f"❌ DocumentRepository.delete_document() failed: {str(e)}")
            await self.session.rollback()
            raise

    async def get_documents_by_entity(self, entity_type: str, entity_id: int) -> List[Document]:
        """Get all documents for a specific entity (client, contract, etc.)"""
        logger.info(f"🔍 DocumentRepository.get_documents_by_entity() called for entity_type: {entity_type}, entity_id: {entity_id}")
        try:
            result = await self.session.execute(
                select(Document).where(
                    and_(
                        Document.typeEntite == entity_type,
                        Document.idEntite == entity_id
                    )
                )
            )
            documents = result.scalars().all()
            logger.info(f"✅ Found {len(documents)} documents for {entity_type} {entity_id}")
            return documents
        except Exception as e:
            logger.error(f"❌ DocumentRepository.get_documents_by_entity() failed: {str(e)}")
            raise

    async def link_document_to_entity(self, document_id: int, entity_type: str, entity_id: int) -> bool:
        """Link a document to an entity"""
        logger.info(f"🔍 DocumentRepository.link_document_to_entity() called for document_id: {document_id}, entity_type: {entity_type}, entity_id: {entity_id}")
        try:
            result = await self.session.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()
            
            if document:
                document.typeEntite = entity_type
                document.idEntite = entity_id
                await self.session.commit()
                logger.info(f"✅ Document {document_id} linked to {entity_type} {entity_id}")
                return True
            else:
                logger.warning(f"⚠️ Document {document_id} not found")
                return False
        except Exception as e:
            logger.error(f"❌ DocumentRepository.link_document_to_entity() failed: {str(e)}")
            await self.session.rollback()
            raise
