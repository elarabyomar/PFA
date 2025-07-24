from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from config.database.database import async_session
from security.auth_middleware import get_current_active_user, require_role
from model.user import User

router = APIRouter()

async def get_session():
    async with async_session() as session:
        yield session

# Toutes les fonctions de changement de mot de passe ont été supprimées 