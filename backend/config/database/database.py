from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

# URL de connexion pour Docker
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgrestest:SYS@postgres_db:5432/test3")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncSession:
    """Fonction pour l'injection de dépendances de session"""
    async with async_session() as session:
        yield session

# Exemple d'utilisation
async def test_connection():
    async with async_session() as session:
        result = await session.execute(text("SELECT 1"))
        return result.scalar()

