from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_
from typing import List, Optional, Tuple
from model.client import Client, Particulier, Societe
from dto.client_dto import ClientResponse

class ClientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_clients_paginated(
        self, 
        skip: int = 0, 
        limit: int = 50,
        search: Optional[str] = None,
        filters: Optional[dict] = None
    ) -> Tuple[List[ClientResponse], int]:
        """
        Get clients with pagination, search, and filtering
        Returns (clients, total_count)
        """
        query = self.session.query(Client)
        
        # Apply search filter
        if search:
            search_filter = or_(
                Client.codeClient.ilike(f"%{search}%"),
                Client.tel.ilike(f"%{search}%"),
                Client.email.ilike(f"%{search}%"),
                Client.typeClient.ilike(f"%{search}%"),
                Client.statut.ilike(f"%{search}%"),
                Client.importance.ilike(f"%{search}%"),
                Client.budget.ilike(f"%{search}%"),
                Client.proba.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Apply additional filters
        if filters:
            if filters.get('typeClient'):
                query = query.filter(Client.typeClient == filters['typeClient'])
            if filters.get('statut'):
                query = query.filter(Client.statut == filters['statut'])
            if filters.get('importance'):
                query = query.filter(Client.importance == filters['importance'])
        
        # Get total count
        total_count = await query.count()
        
        # Apply pagination
        clients = await query.offset(skip).limit(limit).all()
        
        # Convert to response DTOs with computed nom field
        client_responses = []
        for client in clients:
            nom = self._compute_client_name(client)
            client_responses.append(ClientResponse(
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
            ))
        
        return client_responses, total_count

    async def get_client_by_id(self, client_id: int) -> Optional[Client]:
        """Get a single client by ID"""
        return await self.session.query(Client).filter(Client.id == client_id).first()

    async def create_client(self, client_data: dict) -> Client:
        """Create a new client"""
        client = Client(**client_data)
        self.session.add(client)
        await self.session.commit()
        await self.session.refresh(client)
        return client

    async def update_client(self, client_id: int, client_data: dict) -> Optional[Client]:
        """Update an existing client"""
        client = await self.get_client_by_id(client_id)
        if client:
            for key, value in client_data.items():
                if hasattr(client, key):
                    setattr(client, key, value)
            await self.session.commit()
            await self.session.refresh(client)
        return client

    async def delete_client(self, client_id: int) -> bool:
        """Delete a client"""
        client = await self.get_client_by_id(client_id)
        if client:
            self.session.delete(client)
            await self.session.commit()
            return True
        return False

    def _compute_client_name(self, client: Client) -> str:
        """Compute the display name for a client"""
        if client.typeClient == 'PARTICULIER':
            if hasattr(client, 'particulier') and client.particulier:
                return f"{client.particulier.nom} {client.particulier.prenom}".strip()
            return "N/A"
        elif client.typeClient == 'SOCIETE':
            if hasattr(client, 'societe') and client.societe:
                return client.societe.nom
            return "N/A"
        return "N/A"

    def get_client_types(self) -> List[str]:
        """Get all available client types"""
        return ['PARTICULIER', 'SOCIETE']

    def get_client_statuts(self) -> List[str]:
        """Get all available client statuses"""
        return ['Opportunite', 'vrai client', 'ancien client']

    def get_client_importance_levels(self) -> List[str]:
        """Get all available importance levels"""
        return ['1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5']
