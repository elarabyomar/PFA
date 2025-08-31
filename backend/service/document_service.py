from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
from repository.document_repository import DocumentRepository
from dto.document_dto import DocumentResponse, AdherentResponse, ClientCreateWithDocuments
from model.client import Client, Particulier, Societe
from datetime import date, datetime
import os
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Document service module imported")
logger.info(f"🔍 Logger name: {__name__}")

class DocumentService:
    def __init__(self, session: AsyncSession):
        self.repository = DocumentRepository(session)

    async def create_client_with_documents(self, client_data: ClientCreateWithDocuments) -> dict:
        """Create a client with all related data and documents"""
        logger.info("🔍 DocumentService.create_client_with_documents() called")
        try:
            # Create the main client in FIRST transaction
            logger.info("🔄 Creating main client...")
            client = Client(
                codeClient=client_data.codeClient,
                typeClient=client_data.typeClient,
                adresse=client_data.adresse,
                tel=client_data.tel,
                email=client_data.email,
                importance=client_data.importance,
                budget=client_data.budget,
                proba=client_data.proba
            )
            self.repository.session.add(client)
            
            # COMMIT CLIENT FIRST to ensure it exists in database
            logger.info("🔄 Committing client to database...")
            await self.repository.session.commit()
            await self.repository.session.refresh(client)
            logger.info(f"✅ Main client created and committed with ID: {client.id}")
            
            # Verify client exists in database before proceeding
            try:
                result = await self.repository.session.execute(
                    text("SELECT id FROM clients WHERE id = :client_id"),
                    {"client_id": client.id}
                )
                client_check = result.scalar()
                if not client_check:
                    raise Exception(f"Client {client.id} was not properly created in database")
                logger.info(f"✅ Client {client.id} verified in database")
            except Exception as verify_error:
                logger.error(f"❌ Client verification failed: {verify_error}")
                raise

            # Create type-specific data
            if client_data.typeClient == 'PARTICULIER':
                logger.info("🔄 Creating particulier data...")
                particulier = Particulier(
                    idClient=client.id,
                    titre=client_data.titre,
                    nom=client_data.nom,
                    prenom=client_data.prenom,
                    sexe=client_data.sexe,
                    nationalite=client_data.nationalite,
                    lieuNaissance=client_data.lieuNaissance,
                    dateNaissance=client_data.dateNaissance,
                    date_deces=client_data.date_deces,
                    datePermis=client_data.datePermis,
                    cin=client_data.cin,
                    profession=client_data.profession,
                    typeDocIdentite=client_data.typeDocIdentite,
                    situationFamiliale=client_data.situationFamiliale,
                    nombreEnfants=client_data.nombreEnfants,
                    moyenContactPrefere=client_data.moyenContactPrefere,
                    optoutTelephone=client_data.optoutTelephone,
                    optoutEmail=client_data.optoutEmail
                )
                self.repository.session.add(particulier)
                
                # COMMIT PARTICULIER DATA to ensure it exists
                logger.info("🔄 Committing particulier data...")
                await self.repository.session.commit()
                logger.info("✅ Particulier data created and committed")

            elif client_data.typeClient == 'SOCIETE':
                logger.info("🔄 Creating societe data...")
                logger.info(f"📥 SOCIETE data received: nom={client_data.nom}, formeJuridique={client_data.formeJuridique}, capital={client_data.capital}")
                logger.info(f"📥 SOCIETE data received: registreCom={client_data.registreCom}, taxePro={client_data.taxePro}, idFiscal={client_data.idFiscal}")
                logger.info(f"📥 SOCIETE data received: CNSS={client_data.CNSS}, ICE={client_data.ICE}, siteWeb={client_data.siteWeb}")
                logger.info(f"📥 SOCIETE data received: societeMere={client_data.societeMere}, raisonSociale={client_data.raisonSociale}, sigle={client_data.sigle}")
                logger.info(f"📥 SOCIETE data received: tribunalCommerce={client_data.tribunalCommerce}, secteurActivite={client_data.secteurActivite}")
                logger.info(f"📥 SOCIETE data received: dateCreationSociete={client_data.dateCreationSociete}, nomContactPrincipal={client_data.nomContactPrincipal}, fonctionContactPrincipal={client_data.fonctionContactPrincipal}")
                
                societe = Societe(
                    idClient=client.id,
                    nom=client_data.nom,
                    formeJuridique=client_data.formeJuridique,
                    capital=client_data.capital,
                    registreCom=client_data.registreCom,
                    taxePro=client_data.taxePro,
                    idFiscal=client_data.idFiscal,
                    CNSS=client_data.CNSS,
                    ICE=client_data.ICE,
                    siteWeb=client_data.siteWeb,
                    societeMere=client_data.societeMere,
                    raisonSociale=client_data.raisonSociale,
                    sigle=client_data.sigle,
                    tribunalCommerce=client_data.tribunalCommerce,
                    secteurActivite=client_data.secteurActivite,
                    dateCreationSociete=client_data.dateCreationSociete,
                    nomContactPrincipal=client_data.nomContactPrincipal,
                    fonctionContactPrincipal=client_data.fonctionContactPrincipal
                )
                self.repository.session.add(societe)
                
                # COMMIT SOCIETE DATA to ensure it exists
                logger.info("🔄 Committing societe data...")
                await self.repository.session.commit()
                logger.info("✅ Societe data created and committed")

            # Create documents - ONLY AFTER client is fully committed
            if client_data.documents:
                logger.info(f"🔄 Creating {len(client_data.documents)} documents...")
                logger.info(f"📥 Documents list: {client_data.documents}")
                logger.info(f"📥 Client ID for documents: {client.id}")
                logger.info(f"📥 Client ID type: {type(client.id)}")
                
                # FINAL VERIFICATION: Ensure client exists before creating documents
                logger.info("🔍 Final verification: Checking client exists before document creation...")
                try:
                    result = await self.repository.session.execute(
                        text("SELECT COUNT(*) FROM clients WHERE id = :client_id"),
                        {"client_id": client.id}
                    )
                    client_count = result.scalar()
                    if client_count == 0:
                        raise Exception(f"Client {client.id} not found in database before document creation")
                    logger.info(f"✅ Client {client.id} confirmed in database (count: {client_count})")
                except Exception as final_verify_error:
                    logger.error(f"❌ Final client verification failed: {final_verify_error}")
                    raise
                
                for i, doc_data in enumerate(client_data.documents):
                    # Handle both old format (string) and new format (dict with originalName and filePath)
                    if isinstance(doc_data, dict):
                        # New format: document already uploaded with both original name and file path
                        original_name = doc_data.get('originalName', f'Document {i+1}')
                        file_path = doc_data.get('filePath', None)
                        
                        if not file_path:
                            logger.warning(f"⚠️ Document {original_name} missing file path, skipping...")
                            continue
                            
                        logger.info(f"✅ Document {original_name} already uploaded with path: {file_path}")
                        document_data = {
                            'fichierNom': original_name,  # Original filename for display
                            'fichierChemin': file_path,   # UUID filename for file serving
                            'typeEntite': client_data.typeClient,
                            'idDocType': None,
                            'idEntite': client.id,
                            'instantTele': datetime.now()
                        }
                    else:
                        # Old format: just filename (for backward compatibility)
                        doc_name = doc_data
                        logger.info(f"🔄 Creating document {i+1}/{len(client_data.documents)}: {doc_name}")
                        
                        # For CSV import documents, we don't create document records since they don't have actual files
                        # These are just references to processed data, not downloadable documents
                        if doc_name.endswith('.csv') or 'CSV' in doc_name.upper():
                            logger.info(f"ℹ️ Skipping CSV import document record creation for: {doc_name}")
                            logger.info(f"ℹ️ CSV import documents are processed data references, not downloadable files")
                            continue
                        
                        # Validate that this looks like a real document file
                        valid_file_pattern = re.compile(r'\.(pdf|doc|docx|xls|xlsx|txt|jpg|jpeg|png|gif|zip|rar)$', re.IGNORECASE)
                        if not valid_file_pattern.search(doc_name):
                            logger.warning(f"⚠️ Document {doc_name} doesn't appear to be a valid file type, skipping...")
                            logger.warning(f"⚠️ Only documents with valid file extensions are created as downloadable documents")
                            continue
                        
                        # This is a regular document name, create a reference (but it won't be downloadable)
                        logger.info(f"ℹ️ Document {doc_name} appears to be a reference without actual file upload")
                        document_data = {
                            'fichierNom': doc_name,
                            'fichierChemin': None,  # No actual file path available
                            'typeEntite': client_data.typeClient,
                            'idDocType': None,
                            'idEntite': client.id,
                            'instantTele': datetime.now()
                        }
                    
                    logger.info(f"📥 Document data to send: {document_data}")
                    
                    try:
                        document = await self.repository.create_document(document_data)
                        logger.info(f"✅ Document created successfully with ID: {document.id}")
                    except Exception as doc_error:
                        logger.error(f"❌ Failed to create document: {doc_error}")
                        raise
            else:
                logger.info("ℹ️ No documents to create")

            # Create adherents if CSV file provided
            if client_data.adherentsFile:
                logger.info(f"🔄 Processing adherents from file: {client_data.adherentsFile}")
                
                # FINAL VERIFICATION: Ensure client exists before creating adherents
                logger.info("🔍 Final verification: Checking client exists before adherent creation...")
                try:
                    result = await self.repository.session.execute(
                        text("SELECT COUNT(*) FROM clients WHERE id = :client_id"),
                        {"client_id": client.id}
                    )
                    client_count = result.scalar()
                    if client_count == 0:
                        raise Exception(f"Client {client.id} not found in database before adherent creation")
                    logger.info(f"✅ Client {client.id} confirmed in database (count: {client_count})")
                except Exception as final_verify_error:
                    logger.error(f"❌ Final client verification failed: {final_verify_error}")
                    raise
                
                # Create adherent record as a CSV import reference (like a document)
                adherent_data = {
                    'idClientSociete': client.id,  # Link to the client
                    'typeItemAssure': 'CSV_IMPORT',  # Mark as CSV import
                    'dateEntree': date.today(),  # Set entry date to today
                    'statut': 'ACTIF'  # Default status
                }
                
                try:
                    adherent = await self.repository.create_adherent(adherent_data)
                    logger.info(f"✅ Adherent CSV import reference created successfully with ID: {adherent.id}")
                except Exception as adherent_error:
                    logger.error(f"❌ Failed to create adherent CSV reference: {adherent_error}")
                    raise
                
                # Store CSV file as a document if available
                if client_data.adherentsFile:
                    logger.info(f"📁 Storing CSV file '{client_data.adherentsFile}' as document")
                    
                    try:
                        # Create document record for the CSV file
                        csv_document_data = {
                            'typeEntite': 'SOCIETE',
                            'idEntite': client.id,
                            'idDocType': None,  # CSV document type
                            'fichierNom': client_data.adherentsFile,
                            'fichierChemin': client_data.adherentsFilePath if hasattr(client_data, 'adherentsFilePath') and client_data.adherentsFilePath else f"csv_adherents/{client.id}/{client_data.adherentsFile}",
                            'instantTele': datetime.now()
                        }
                        
                        csv_document = await self.repository.create_document(csv_document_data)
                        logger.info(f"✅ CSV file stored as document with ID: {csv_document.id}")
                        
                    except Exception as csv_error:
                        logger.error(f"❌ Failed to store CSV file as document: {csv_error}")
                        # Don't fail the entire operation, just log the error
                        logger.warning("⚠️ Continuing with client creation despite CSV file storage failure")

            await self.repository.session.commit()
            logger.info("✅ All data committed successfully")
            
            return {
                "success": True,
                "client_id": client.id,
                "message": "Client created successfully with all data"
            }

        except Exception as e:
            logger.error(f"❌ DocumentService.create_client_with_documents() failed: {str(e)}")
            await self.repository.session.rollback()
            raise

    async def get_client_documents(self, client_id: int) -> List[DocumentResponse]:
        """Get all documents for a client"""
        logger.info(f"🔍 DocumentService.get_client_documents() called for client_id: {client_id}")
        try:
            documents = await self.repository.get_documents_by_client(client_id)
            logger.info(f"📄 Retrieved {len(documents)} documents from repository for client {client_id}")
            
            # Log details about each document
            for i, doc in enumerate(documents):
                logger.info(f"📄 Document {i+1}: ID={doc.id}, Nom={doc.fichierNom}, Chemin={doc.fichierChemin}, Type={doc.typeEntite}")
            
            # Convert to DTOs
            document_responses = [DocumentResponse.from_orm(doc) for doc in documents]
            logger.info(f"✅ Converted {len(document_responses)} documents to DTOs")
            
            return document_responses
        except Exception as e:
            logger.error(f"❌ DocumentService.get_client_documents() failed: {str(e)}")
            raise

    async def get_client_adherents(self, client_id: int) -> List[AdherentResponse]:
        """Get all adherents for a client"""
        logger.info(f"🔍 DocumentService.get_client_adherents() called for client_id: {client_id}")
        try:
            adherents = await self.repository.get_adherents_by_client(client_id)
            return [AdherentResponse.from_orm(adherent) for adherent in adherents]
        except Exception as e:
            logger.error(f"❌ DocumentService.get_client_adherents() failed: {str(e)}")
            raise

    async def create_document(self, document_data: dict) -> DocumentResponse:
        """Create a new document"""
        logger.info(f"🔍 DocumentService.create_document() called with data: {document_data}")
        try:
            document = await self.repository.create_document(document_data)
            return DocumentResponse.from_orm(document)
        except Exception as e:
            logger.error(f"❌ DocumentService.create_document() failed: {str(e)}")
            raise

    async def delete_document(self, document_id: int) -> bool:
        """Delete a document"""
        logger.info(f"🔍 DocumentService.delete_document() called for document_id: {document_id}")
        try:
            success = await self.repository.delete_document(document_id)
            return success
        except Exception as e:
            logger.error(f"❌ DocumentService.delete_document() failed: {str(e)}")
            raise

    async def get_documents_by_entity(self, entity_type: str, entity_id: int) -> List[DocumentResponse]:
        """Get all documents for a specific entity (client, contract, etc.)"""
        logger.info(f"🔍 DocumentService.get_documents_by_entity() called for entity_type: {entity_type}, entity_id: {entity_id}")
        try:
            documents = await self.repository.get_documents_by_entity(entity_type, entity_id)
            logger.info(f"📄 Retrieved {len(documents)} documents from repository for {entity_type} {entity_id}")
            
            # Convert to DTOs
            document_responses = [DocumentResponse.from_orm(doc) for doc in documents]
            logger.info(f"✅ Converted {len(document_responses)} documents to DTOs")
            
            return document_responses
        except Exception as e:
            logger.error(f"❌ DocumentService.get_documents_by_entity() failed: {str(e)}")
            raise

    async def link_document_to_entity(self, document_id: int, entity_type: str, entity_id: int) -> bool:
        """Link a document to an entity"""
        logger.info(f"🔍 DocumentService.link_document_to_entity() called for document_id: {document_id}, entity_type: {entity_type}, entity_id: {entity_id}")
        try:
            success = await self.repository.link_document_to_entity(document_id, entity_type, entity_id)
            return success
        except Exception as e:
            logger.error(f"❌ DocumentService.link_document_to_entity() failed: {str(e)}")
            raise
