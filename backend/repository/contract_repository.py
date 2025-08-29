from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import logging
from model.contract import Contract
from dto.contract_dto import ContractResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Contract repository module imported")
logger.info(f"🔍 Logger name: {__name__}")

class ContractRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_contracts_by_client(self, client_id: int) -> List[Contract]:
        """Get all contracts for a specific client"""
        from sqlalchemy.orm import selectinload
        
        result = await self.session.execute(
            select(Contract)
            .options(selectinload(Contract.produit))
            .where(Contract.idClient == client_id)
        )
        return result.scalars().all()

    async def create_contract(self, contract_data: dict) -> Contract:
        """Create a new contract"""
        try:
            logger.info(f"🔨 Creating contract with data: {contract_data}")
            
            # Ensure required fields are present
            if 'numPolice' not in contract_data:
                contract_data['numPolice'] = await self.generate_police_number()
                logger.info(f"🔢 Generated police number: {contract_data['numPolice']}")
            
            if 'dateDebut' not in contract_data:
                from datetime import date
                contract_data['dateDebut'] = date.today()
                logger.info(f"📅 Set default date: {contract_data['dateDebut']}")
            
            logger.info(f"📋 Final contract data: {contract_data}")
            
            contract = Contract(**contract_data)
            self.session.add(contract)
            await self.session.commit()
            await self.session.refresh(contract)
            
            logger.info(f"✅ Contract created successfully with ID: {contract.id}")
            return contract
            
        except Exception as e:
            logger.error(f"❌ Error creating contract: {str(e)}")
            logger.error(f"❌ Contract data: {contract_data}")
            raise

    async def update_contract(self, contract_id: int, contract_data: dict) -> Optional[Contract]:
        """Update an existing contract"""
        contract = await self.get_contract_by_id(contract_id)
        if contract:
            for key, value in contract_data.items():
                if hasattr(contract, key):
                    setattr(contract, key, value)
            await self.session.commit()
            await self.session.refresh(contract)
        return contract

    async def delete_contract(self, contract_id: int) -> bool:
        """Delete a contract"""
        contract = await self.get_contract_by_id(contract_id)
        if contract:
            self.session.delete(contract)
            await self.session.commit()
            return True
        return False

    async def get_contract_by_id(self, contract_id: int) -> Optional[Contract]:
        """Get a single contract by ID"""
        from sqlalchemy.orm import selectinload
        
        result = await self.session.execute(
            select(Contract)
            .options(selectinload(Contract.produit))
            .where(Contract.id == contract_id)
        )
        return result.scalars().first()

    async def generate_police_number(self) -> str:
        """Generate a unique police number"""
        import random
        
        # Generate a random 6-character string: A-Z or 1-9
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789'
        police_number = ''.join(random.choice(characters) for _ in range(6))
        
        # Ensure it's unique using async SQLAlchemy 2.0 syntax
        while True:
            result = await self.session.execute(
                select(Contract).where(Contract.numPolice == police_number)
            )
            existing = result.scalars().first()
            if not existing:
                break
            # Generate new number if this one exists
            police_number = ''.join(random.choice(characters) for _ in range(6))
        
        return police_number
