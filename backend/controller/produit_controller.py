from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.database.database import get_session
from model.produit import Produit
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/produits", tags=["produits"])

@router.get("/", response_model=List[dict])
async def get_produits(session: AsyncSession = Depends(get_session)):
    """Get all products"""
    try:
        result = await session.execute(select(Produit))
        produits = result.scalars().all()
        
        return [
            {
                "id": produit.id,
                "codeProduit": produit.codeProduit,
                "libelle": produit.libelle,
                "description": produit.description
            }
            for produit in produits
        ]
    except Exception as e:
        logger.error(f"Error fetching produits: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des produits")

@router.get("/{produit_id}", response_model=dict)
async def get_produit(produit_id: int, session: AsyncSession = Depends(get_session)):
    """Get a single product by ID"""
    try:
        result = await session.execute(select(Produit).where(Produit.id == produit_id))
        produit = result.scalar_one_or_none()
        
        if not produit:
            raise HTTPException(status_code=404, detail="Produit non trouvé")
        
        return {
            "id": produit.id,
            "codeProduit": produit.codeProduit,
            "libelle": produit.libelle,
            "description": produit.description
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching produit {produit_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération du produit")
