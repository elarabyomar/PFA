#!/usr/bin/env python3
"""
Migration script to add transformed and idContrat columns to opportunities table
This enables tracking which opportunities have been transformed to contracts
"""

import asyncio
import logging
from sqlalchemy import text
from config.database.database import get_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_opportunity_transform():
    """Add transformed and idContrat columns to opportunities table"""
    engine = get_engine()
    
    try:
        async with engine.begin() as conn:
            logger.info("🔄 Starting opportunity transform migration...")
            
            # Check if columns already exist
            check_transformed_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'opportunites' AND column_name = 'transformed'
            """)
            
            check_idcontrat_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'opportunites' AND column_name = 'idContrat'
            """)
            
            transformed_exists = await conn.execute(check_transformed_query)
            idcontrat_exists = await conn.execute(check_idcontrat_query)
            
            # Add transformed column if it doesn't exist
            if not transformed_exists.fetchone():
                logger.info("📝 Adding 'transformed' column to opportunities table...")
                add_transformed_query = text("""
                    ALTER TABLE opportunites 
                    ADD COLUMN transformed BOOLEAN DEFAULT FALSE
                """)
                await conn.execute(add_transformed_query)
                logger.info("✅ Added 'transformed' column")
            else:
                logger.info("ℹ️ 'transformed' column already exists")
            
            # Add idContrat column if it doesn't exist
            if not idcontrat_exists.fetchone():
                logger.info("📝 Adding 'idContrat' column to opportunities table...")
                add_idcontrat_query = text("""
                    ALTER TABLE opportunites 
                    ADD COLUMN "idContrat" INTEGER REFERENCES contrats(id)
                """)
                await conn.execute(add_idcontrat_query)
                logger.info("✅ Added 'idContrat' column with foreign key reference")
            else:
                logger.info("ℹ️ 'idContrat' column already exists")
            
            logger.info("✅ Opportunity transform migration completed successfully")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate_opportunity_transform())
