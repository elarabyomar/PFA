from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RoleCreateDTO(BaseModel):
    """DTO pour créer un nouveau rôle"""
    name: str = Field(..., min_length=2, max_length=50, description="Nom du rôle")
    description: Optional[str] = Field(None, max_length=500, description="Description du rôle")

class RoleUpdateDTO(BaseModel):
    """DTO pour modifier un rôle existant"""
    name: Optional[str] = Field(None, min_length=2, max_length=50, description="Nom du rôle")
    description: Optional[str] = Field(None, max_length=500, description="Description du rôle")
    is_active: Optional[bool] = Field(None, description="Statut actif/inactif du rôle")

class RoleResponseDTO(BaseModel):
    """DTO pour la réponse des informations d'un rôle"""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 