from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime

class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str

class UserCreateDTO(BaseModel):
    nom: str = Field(..., min_length=2, max_length=50, description="Nom de l'utilisateur")
    prenom: str = Field(..., min_length=2, max_length=50, description="Prénom de l'utilisateur")
    email: EmailStr = Field(..., description="Email unique de l'utilisateur")
    password: Optional[str] = Field(None, min_length=6, description="Mot de passe de l'utilisateur (optionnel, généré automatiquement si non fourni)")
    date_naissance: date = Field(..., description="Date de naissance (format: YYYY-MM-DD)")
    roles: List[str] = Field(..., description="Liste des rôles de l'utilisateur")

class UserUpdateDTO(BaseModel):
    nom: Optional[str] = Field(None, min_length=2, max_length=50, description="Nom de l'utilisateur")
    prenom: Optional[str] = Field(None, min_length=2, max_length=50, description="Prénom de l'utilisateur")
    email: Optional[EmailStr] = Field(None, description="Email unique de l'utilisateur")
    date_naissance: Optional[date] = Field(None, description="Date de naissance (format: YYYY-MM-DD)")
    roles: Optional[List[str]] = Field(None, description="Liste des rôles de l'utilisateur")

class UserResponseDTO(BaseModel):
    id: int
    nom: str
    prenom: str
    email: str
    date_naissance: date
    role: str
    roles: Optional[str]
    password: Optional[str] = None  # Pour retourner le mot de passe généré
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ChangePasswordDTO(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


