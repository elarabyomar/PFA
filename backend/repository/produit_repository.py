from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import logging
from model.produit import Produit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Produit repository module imported")
logger.info(f"🔍 Logger name: {__name__}")

class ProduitRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_produit_by_id(self, produit_id: int) -> Optional[Produit]:
        """Get a single product by ID"""
        try:
            result = await self.session.execute(
                select(Produit).where(Produit.id == produit_id)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"❌ Error getting product by ID {produit_id}: {e}")
            return None

    async def get_all_produits(self) -> List[Produit]:
        """Get all products"""
        try:
            result = await self.session.execute(select(Produit))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"❌ Error getting all products: {e}")
            return []

    async def create_produit(self, produit_data: dict) -> Optional[Produit]:
        """Create a new product"""
        try:
            produit = Produit(**produit_data)
            self.session.add(produit)
            await self.session.commit()
            await self.session.refresh(produit)
            return produit
        except Exception as e:
            logger.error(f"❌ Error creating product: {e}")
            await self.session.rollback()
            return None

    async def update_produit(self, produit_id: int, produit_data: dict) -> Optional[Produit]:
        """Update an existing product"""
        try:
            produit = await self.get_produit_by_id(produit_id)
            if produit:
                for key, value in produit_data.items():
                    if hasattr(produit, key):
                        setattr(produit, key, value)
                await self.session.commit()
                await self.session.refresh(produit)
                return produit
            return None
        except Exception as e:
            logger.error(f"❌ Error updating product {produit_id}: {e}")
            await self.session.rollback()
            return None

    async def delete_produit(self, produit_id: int) -> bool:
        """Delete a product"""
        try:
            produit = await self.get_produit_by_id(produit_id)
            if produit:
                self.session.delete(produit)
                await self.session.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error deleting product {produit_id}: {e}")
            await self.session.rollback()
            return False

