from sqlalchemy import Column, Integer, String, DateTime, Date
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
    role = Column(String, nullable=False)


