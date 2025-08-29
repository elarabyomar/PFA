from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from repository.client_relation_repository import ClientRelationRepository
from dto.client_relation_dto import ClientRelationResponse, ClientRelationCreate, ClientRelationUpdate, TypeRelationResponse, TypeRelationCreate
from datetime import date

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Client relation service module imported")
logger.info(f"🔍 Logger name: {__name__}")

class ClientRelationService:
    def __init__(self, session: AsyncSession):
        self.repository = ClientRelationRepository(session)

    async def get_client_relations(self, client_id: int) -> List[ClientRelationResponse]:
        """Get all relations for a specific client"""
        relations = await self.repository.get_client_relations(client_id)
        
        # Convert to DTOs with proper client data extraction
        relation_dtos = []
        for relation in relations:
            try:
                # Extract client data from the joined query results
                relation_dict = {
                    'id': relation.id,
                    'idClientPrincipal': relation.idClientPrincipal,
                    'idClientLie': relation.idClientLie,
                    'idTypeRelation': relation.idTypeRelation,
                    'dateDebut': relation.dateDebut,
                    'dateFin': relation.dateFin,
                    'description': relation.description,
                    'client_principal': {
                        'id': relation.idClientPrincipal,
                        'codeClient': getattr(relation, 'principal_data', {}).get('codeClient', 'N/A'),
                        'typeClient': getattr(relation, 'principal_data', {}).get('typeClient', 'N/A'),
                        'nom': self._get_client_name_from_data(getattr(relation, 'principal_data', {}))
                    },
                    'client_lie': {
                        'id': relation.idClientLie,
                        'codeClient': getattr(relation, 'linked_data', {}).get('codeClient', 'N/A'),
                        'typeClient': getattr(relation, 'linked_data', {}).get('typeClient', 'N/A'),
                        'nom': self._get_client_name_from_data(getattr(relation, 'linked_data', {}))
                    },
                    'type_relation': {
                        'id': relation.idTypeRelation,
                        'codeTypeRelation': getattr(relation, 'type_data', {}).get('codeTypeRelation', 'N/A'),
                        'libelle': getattr(relation, 'type_data', {}).get('libelle', 'N/A')
                    } if relation.idTypeRelation else None
                }
                relation_dtos.append(ClientRelationResponse(**relation_dict))
            except Exception as e:
                logger.error(f"Error processing relation {relation.id}: {e}")
                # Create a fallback DTO with basic data
                fallback_dict = {
                    'id': relation.id,
                    'idClientPrincipal': relation.idClientPrincipal,
                    'idClientLie': relation.idClientLie,
                    'idTypeRelation': relation.idTypeRelation,
                    'dateDebut': relation.dateDebut,
                    'dateFin': relation.dateFin,
                    'description': relation.description,
                    'client_principal': None,
                    'client_lie': None,
                    'type_relation': None
                }
                relation_dtos.append(ClientRelationResponse(**fallback_dict))
        
        return relation_dtos

    async def create_client_relation(self, relation_data: ClientRelationCreate) -> ClientRelationResponse:
        """Create a new client relation"""
        logger.info(f"🔍 Creating client relation: {relation_data}")
        
        # Set default date if not provided
        if not relation_data.dateDebut:
            relation_data.dateDebut = date.today()
        
        logger.info(f"🔍 Calling repository with data: {relation_data.dict()}")
        relation = await self.repository.create_client_relation(relation_data.dict())
        logger.info(f"✅ Relation created in repository: {relation}")
        
        # For newly created relations, we need to construct the response manually
        # since the ORM object doesn't have the joined data yet
        relation_dict = {
            'id': relation.id,
            'idClientPrincipal': relation.idClientPrincipal,
            'idClientLie': relation.idClientLie,
            'idTypeRelation': relation.idTypeRelation,
            'dateDebut': relation.dateDebut,
            'dateFin': relation.dateFin,
            'description': relation.description,
            'client_principal': None,  # Will be populated when fetched
            'client_lie': None,        # Will be populated when fetched
            'type_relation': None      # Will be populated when fetched
        }
        
        logger.info(f"✅ Returning relation response: {relation_dict}")
        return ClientRelationResponse(**relation_dict)

    async def update_client_relation(self, relation_id: int, relation_data: ClientRelationUpdate) -> Optional[ClientRelationResponse]:
        """Update an existing client relation"""
        relation = await self.repository.update_client_relation(relation_id, relation_data.dict(exclude_unset=True))
        if relation:
            # For updated relations, we need to construct the response manually
            relation_dict = {
                'id': relation.id,
                'idClientPrincipal': relation.idClientPrincipal,
                'idClientLie': relation.idClientLie,
                'idTypeRelation': relation.idTypeRelation,
                'dateDebut': relation.dateDebut,
                'dateFin': relation.dateFin,
                'description': relation.description,
                'client_principal': None,  # Will be populated when fetched
                'client_lie': None,        # Will be populated when fetched
                'type_relation': None      # Will be populated when fetched
            }
            return ClientRelationResponse(**relation_dict)
        return None

    async def delete_client_relation(self, relation_id: int) -> bool:
        """Delete a client relation"""
        return await self.repository.delete_client_relation(relation_id)

    async def get_client_relation_by_id(self, relation_id: int) -> Optional[ClientRelationResponse]:
        """Get a single client relation by ID"""
        relation = await self.repository.get_client_relation_by_id(relation_id)
        if relation:
            # For single relations, we need to construct the response manually
            relation_dict = {
                'id': relation.id,
                'idClientPrincipal': relation.idClientPrincipal,
                'idClientLie': relation.idClientLie,
                'idTypeRelation': relation.idTypeRelation,
                'dateDebut': relation.dateDebut,
                'dateFin': relation.dateFin,
                'description': relation.description,
                'client_principal': None,  # Will be populated when fetched
                'client_lie': None,        # Will be populated when fetched
                'type_relation': None      # Will be populated when fetched
            }
            return ClientRelationResponse(**relation_dict)
        return None

    async def get_type_relations(self) -> List[TypeRelationResponse]:
        """Get all available type relations"""
        type_relations = await self.repository.get_type_relations()
        return [TypeRelationResponse.from_orm(tr) for tr in type_relations]

    async def create_type_relation(self, type_relation_data: TypeRelationCreate) -> TypeRelationResponse:
        """Create a new type relation"""
        type_relation = await self.repository.create_type_relation(type_relation_data.dict())
        return TypeRelationResponse.from_orm(type_relation)

    def _get_client_name_from_data(self, client_data: dict) -> str:
        """Helper method to get client display name from joined data"""
        if not client_data or not isinstance(client_data, dict):
            return "N/A"
        
        try:
            type_client = client_data.get('typeClient', '')
            
            if type_client == 'PARTICULIER':
                nom = client_data.get('nom', '') or ''
                prenom = client_data.get('prenom', '') or ''
                name = f"{nom} {prenom}".strip()
                return name if name else client_data.get('codeClient', 'N/A')
            elif type_client == 'SOCIETE':
                societe_nom = client_data.get('societe_nom', '') or ''
                return societe_nom if societe_nom else client_data.get('codeClient', 'N/A')
            else:
                return client_data.get('codeClient', 'N/A')
        except Exception as e:
            logger.error(f"Error getting client name from data: {e}")
            return client_data.get('codeClient', 'N/A') if client_data else 'N/A'
