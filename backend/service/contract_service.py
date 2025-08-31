from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from repository.contract_repository import ContractRepository
from dto.contract_dto import ContractResponse, ContractCreate, ContractUpdate
from datetime import date
import time
import random
import string

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Contract service module imported")
logger.info(f"🔍 Logger name: {__name__}")

class ContractService:
    def __init__(self, session: AsyncSession):
        self.repository = ContractRepository(session)

    async def get_all_contracts(self) -> List[ContractResponse]:
        """Get all contracts with client information"""
        contracts = await self.repository.get_all_contracts()
        
        # Load product information for each contract
        contract_responses = []
        for contract in contracts:
            produit_data = None
            if hasattr(contract, 'produit') and contract.produit:
                try:
                    produit_data = {
                        'id': contract.produit.id,
                        'libelle': contract.produit.libelle,
                        'codeProduit': contract.produit.codeProduit
                    }
                    logger.info(f"✅ Loaded product data from relationship for contract {contract.id}: {produit_data}")
                except Exception as produit_error:
                    logger.warning(f"⚠️ Failed to load product data from relationship for contract {contract.id}: {produit_error}")
                    produit_data = None
            elif contract.idProduit:
                logger.warning(f"⚠️ Contract {contract.id} has idProduit {contract.idProduit} but no produit relationship loaded")
            
            # Load compagnie data
            compagnie_data = None
            if hasattr(contract, 'compagnie') and contract.compagnie:
                try:
                    compagnie_data = {
                        'id': contract.compagnie.id,
                        'codeCIE': contract.compagnie.codeCIE,
                        'nom': contract.compagnie.nom
                    }
                except Exception as compagnie_error:
                    logger.warning(f"⚠️ Failed to load compagnie data from relationship for contract {contract.id}: {compagnie_error}")
                    compagnie_data = None
            
            # Load duree data
            duree_data = None
            if hasattr(contract, 'duree') and contract.duree:
                try:
                    duree_data = {
                        'id': contract.duree.id,
                        'libelle': contract.duree.libelle,
                        'nbMois': contract.duree.nbMois
                    }
                except Exception as duree_error:
                    logger.warning(f"⚠️ Failed to load duree data from relationship for contract {contract.id}: {duree_error}")
                    duree_data = None
            
            # Load client data with computed name
            client_data = None
            if hasattr(contract, 'client') and contract.client:
                try:
                    # Compute client name based on type
                    client_nom = None
                    if contract.client.typeClient == 'PARTICULIER' and hasattr(contract.client, 'particulier') and contract.client.particulier:
                        client_nom = f"{contract.client.particulier.nom} {contract.client.particulier.prenom}"
                    elif contract.client.typeClient == 'SOCIETE' and hasattr(contract.client, 'societe') and contract.client.societe:
                        client_nom = contract.client.societe.nom
                    else:
                        client_nom = contract.client.codeClient  # Fallback to code if no name found
                    
                    client_data = {
                        'id': contract.client.id,
                        'codeClient': contract.client.codeClient,
                        'typeClient': contract.client.typeClient,
                        'nom': client_nom
                    }
                except Exception as client_error:
                    logger.warning(f"⚠️ Failed to load client data from relationship for contract {contract.id}: {client_error}")
                    client_data = None
            
            contract_responses.append(ContractResponse(**{
                'id': contract.id,
                'numPolice': contract.numPolice,
                'typeContrat': contract.typeContrat,
                'dateDebut': contract.dateDebut,
                'dateFin': contract.dateFin,
                'idClient': contract.idClient,
                'idProduit': contract.idProduit,
                'idCompagnie': contract.idCompagnie,
                'prime': contract.prime,
                'idTypeDuree': contract.idTypeDuree,
                'produit': produit_data,
                'compagnie': compagnie_data,
                'duree': duree_data,
                'client': client_data
            }))
        
        return contract_responses

    async def get_contracts_by_client(self, client_id: int) -> List[ContractResponse]:
        """Get all contracts for a specific client"""
        contracts = await self.repository.get_contracts_by_client(client_id)
        
        # Load product information for each contract
        contract_responses = []
        for contract in contracts:
            produit_data = None
            if hasattr(contract, 'produit') and contract.produit:
                try:
                    produit_data = {
                        'id': contract.produit.id,
                        'libelle': contract.produit.libelle,
                        'codeProduit': contract.produit.codeProduit
                    }
                    logger.info(f"✅ Loaded product data from relationship for contract {contract.id}: {produit_data}")
                except Exception as produit_error:
                    logger.warning(f"⚠️ Failed to load product data from relationship for contract {contract.id}: {produit_error}")
                    produit_data = None
            elif contract.idProduit:
                logger.warning(f"⚠️ Contract {contract.id} has idProduit {contract.idProduit} but no produit relationship loaded")
            
            # Load compagnie data
            compagnie_data = None
            if hasattr(contract, 'compagnie') and contract.compagnie:
                try:
                    compagnie_data = {
                        'id': contract.compagnie.id,
                        'codeCIE': contract.compagnie.codeCIE,
                        'nom': contract.compagnie.nom
                    }
                except Exception as compagnie_error:
                    logger.warning(f"⚠️ Failed to load compagnie data from relationship for contract {contract.id}: {compagnie_error}")
                    compagnie_data = None
            
            # Load duree data
            duree_data = None
            if hasattr(contract, 'duree') and contract.duree:
                try:
                    duree_data = {
                        'id': contract.duree.id,
                        'libelle': contract.duree.libelle,
                        'nbMois': contract.duree.nbMois
                    }
                except Exception as duree_error:
                    logger.warning(f"⚠️ Failed to load duree data from relationship for contract {contract.id}: {duree_error}")
                    duree_data = None
            
            contract_responses.append(ContractResponse(**{
                'id': contract.id,
                'numPolice': contract.numPolice,
                'typeContrat': contract.typeContrat,
                'dateDebut': contract.dateDebut,
                'dateFin': contract.dateFin,
                'idClient': contract.idClient,
                'idProduit': contract.idProduit,
                'idCompagnie': contract.idCompagnie,
                'prime': contract.prime,
                'idTypeDuree': contract.idTypeDuree,
                'produit': produit_data,
                'compagnie': compagnie_data,
                'duree': duree_data
            }))
        
        return contract_responses

    async def create_contract(self, contract_data: ContractCreate) -> ContractResponse:
        """Create a new contract"""
        # Set default date if not provided
        if not contract_data.dateDebut:
            contract_data.dateDebut = date.today()
        
        # Generate police number if not provided
        if not contract_data.numPolice:
            contract_data.numPolice = await self.repository.generate_police_number()
        
        contract = await self.repository.create_contract(contract_data.dict())
        
        # Load product information for the created contract
        produit_data = None
        if hasattr(contract, 'produit') and contract.produit:
            try:
                produit_data = {
                    'id': contract.produit.id,
                    'libelle': contract.produit.libelle,
                    'codeProduit': contract.produit.codeProduit
                }
            except Exception as produit_error:
                logger.warning(f"⚠️ Failed to load product data from relationship for created contract: {produit_error}")
                produit_data = None
        
        return ContractResponse(**{
            'id': contract.id,
            'numPolice': contract.numPolice,
            'typeContrat': contract.typeContrat,
            'dateDebut': contract.dateDebut,
            'dateFin': contract.dateFin,
            'idClient': contract.idClient,
            'idProduit': contract.idProduit,
            'produit': produit_data
        })

    async def update_contract(self, contract_id: int, contract_data: ContractUpdate) -> Optional[ContractResponse]:
        """Update an existing contract"""
        contract = await self.repository.update_contract(contract_id, contract_data.dict(exclude_unset=True))
        if contract:
            # Load product information for the updated contract
            produit_data = None
            if hasattr(contract, 'produit') and contract.produit:
                try:
                    produit_data = {
                        'id': contract.produit.id,
                        'libelle': contract.produit.libelle,
                        'codeProduit': contract.produit.codeProduit
                    }
                except Exception as produit_error:
                    logger.warning(f"⚠️ Failed to load product data from relationship for updated contract: {produit_error}")
                    produit_data = None
            
            return ContractResponse(**{
                'id': contract.id,
                'numPolice': contract.numPolice,
                'typeContrat': contract.typeContrat,
                'dateDebut': contract.dateDebut,
                'dateFin': contract.dateFin,
                'idClient': contract.idClient,
                'idProduit': contract.idProduit,
                'produit': produit_data
            })
        return None

    async def delete_contract(self, contract_id: int) -> bool:
        """Delete a contract"""
        return await self.repository.delete_contract(contract_id)

    async def get_contract_by_id(self, contract_id: int) -> Optional[ContractResponse]:
        """Get a single contract by ID"""
        contract = await self.repository.get_contract_by_id(contract_id)
        if contract:
            # Load product information for the contract
            produit_data = None
            if hasattr(contract, 'produit') and contract.produit:
                try:
                    produit_data = {
                        'id': contract.produit.id,
                        'libelle': contract.produit.libelle,
                        'codeProduit': contract.produit.codeProduit
                    }
                except Exception as produit_error:
                    logger.warning(f"⚠️ Failed to load product data from relationship for contract {contract_id}: {produit_error}")
                    produit_data = None
            
            return ContractResponse(**{
                'id': contract.id,
                'numPolice': contract.numPolice,
                'typeContrat': contract.typeContrat,
                'dateDebut': contract.dateDebut,
                'dateFin': contract.dateFin,
                'idClient': contract.idClient,
                'idProduit': contract.idProduit,
                'produit': produit_data
            })
        return None

    async def transform_opportunity_to_contract(self, opportunity_id: int, contract_data: dict, document_files: Optional[list] = None) -> ContractResponse:
        """Transform an opportunity to a contract"""
        try:
            # Get the opportunity details
            from repository.opportunity_repository import OpportunityRepository
            opportunity_repo = OpportunityRepository(self.repository.session)
            opportunity = await opportunity_repo.get_opportunity_by_id(opportunity_id)
            
            if not opportunity:
                raise ValueError(f"Opportunity with ID {opportunity_id} not found")
            
            # Generate 6-character alphanumeric contract number (A-Z, 1-9)
            def generate_contract_number():
                chars = string.ascii_uppercase + string.digits.replace('0', '')  # A-Z, 1-9
                return ''.join(random.choice(chars) for _ in range(6))
            
            contract_num = generate_contract_number()
            
            # Create contract data from opportunity with all new fields
            contract_data_from_opportunity = {
                'idClient': opportunity.idClient,
                'idProduit': opportunity.idProduit,
                'typeContrat': contract_data.get('typeContrat', 'Duree ferme'),
                'dateDebut': contract_data.get('dateDebut', date.today()),
                'dateFin': contract_data.get('dateFin'),
                'numPolice': contract_num,
                'prime': contract_data.get('prime'),
                'idCompagnie': contract_data.get('idCompagnie'),
                'idTypeDuree': contract_data.get('idTypeDuree')
            }
            
            # Create the contract
            contract = await self.repository.create_contract(contract_data_from_opportunity)
            logger.info(f"✅ Contract created successfully: {contract}")
            
            # Handle document uploads if provided
            if document_files and len(document_files) > 0:
                try:
                    # Upload each document using the document service directly
                    for doc_file in document_files:
                        try:
                            # Use the document service to create documents with proper UUID filenames
                            from repository.document_repository import DocumentRepository
                            import os
                            import uuid
                            from datetime import datetime
                            
                            # Generate UUID filename
                            file_extension = os.path.splitext(doc_file['file'].filename)[1]
                            unique_filename = f"{uuid.uuid4()}{file_extension}"
                            
                            # Save the file to disk
                            current_dir = os.path.dirname(os.path.abspath(__file__))
                            upload_dir = os.path.join(os.path.dirname(current_dir), "uploads")
                            
                            if not os.path.exists(upload_dir):
                                os.makedirs(upload_dir)
                            
                            file_path = os.path.join(upload_dir, unique_filename)
                            
                            # Read and save the file
                            content = await doc_file['file'].read()
                            with open(file_path, "wb") as buffer:
                                buffer.write(content)
                            
                            # Create document record using the repository directly
                            document_repo = DocumentRepository(self.repository.session)
                            document_data = {
                                'fichierNom': doc_file.get('name', 'Document contrat'),
                                'fichierChemin': unique_filename,  # Store UUID filename
                                'typeEntite': 'contrat',
                                'idEntite': contract.id,
                                'instantTele': datetime.now()
                            }
                            
                            await document_repo.create_document(document_data)
                            logger.info(f"✅ Document {doc_file.get('name')} uploaded and linked to contract {contract.id}")
                            
                        except Exception as doc_error:
                            logger.warning(f"⚠️ Failed to process document {doc_file.get('name')}: {doc_error}")
                            continue
                except Exception as doc_error:
                    logger.warning(f"⚠️ Failed to link documents to contract: {doc_error}")
                    # Don't fail the transformation if document linking fails
            
            # Get fresh contract data to ensure we have the latest information
            fresh_contract = await self.repository.get_contract_by_id(contract.id)
            
            # Update the opportunity status to mark it as transformed
            try:
                await opportunity_repo.update_opportunity(opportunity_id, {
                    'etape': 'Transformée',
                    'transformed': True,
                    'idContrat': fresh_contract.id,
                    'dateTransformation': date.today()
                })
                logger.info(f"✅ Updated opportunity {opportunity_id} status to 'Transformée' and linked to contract {fresh_contract.id}")
            except Exception as update_error:
                logger.warning(f"⚠️ Failed to update opportunity status: {update_error}")
                # Don't fail the transformation if status update fails
            
            logger.info(f"✅ Successfully transformed opportunity {opportunity_id} to contract {fresh_contract.id}")
            
            # Return the created contract with fresh data including new fields
            contract_dict = {
                'id': fresh_contract.id,
                'idClient': fresh_contract.idClient,
                'idProduit': fresh_contract.idProduit,
                'typeContrat': fresh_contract.typeContrat,
                'dateDebut': fresh_contract.dateDebut,
                'dateFin': fresh_contract.dateFin,
                'numPolice': fresh_contract.numPolice,
                'prime': fresh_contract.prime,
                'idCompagnie': fresh_contract.idCompagnie,
                'idTypeDuree': fresh_contract.idTypeDuree
            }
            
            if hasattr(fresh_contract, 'produit') and fresh_contract.produit:
                contract_dict['produit'] = {
                    'id': fresh_contract.produit.id,
                    'codeProduit': fresh_contract.produit.codeProduit,
                    'libelle': fresh_contract.produit.libelle,
                    'description': fresh_contract.produit.description
                }
            
            if hasattr(fresh_contract, 'compagnie') and fresh_contract.compagnie:
                contract_dict['compagnie'] = {
                    'id': fresh_contract.compagnie.id,
                    'codeCIE': fresh_contract.compagnie.codeCIE,
                    'nom': fresh_contract.compagnie.nom
                }
            
            if hasattr(fresh_contract, 'duree') and fresh_contract.duree:
                contract_dict['duree'] = {
                    'id': fresh_contract.duree.id,
                    'libelle': fresh_contract.duree.libelle,
                    'nbMois': fresh_contract.duree.nbMois
                }
            
            return ContractResponse(**contract_dict)
            
        except Exception as e:
            logger.error(f"❌ Error transforming opportunity to contract: {e}")
            raise
