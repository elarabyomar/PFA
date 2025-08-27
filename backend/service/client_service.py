from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from repository.client_repository import ClientRepository
from dto.client_dto import ClientResponse, ClientCreate, ClientUpdate

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
        return await self.repository.get_clients_paginated(skip, limit, search, filters)

    async def get_client_by_id(self, client_id: int) -> Optional[ClientResponse]:
        """Get a single client by ID"""
        client = await self.repository.get_client_by_id(client_id)
        if client:
            nom = self.repository._compute_client_name(client)
            return ClientResponse(
                id=client.id,
                codeClient=client.codeClient,
                typeClient=client.typeClient,
                adresse=client.adresse,
                tel=client.tel,
                email=client.email,
                statut=client.statut,
                importance=client.importance,
                budget=client.budget,
                proba=client.proba,
                nom=nom
            )
        return None

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
        nom = self.repository._compute_client_name(client)
        return ClientResponse(
            id=client.id,
            codeClient=client.codeClient,
            typeClient=client.typeClient,
            adresse=client.adresse,
            tel=client.tel,
            email=client.email,
            statut=client.statut,
            importance=client.importance,
            budget=client.budget,
            proba=client.proba,
            nom=nom
        )

    async def update_client(self, client_id: int, client_data: ClientUpdate) -> ClientResponse:
        """Update an existing client"""
        # Validate client data
        if client_data.typeClient and client_data.typeClient not in ['PARTICULIER', 'SOCIETE']:
            raise ValueError("Type client must be either PARTICULIER or SOCIETE")
        
        # Update client
        client = await self.repository.update_client(client_id, client_data.dict(exclude_unset=True))
        
        if client:
            # Return response with computed nom
            nom = self.repository._compute_client_name(client)
            return ClientResponse(
                id=client.id,
                codeClient=client.codeClient,
                typeClient=client.typeClient,
                adresse=client.adresse,
                tel=client.tel,
                email=client.email,
                statut=client.statut,
                importance=client.importance,
                budget=client.budget,
                proba=client.proba,
                nom=nom
            )
        return None

    async def delete_client(self, client_id: int) -> bool:
        """Delete a client"""
        return await self.repository.delete_client(client_id)

    def get_client_types(self) -> List[str]:
        """Get all available client types"""
        return self.repository.get_client_types()

    def get_client_statuts(self) -> List[str]:
        """Get all available client statuses"""
        return self.repository.get_client_statuts()

    def get_client_importance_levels(self) -> List[str]:
        """Get all available importance levels"""
        return self.repository.get_client_importance_levels()

    def format_budget(self, budget: str) -> str:
        """Format budget value for display"""
        if not budget:
            return "0 DH"
        
        try:
            # Try to parse as number and format
            budget_num = float(budget)
            return f"{budget_num:,.2f} DH"
        except ValueError:
            # If not a number, return as is
            return budget

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
