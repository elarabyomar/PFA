from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os
import logging
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()

# URL de connexion pour Docker
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres_test:SYS@postgres_db:5432/test3")
logger.info(f"🔍 Database URL: {DATABASE_URL}")

try:
    logger.info("🚀 Creating async database engine...")
    engine = create_async_engine(DATABASE_URL, echo=True)
    logger.info("✅ Async database engine created successfully")
    
    logger.info("🚀 Creating async session maker...")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    logger.info("✅ Async session maker created successfully")
except Exception as e:
    logger.error(f"❌ Failed to create database engine/session: {e}")
    logger.error(f"❌ Error type: {type(e).__name__}")
    import traceback
    logger.error(f"❌ Traceback: {traceback.format_exc()}")
    raise

async def get_session() -> AsyncSession:
    """Fonction pour l'injection de dépendances de session"""
    try:
        logger.debug("🔄 Creating new database session...")
        session = async_session()
        logger.debug("✅ Database session created successfully")
        yield session
        logger.debug("🔄 Database session yielded successfully")
        await session.close()
    except Exception as e:
        logger.error(f"❌ Error creating database session: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise

# Test connection function
async def test_connection():
    """Test database connection"""
    try:
        logger.info("🧪 Testing database connection...")
        async with async_session() as session:
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            logger.info(f"✅ Database connection test successful: {value}")
            return value
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise

