from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    date_naissance = Column(Date, nullable=False)
    role = Column(String, nullable=False)  # Rôle de l'utilisateur
    password_changed = Column(Boolean, default=False)  # Nouveau champ pour suivre si le mot de passe a été changé
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)


