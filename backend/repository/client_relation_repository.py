from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import logging
from model.client_relation import ClientRelation, TypeRelation
from dto.client_relation_dto import ClientRelationResponse, TypeRelationResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Client relation repository module imported")
logger.info(f"🔍 Logger name: {__name__}")

class ClientRelationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_client_relations(self, client_id: int) -> List[ClientRelation]:
        """Get all relations for a specific client (as principal or linked)"""
        from sqlalchemy import text
        
        # Use raw SQL with JOINs to get all the data we need
        query = text('''
            SELECT 
                cr.id,
                cr."idClientPrincipal",
                cr."idClientLie",
                cr."idTypeRelation",
                cr."dateDebut",
                cr."dateFin",
                cr.description,
                -- Principal client data
                c1."codeClient" as principal_code,
                c1."typeClient" as principal_type,
                p1.nom as principal_nom,
                p1.prenom as principal_prenom,
                s1.nom as principal_societe_nom,
                -- Linked client data
                c2."codeClient" as linked_code,
                c2."typeClient" as linked_type,
                p2.nom as linked_nom,
                p2.prenom as linked_prenom,
                s2.nom as linked_societe_nom,
                -- Type relation data
                tr."codeTypeRelation",
                tr.libelle as type_libelle
            FROM clients_relations cr
            LEFT JOIN clients c1 ON cr."idClientPrincipal" = c1.id
            LEFT JOIN clients c2 ON cr."idClientLie" = c2.id
            LEFT JOIN particuliers p1 ON c1.id = p1."idClient"
            LEFT JOIN particuliers p2 ON c2.id = p2."idClient"
            LEFT JOIN societes s1 ON c1.id = s1."idClient"
            LEFT JOIN societes s2 ON c2.id = s2."idClient"
            LEFT JOIN type_relation tr ON cr."idTypeRelation" = tr.id
            WHERE cr."idClientPrincipal" = :client_id OR cr."idClientLie" = :client_id
        ''')
        
        result = await self.session.execute(query, {"client_id": client_id})
        rows = result.fetchall()
        
        # Convert to ClientRelation objects with computed data
        relations = []
        for row in rows:
            # Create a mock ClientRelation object with the joined data
            relation = ClientRelation()
            relation.id = row[0]
            relation.idClientPrincipal = row[1]
            relation.idClientLie = row[2]
            relation.idTypeRelation = row[3]
            relation.dateDebut = row[4]
            relation.dateFin = row[5]
            relation.description = row[6]
            
            # Add computed client data as attributes
            relation.principal_data = {
                'codeClient': row[7],
                'typeClient': row[8],
                'nom': row[9],
                'prenom': row[10],
                'societe_nom': row[11]
            }
            
            relation.linked_data = {
                'codeClient': row[12],
                'typeClient': row[13],
                'nom': row[14],
                'prenom': row[15],
                'societe_nom': row[16]
            }
            
            relation.type_data = {
                'codeTypeRelation': row[17],
                'libelle': row[18]
            }
            
            relations.append(relation)
        
        return relations

    async def create_client_relation(self, relation_data: dict) -> ClientRelation:
        """Create a new client relation"""
        logger.info(f"🔍 Repository: Creating client relation with data: {relation_data}")
        
        relation = ClientRelation(**relation_data)
        logger.info(f"🔍 Repository: Created ClientRelation object: {relation}")
        
        self.session.add(relation)
        logger.info(f"🔍 Repository: Added relation to session")
        
        await self.session.commit()
        logger.info(f"🔍 Repository: Committed to database")
        
        await self.session.refresh(relation)
        logger.info(f"🔍 Repository: Refreshed relation object: {relation}")
        
        return relation

    async def update_client_relation(self, relation_id: int, relation_data: dict) -> Optional[ClientRelation]:
        """Update an existing client relation"""
        relation = await self.get_client_relation_by_id(relation_id)
        if relation:
            for key, value in relation_data.items():
                if hasattr(relation, key):
                    setattr(relation, key, value)
            await self.session.commit()
            await self.session.refresh(relation)
        return relation

    async def delete_client_relation(self, relation_id: int) -> bool:
        """Delete a client relation"""
        logger.info(f"🔍 Repository: Deleting client relation with ID: {relation_id}")
        
        try:
            from sqlalchemy import text
            
            # First, verify the relation exists
            verify_query = text('SELECT id FROM clients_relations WHERE id = :relation_id')
            verify_result = await self.session.execute(verify_query, {"relation_id": relation_id})
            existing_relation = verify_result.fetchone()
            
            if not existing_relation:
                logger.warning(f"⚠️ Repository: No relation found with ID {relation_id}")
                return False
            
            logger.info(f"🔍 Repository: Found relation {relation_id}, proceeding with deletion")
            
            # Use direct SQL delete to avoid session context issues
            delete_query = text('DELETE FROM clients_relations WHERE id = :relation_id')
            result = await self.session.execute(delete_query, {"relation_id": relation_id})
            
            if result.rowcount > 0:
                await self.session.commit()
                logger.info(f"✅ Repository: Successfully deleted relation {relation_id}, {result.rowcount} rows affected")
                
                # Verify deletion
                verify_after = await self.session.execute(verify_query, {"relation_id": relation_id})
                if verify_after.fetchone():
                    logger.error(f"❌ Repository: Relation {relation_id} still exists after deletion!")
                    return False
                else:
                    logger.info(f"✅ Repository: Deletion verified - relation {relation_id} no longer exists")
                    return True
            else:
                logger.warning(f"⚠️ Repository: No rows affected when deleting relation {relation_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Repository: Error deleting relation {relation_id}: {e}")
            await self.session.rollback()
            return False

    async def get_client_relation_by_id(self, relation_id: int) -> Optional[ClientRelation]:
        """Get a single client relation by ID"""
        result = await self.session.execute(
            select(ClientRelation).where(ClientRelation.id == relation_id)
        )
        return result.scalars().first()

    async def get_type_relations(self) -> List[TypeRelation]:
        """Get all available type relations"""
        result = await self.session.execute(select(TypeRelation))
        return result.scalars().all()

    async def create_type_relation(self, type_relation_data: dict) -> TypeRelation:
        """Create a new type relation"""
        type_relation = TypeRelation(**type_relation_data)
        self.session.add(type_relation)
        await self.session.commit()
        await self.session.refresh(type_relation)
        return type_relation
