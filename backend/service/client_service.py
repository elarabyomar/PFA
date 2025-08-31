from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
from repository.client_repository import ClientRepository
from dto.client_dto import ClientResponse, ClientCreate, ClientUpdate
from model.client import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Client service module imported")
logger.info(f"🔍 Logger name: {__name__}")
logger.info(f"🔍 Logger level: {logger.level}")

class ClientService:
    def __init__(self, session: AsyncSession):
        self.repository = ClientRepository(session)

    async def get_clients_paginated(
        self, 
        skip: int = 0, 
        limit: int = 50,
        search: Optional[str] = None,
        filters: Optional[dict] = None
    ) -> Tuple[List[ClientResponse], int]:
        """Get clients with pagination, search, and filtering"""
        logger.info("🔍 ClientService.get_clients_paginated() called")
        logger.info(f"🔍 Parameters: skip={skip}, limit={limit}, search='{search}', filters={filters}")
        
        try:
            logger.info("🔄 Calling repository.get_clients_paginated()")
            result = await self.repository.get_clients_paginated(skip, limit, search, filters)
            logger.info(f"✅ Repository returned: {len(result[0])} clients, total_count={result[1]}")
            return result
        except Exception as e:
            logger.error(f"❌ ClientService.get_clients_paginated() failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise

    async def get_client_by_id(self, client_id: int) -> Optional[ClientResponse]:
        """Get a single client by ID"""
        client = await self.repository.get_client_by_id(client_id)
        if client:
            # Use a safe method to compute the name without lazy loading
            nom = self._compute_safe_client_name(client)
            return ClientResponse(
                id=client.id,
                codeClient=client.codeClient,
                typeClient=client.typeClient,
                adresse=client.adresse,
                tel=client.tel,
                email=client.email,
                importance=client.importance,
                budget=client.budget,
                proba=client.proba,
                nom=nom
            )
        return None

    def _compute_safe_client_name(self, client: Client) -> str:
        """Compute client name safely without accessing lazy-loaded relationships"""
        if client.typeClient == 'PARTICULIER':
            # For particuliers, we'll use a default name since we can't access the relationship safely
            return f"Particulier {client.codeClient}"
        elif client.typeClient == 'SOCIETE':
            # For societes, we'll use a default name since we can't access the relationship safely
            return f"Société {client.codeClient}"
        return client.codeClient or "N/A"

    async def get_client_details(self, client_id: int) -> Optional[dict]:
        """Get detailed client information including particulier/societe data"""
        client_details = await self.repository.get_client_details(client_id)
        return client_details

    async def create_client(self, client_data: ClientCreate) -> ClientResponse:
        """Create a new client"""
        # Validate client data
        if not client_data.codeClient:
            raise ValueError("Code client is required")
        
        if client_data.typeClient not in ['PARTICULIER', 'SOCIETE']:
            raise ValueError("Type client must be either PARTICULIER or SOCIETE")
        
        # Create client
        client = await self.repository.create_client(client_data.dict())
        
        # Return response with computed nom
        nom = self._compute_safe_client_name(client)
        return ClientResponse(
            id=client.id,
            codeClient=client.codeClient,
            typeClient=client.typeClient,
            adresse=client.adresse,
            tel=client.tel,
            email=client.email,
            importance=client.importance,
            budget=client.budget,
            proba=client.proba,
            nom=nom
        )

    async def update_client(self, client_id: int, client_data) -> ClientResponse:
        """Update an existing client"""
        logger.info(f"🔄 ClientService.update_client({client_id}) called")
        logger.debug(f"📝 Update data: {client_data}")
        
        try:
            # Handle both DTO and plain dict inputs
            if hasattr(client_data, 'dict'):
                # It's a Pydantic model
                update_dict = client_data.dict(exclude_unset=True)
            else:
                # It's a plain dict
                update_dict = client_data
            
            logger.debug(f"📝 Processed update dict: {update_dict}")
            
            # Validate client data
            if 'typeClient' in update_dict and update_dict['typeClient'] not in ['PARTICULIER', 'SOCIETE']:
                raise ValueError("Type client must be either PARTICULIER or SOCIETE")
            
            # Update client
            logger.info(f"🔄 Calling repository.update_client({client_id})")
            client = await self.repository.update_client(client_id, update_dict)
            
            if client:
                logger.info(f"✅ ClientService.update_client({client_id}) successful")
                # Return response with computed nom
                nom = self._compute_safe_client_name(client)
                return ClientResponse(
                    id=client.id,
                    codeClient=client.codeClient,
                    typeClient=client.typeClient,
                    adresse=client.adresse,
                    tel=client.tel,
                    email=client.email,
                    importance=client.importance,
                    budget=client.budget,
                    proba=client.proba,
                    nom=nom
                )
            else:
                logger.warning(f"⚠️ ClientService.update_client({client_id}) returned None")
                return None
                
        except Exception as e:
            logger.error(f"❌ ClientService.update_client({client_id}) failed: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise

    async def delete_client(self, client_id: int) -> bool:
        """Delete a client and automatically clean up all associated relations"""
        logger.info(f"🗑️ ClientService.delete_client({client_id}) called")
        try:
            logger.debug(f"🔄 Calling repository.delete_client({client_id})")
            result = await self.repository.delete_client(client_id)
            if result:
                logger.info(f"✅ ClientService.delete_client({client_id}) successful")
                logger.info(f"🔄 All associated clients have been automatically returned to the main table")
            else:
                logger.warning(f"⚠️ ClientService.delete_client({client_id}) returned False")
            return result
        except Exception as e:
            logger.error(f"❌ ClientService.delete_client({client_id}) failed: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise

    async def verify_client_cleanup(self, client_id: int) -> bool:
        """Verify that a deleted client has been properly cleaned up"""
        logger.info(f"🔍 ClientService.verify_client_cleanup({client_id}) called")
        try:
            # Check if any relations still exist for this client
            result = await self.repository.session.execute(
                text('SELECT COUNT(*) FROM clients_relations WHERE "idClientPrincipal" = :client_id OR "idClientLie" = :client_id'),
                {"client_id": client_id}
            )
            remaining_relations = result.scalar()
            
            if remaining_relations == 0:
                logger.info(f"✅ Cleanup verification successful for client {client_id}: No remaining relations")
                return True
            else:
                logger.warning(f"⚠️ Cleanup verification failed for client {client_id}: {remaining_relations} relations still exist")
                return False
                
        except Exception as e:
            logger.error(f"❌ ClientService.verify_client_cleanup({client_id}) failed: {e}")
            return False

    async def force_cleanup_orphaned_relations(self) -> int:
        """Force cleanup of any orphaned client relations (for maintenance purposes)"""
        logger.info("🧹 ClientService.force_cleanup_orphaned_relations() called")
        try:
            # Find relations where either the principal or associate client no longer exists
            orphaned_relations = await self.repository.session.execute(
                text('''
                    SELECT cr.id FROM clients_relations cr
                    LEFT JOIN clients c1 ON cr."idClientPrincipal" = c1.id
                    LEFT JOIN clients c2 ON cr."idClientLie" = c2.id
                    WHERE c1.id IS NULL OR c2.id IS NULL
                ''')
            )
            orphaned_ids = [row[0] for row in orphaned_relations.fetchall()]
            
            if orphaned_ids:
                logger.warning(f"⚠️ Found {len(orphaned_ids)} orphaned relations to clean up")
                
                # Delete orphaned relations
                result = await self.repository.session.execute(
                    text('DELETE FROM clients_relations WHERE id = ANY(:orphaned_ids)'),
                    {"orphaned_ids": orphaned_ids}
                )
                
                deleted_count = result.rowcount
                logger.info(f"✅ Cleaned up {deleted_count} orphaned relations")
                
                # Commit the cleanup
                await self.repository.session.commit()
                
                return deleted_count
            else:
                logger.info("✅ No orphaned relations found")
                return 0
                
        except Exception as e:
            logger.error(f"❌ ClientService.force_cleanup_orphaned_relations() failed: {e}")
            await self.repository.session.rollback()
            raise

    async def get_client_types(self) -> List[str]:
        """Get all available client types"""
        logger.info("🔍 ClientService.get_client_types() called")
        try:
            logger.info("🔄 Calling repository.get_client_types()")
            result = self.repository.get_client_types()
            logger.info(f"✅ Repository returned: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ ClientService.get_client_types() failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise



    async def get_client_importance_levels(self) -> List[str]:
        """Get all available importance levels"""
        return self.repository.get_client_importance_levels()

    def format_budget(self, budget) -> str:
        """Format budget value for display"""
        if not budget:
            return "0 DH"
        
        try:
            # Handle both string and Decimal types
            if hasattr(budget, 'quantize'):  # Decimal type
                budget_num = float(budget)
            else:
                # Try to parse as number and format
                budget_num = float(budget)
            return f"{budget_num:,.2f} DH"
        except (ValueError, TypeError):
            # If not a number, return as is
            return str(budget) if budget else "0 DH"

    def format_proba(self, proba: str) -> str:
        """Format probability value for display"""
        if not proba:
            return "0%"
        
        try:
            # Try to parse as number and format as percentage
            proba_num = float(proba)
            return f"{proba_num:.1f}%"
        except ValueError:
            # If not a number, return as is
            return proba
