from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from config.database.database import get_session
from security.auth_middleware import get_current_active_user, require_role
from model.user import User

router = APIRouter()

# Toutes les fonctions de changement de mot de passe ont été supprimées 