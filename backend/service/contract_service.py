from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from repository.contract_repository import ContractRepository
from dto.contract_dto import ContractResponse, ContractCreate, ContractUpdate
from datetime import date

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Contract service module imported")
logger.info(f"🔍 Logger name: {__name__}")

class ContractService:
    def __init__(self, session: AsyncSession):
        self.repository = ContractRepository(session)

    async def get_contracts_by_client(self, client_id: int) -> List[ContractResponse]:
        """Get all contracts for a specific client"""
        contracts = await self.repository.get_contracts_by_client(client_id)
        return [ContractResponse(**{
            'id': contract.id,
            'numPolice': contract.numPolice,
            'typeContrat': contract.typeContrat,
            'dateDebut': contract.dateDebut,
            'dateFin': contract.dateFin,
            'idClient': contract.idClient,
            'idProduit': contract.idProduit,
            'produit': {
                'id': contract.produit.id,
                'libelle': contract.produit.libelle,
                'codeProduit': contract.produit.codeProduit
            } if contract.produit else None
        }) for contract in contracts]

    async def create_contract(self, contract_data: ContractCreate) -> ContractResponse:
        """Create a new contract"""
        # Set default date if not provided
        if not contract_data.dateDebut:
            contract_data.dateDebut = date.today()
        
        # Generate police number if not provided
        if not contract_data.numPolice:
            contract_data.numPolice = await self.repository.generate_police_number()
        
        contract = await self.repository.create_contract(contract_data.dict())
        
        return ContractResponse(**{
            'id': contract.id,
            'numPolice': contract.numPolice,
            'typeContrat': contract.typeContrat,
            'dateDebut': contract.dateDebut,
            'dateFin': contract.dateFin,
            'idClient': contract.idClient,
            'idProduit': contract.idProduit,
            'produit': {
                'id': contract.produit.id,
                'libelle': contract.produit.libelle,
                'codeProduit': contract.produit.codeProduit
            } if contract.produit else None
        })

    async def update_contract(self, contract_id: int, contract_data: ContractUpdate) -> Optional[ContractResponse]:
        """Update an existing contract"""
        contract = await self.repository.update_contract(contract_id, contract_data.dict(exclude_unset=True))
        if contract:
            return ContractResponse(**{
                'id': contract.id,
                'numPolice': contract.numPolice,
                'typeContrat': contract.typeContrat,
                'dateDebut': contract.dateDebut,
                'dateFin': contract.dateFin,
                'idClient': contract.idClient,
                'idProduit': contract.idProduit,
                'produit': {
                    'id': contract.produit.id,
                    'libelle': contract.produit.libelle,
                    'codeProduit': contract.produit.codeProduit
                } if contract.produit else None
            })
        return None

    async def delete_contract(self, contract_id: int) -> bool:
        """Delete a contract"""
        return await self.repository.delete_contract(contract_id)

    async def get_contract_by_id(self, contract_id: int) -> Optional[ContractResponse]:
        """Get a single contract by ID"""
        contract = await self.repository.get_contract_by_id(contract_id)
        if contract:
            return ContractResponse(**{
                'id': contract.id,
                'numPolice': contract.numPolice,
                'typeContrat': contract.typeContrat,
                'dateDebut': contract.dateDebut,
                'dateFin': contract.dateFin,
                'idClient': contract.idClient,
                'idProduit': contract.idProduit,
                'produit': {
                    'id': contract.produit.id,
                    'libelle': contract.produit.libelle,
                    'codeProduit': contract.produit.codeProduit
                } if contract.produit else None
            })
        return None

    async def transform_opportunity_to_contract(self, opportunity_id: int, contract_data: dict) -> ContractResponse:
        """Transform an opportunity to a contract"""
        try:
            logger.info(f"🔄 Starting transformation of opportunity {opportunity_id} to contract")
            logger.info(f"📋 Received contract data: {contract_data}")
            
            # Import opportunity service to get opportunity details
            from service.opportunity_service import OpportunityService
            from repository.opportunity_repository import OpportunityRepository
            
            # Get opportunity details
            opportunity_repo = OpportunityRepository(self.repository.session)
            logger.info(f"🔍 Fetching opportunity {opportunity_id} from repository...")
            opportunity = await opportunity_repo.get_opportunity_by_id(opportunity_id)
            
            if not opportunity:
                logger.error(f"❌ Opportunity with ID {opportunity_id} not found")
                raise ValueError(f"Opportunity with ID {opportunity_id} not found")
            
            logger.info(f"✅ Found opportunity: {opportunity}")
            
            # Create contract data from opportunity - ONLY take product, generate everything else
            contract_data_from_opportunity = {
                'numPolice': await self.repository.generate_police_number(),  # Auto-generate 6-char police number
                'typeContrat': contract_data.get('typeContrat', 'Duree ferme'),  # From dropdown or default
                'dateDebut': date.today(),  # Today's date (transformation date)
                'dateFin': contract_data.get('dateFin'),  # User must choose
                'idClient': opportunity.idClient,  # From opportunity
                'idProduit': opportunity.idProduit  # ONLY thing taken from opportunity
            }
            
            # Ensure all required fields are present and valid
            logger.info(f"🔍 Validating contract data:")
            logger.info(f"  - numPolice: {contract_data_from_opportunity['numPolice']} (type: {type(contract_data_from_opportunity['numPolice'])})")
            logger.info(f"  - typeContrat: {contract_data_from_opportunity['typeContrat']} (type: {type(contract_data_from_opportunity['typeContrat'])})")
            logger.info(f"  - dateDebut: {contract_data_from_opportunity['dateDebut']} (type: {type(contract_data_from_opportunity['dateDebut'])})")
            logger.info(f"  - dateFin: {contract_data_from_opportunity['dateFin']} (type: {type(contract_data_from_opportunity['dateFin'])})")
            logger.info(f"  - idClient: {contract_data_from_opportunity['idClient']} (type: {type(contract_data_from_opportunity['idClient'])})")
            logger.info(f"  - idProduit: {contract_data_from_opportunity['idProduit']} (type: {type(contract_data_from_opportunity['idProduit'])})")
            
            # Convert date strings to date objects if needed
            if isinstance(contract_data_from_opportunity['dateDebut'], str):
                from datetime import datetime
                contract_data_from_opportunity['dateDebut'] = datetime.strptime(
                    contract_data_from_opportunity['dateDebut'], '%Y-%m-%d'
                ).date()
                logger.info(f"📅 Converted dateDebut string to date: {contract_data_from_opportunity['dateDebut']}")
            
            if contract_data_from_opportunity['dateFin'] and isinstance(contract_data_from_opportunity['dateFin'], str):
                from datetime import datetime
                contract_data_from_opportunity['dateFin'] = datetime.strptime(
                    contract_data_from_opportunity['dateFin'], '%Y-%m-%d'
                ).date()
                logger.info(f"📅 Converted dateFin string to date: {contract_data_from_opportunity['dateFin']}")
            
            logger.info(f"📋 Contract data to create: {contract_data_from_opportunity}")
            
            # Create the contract
            logger.info("🔨 Creating contract in repository...")
            logger.info(f"🔍 Contract data type check:")
            logger.info(f"  - dateDebut type: {type(contract_data_from_opportunity['dateDebut'])}")
            logger.info(f"  - dateDebut value: {contract_data_from_opportunity['dateDebut']}")
            logger.info(f"  - dateFin type: {type(contract_data_from_opportunity['dateFin'])}")
            logger.info(f"  - dateFin value: {contract_data_from_opportunity['dateFin']}")
            
            contract = await self.repository.create_contract(contract_data_from_opportunity)
            logger.info(f"✅ Contract created successfully: {contract}")
            
            # Optionally, you could update the opportunity status here
            # For example, mark it as "Transformed" or "Closed"
            
            logger.info(f"✅ Successfully transformed opportunity {opportunity_id} to contract {contract.id}")
            
            return ContractResponse(**{
                'id': contract.id,
                'numPolice': contract.numPolice,
                'typeContrat': contract.typeContrat,
                'dateDebut': contract.dateDebut,
                'dateFin': contract.dateFin,
                'idClient': contract.idClient,
                'idProduit': contract.idProduit,
                'produit': {
                    'id': contract.produit.id,
                    'libelle': contract.produit.libelle,
                    'codeProduit': contract.produit.codeProduit
                } if contract.produit else None
            })
            
        except Exception as e:
            logger.error(f"❌ Error transforming opportunity {opportunity_id} to contract: {str(e)}")
            logger.error(f"❌ Exception type: {type(e)}")
            logger.error(f"❌ Exception details: {e}")
            raise
