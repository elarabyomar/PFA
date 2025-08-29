from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, text
from typing import List, Optional, Tuple
import logging
from model.client import Client, Particulier, Societe
from dto.client_dto import ClientResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log when this module is imported
logger.info("🔍 Client repository module imported")
logger.info(f"🔍 Logger name: {__name__}")
logger.info(f"🔍 Logger level: {logger.level}")

class ClientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_clients_paginated(
        self, 
        skip: int = 0, 
        limit: int = 50,
        search: Optional[str] = None,
        filters: Optional[dict] = None
    ) -> Tuple[List[ClientResponse], int]:
        """
        Get clients with pagination, search, and filtering
        Returns (clients, total_count)
        """
        logger.info("🔍 ClientRepository.get_clients_paginated() called")
        logger.info(f"🔍 Parameters: skip={skip}, limit={limit}, search='{search}', filters={filters}")
        
        try:
            # Build the base query
            logger.info("🔍 Building base query...")
            query = select(Client)
            logger.info("✅ Base query built")
            
            # Apply search filter
            if search:
                logger.info(f"🔍 Applying search filter: '{search}'")
                search_filter = or_(
                    Client.codeClient.ilike(f"%{search}%"),
                    Client.tel.ilike(f"%{search}%"),
                    Client.email.ilike(f"%{search}%"),
                    Client.typeClient.ilike(f"%{search}%"),

                    Client.importance.ilike(f"%{search}%"),
                    Client.budget.ilike(f"%{search}%"),
                    Client.proba.ilike(f"%{search}%")
                )
                query = query.where(search_filter)
                logger.info("✅ Search filter applied")
            
            # Apply additional filters
            if filters:
                logger.info(f"🔍 Applying additional filters: {filters}")
                if filters.get('typeClient'):
                    query = query.where(Client.typeClient == filters['typeClient'])
                    logger.info(f"✅ Type filter applied: {filters['typeClient']}")

                if filters.get('importance'):
                    query = query.where(Client.importance == filters['importance'])
                    logger.info(f"✅ Importance filter applied: {filters['importance']}")
                logger.info("✅ All additional filters applied")
            
            # Get total count
            logger.info("🔍 Getting total count...")
            count_query = select(Client)
            if search:
                count_query = count_query.where(search_filter)
            if filters:
                if filters.get('typeClient'):
                    count_query = count_query.where(Client.typeClient == filters['typeClient'])

                if filters.get('importance'):
                    count_query = count_query.where(Client.importance == filters['importance'])
            
            logger.info("🔍 Executing count query...")
            total_count_result = await self.session.execute(count_query)
            total_count = len(total_count_result.scalars().all())
            logger.info(f"✅ Total count retrieved: {total_count}")
            
            # Apply pagination
            logger.info(f"🔍 Applying pagination: offset={skip}, limit={limit}")
            query = query.offset(skip).limit(limit)
            
            # Execute main query with JOINs to avoid lazy loading issues
            logger.info("🔍 Executing main query with JOINs...")
            from model.client import Particulier, Societe
            
            # Use explicit JOINs instead of lazy loading
            query_with_joins = select(
                Client,
                Particulier.nom.label('particulier_nom'),
                Particulier.prenom.label('particulier_prenom'),
                Societe.nom.label('societe_nom')
            ).outerjoin(
                Particulier, Client.id == Particulier.idClient
            ).outerjoin(
                Societe, Client.id == Societe.idClient
            )
            
            # Apply the same filters to the JOIN query
            if search:
                query_with_joins = query_with_joins.where(search_filter)
            if filters:
                if filters.get('typeClient'):
                    query_with_joins = query_with_joins.where(Client.typeClient == filters['typeClient'])

                if filters.get('importance'):
                    query_with_joins = query_with_joins.where(Client.importance == filters['importance'])
            
            # Apply pagination to JOIN query
            query_with_joins = query_with_joins.offset(skip).limit(limit)
            
            # Add ordering to show newest clients first
            query_with_joins = query_with_joins.order_by(Client.id.desc())
            
            result = await self.session.execute(query_with_joins)
            rows = result.all()
            logger.info(f"✅ Main query executed, {len(rows)} clients retrieved")
            
            # Convert to response DTOs with computed nom field
            logger.info("🔍 Converting to response DTOs...")
            client_responses = []
            for i, row in enumerate(rows):
                client = row[0]  # First element is the Client object
                particulier_nom = row[1]  # Particulier nom
                particulier_prenom = row[2]  # Particulier prenom
                societe_nom = row[3]  # Societe nom
                
                try:
                    logger.info(f"🔍 Processing client {i+1}/{len(rows)}: ID={client.id}, Type={client.typeClient}")
                    logger.info(f"🔍 Raw JOIN data - particulier_nom: '{particulier_nom}', particulier_prenom: '{particulier_prenom}', societe_nom: '{societe_nom}'")
                    
                    # Check if this client is associated with another client
                    is_associated = await self._is_client_associated(client.id)
                    
                    # Compute name from joined data instead of lazy loading
                    nom = self._compute_client_name_from_joined_data(
                        client.typeClient, particulier_nom, particulier_prenom, societe_nom
                    )
                    logger.info(f"✅ Computed nom for client {client.id}: '{nom}'")
                    
                    client_response = ClientResponse(
                        id=client.id,
                        codeClient=client.codeClient,
                        typeClient=client.typeClient,
                        adresse=client.adresse,
                        tel=client.tel,
                        email=client.email,
                        importance=client.importance,
                        budget=client.budget,
                        proba=client.proba,
                        nom=nom,
                        isAssociated=is_associated
                    )
                    client_responses.append(client_response)
                    logger.info(f"✅ Client {client.id} converted to DTO successfully (isAssociated: {is_associated})")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing client {client.id}: {str(e)}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    raise
            
            logger.info(f"✅ Successfully converted {len(client_responses)} clients to DTOs")
            return client_responses, total_count
            
        except Exception as e:
            logger.error(f"❌ ClientRepository.get_clients_paginated() failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise

    async def get_client_by_id(self, client_id: int) -> Optional[Client]:
        """Get a single client by ID"""
        result = await self.session.execute(select(Client).where(Client.id == client_id))
        return result.scalars().first()

    async def get_client_details(self, client_id: int) -> Optional[dict]:
        """Get detailed client information including particulier/societe data"""
        try:
            # Get the client
            client_result = await self.session.execute(
                select(Client).where(Client.id == client_id)
            )
            client = client_result.scalars().first()
            
            if not client:
                return None
            
            # Get particulier or societe data based on client type
            if client.typeClient == 'PARTICULIER':
                particulier_result = await self.session.execute(
                    select(Particulier).where(Particulier.idClient == client_id)
                )
                particulier = particulier_result.scalars().first()
                
                if particulier:
                    return {
                        'client': {
                            'id': client.id,
                            'codeClient': client.codeClient,
                            'typeClient': client.typeClient,
                            'adresse': client.adresse,
                            'tel': client.tel,
                            'email': client.email,
                            'importance': client.importance,
                            'budget': client.budget,
                            'proba': client.proba
                        },
                        'particulier': {
                            'titre': particulier.titre,
                            'nom': particulier.nom,
                            'prenom': particulier.prenom,
                            'sexe': particulier.sexe,
                            'nationalite': particulier.nationalite,
                            'lieuNaissance': particulier.lieuNaissance,
                            'dateNaissance': particulier.dateNaissance,
                            'date_deces': particulier.date_deces,
                            'datePermis': particulier.datePermis,
                            'cin': particulier.cin,
                            'profession': particulier.profession,
                            'typeDocIdentite': particulier.typeDocIdentite,
                            'situationFamiliale': particulier.situationFamiliale,
                            'nombreEnfants': particulier.nombreEnfants,
                    
                            'moyenContactPrefere': particulier.moyenContactPrefere,
                            'optoutTelephone': particulier.optoutTelephone,
                            'optoutEmail': particulier.optoutEmail
                        }
                    }
            
            elif client.typeClient == 'SOCIETE':
                societe_result = await self.session.execute(
                    select(Societe).where(Societe.idClient == client_id)
                )
                societe = societe_result.scalars().first()
                
                if societe:
                    return {
                        'client': {
                            'id': client.id,
                            'codeClient': client.codeClient,
                            'typeClient': client.typeClient,
                            'adresse': client.adresse,
                            'tel': client.tel,
                            'email': client.email,
                            'importance': client.importance,
                            'budget': client.budget,
                            'proba': client.proba
                        },
                        'societe': {
                            'nom': societe.nom,
                            'formeJuridique': societe.formeJuridique,
                            'capital': societe.capital,
                            'registreCom': societe.registreCom,
                            'taxePro': societe.taxePro,
                            'idFiscal': societe.idFiscal,
                            'CNSS': societe.CNSS,
                            'ICE': societe.ICE,
                            'siteWeb': societe.siteWeb,
                            'societeMere': societe.societeMere,
                            'raisonSociale': societe.raisonSociale,
                            'sigle': societe.sigle,
                            'tribunalCommerce': societe.tribunalCommerce,
                            'secteurActivite': societe.secteurActivite,
                            'dateCreationSociete': societe.dateCreationSociete,
                    
                            'nomContactPrincipal': societe.nomContactPrincipal,
                            'fonctionContactPrincipal': societe.fonctionContactPrincipal
                        }
                    }
            
            # Return client data even if particulier/societe data is missing
            return {
                'client': {
                    'id': client.id,
                    'codeClient': client.codeClient,
                    'typeClient': client.typeClient,
                    'adresse': client.adresse,
                    'tel': client.tel,
                    'email': client.email,
                    'importance': client.importance,
                    'budget': client.budget,
                    'proba': client.proba
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting client details: {str(e)}")
            raise

    async def create_client(self, client_data: dict) -> Client:
        """Create a new client"""
        client = Client(**client_data)
        self.session.add(client)
        await self.session.commit()
        await self.session.refresh(client)
        return client

    async def update_client(self, client_id: int, client_data: dict) -> Optional[Client]:
        """Update an existing client"""
        logger.info(f"🔄 Starting update of client {client_id}...")
        logger.debug(f"📝 Update data: {client_data}")
        
        try:
            client = await self.get_client_by_id(client_id)
            if client:
                logger.debug(f"✅ Client {client_id} found, applying updates...")
                
                # Track what fields are being updated
                updated_fields = []
                related_updates = []
                
                # Handle basic client fields
                for key, value in client_data.items():
                    if hasattr(client, key):
                        old_value = getattr(client, key)
                        setattr(client, key, value)
                        updated_fields.append(f"{key}: {old_value} → {value}")
                        logger.debug(f"📝 Updated client {key}: {old_value} → {value}")
                    else:
                        logger.debug(f"ℹ️ Field {key} not found on client model, checking related tables...")
                        # Check if this is a field that should be updated in related tables
                        if client.typeClient == 'PARTICULIER':
                            # All fields that can be updated in particuliers table
                            particulier_fields = [
                                'nom', 'prenom', 'titre', 'sexe', 'nationalite', 'lieuNaissance',
                                'dateNaissance', 'date_deces', 'datePermis', 'cin', 'profession',
                                'typeDocIdentite', 'situationFamiliale', 'nombreEnfants',
                                'moyenContactPrefere', 'optoutTelephone', 'optoutEmail'
                            ]
                            if key in particulier_fields:
                                related_updates.append((key, value))
                                logger.debug(f"✅ Field {key} will be updated in particuliers table")
                            else:
                                logger.warning(f"⚠️ Field {key} not supported for particuliers table")
                        
                        elif client.typeClient == 'SOCIETE':
                            # All fields that can be updated in societes table
                            societe_fields = [
                                'nom', 'formeJuridique', 'capital', 'registreCom', 'taxePro',
                                'idFiscal', 'CNSS', 'ICE', 'siteWeb', 'societeMere',
                                'raisonSociale', 'sigle', 'tribunalCommerce', 'secteurActivite',
                                'dateCreationSociete', 'nomContactPrincipal',
                                'fonctionContactPrincipal'
                            ]
                            if key in societe_fields:
                                related_updates.append((key, value))
                                logger.debug(f"✅ Field {key} will be updated in societes table")
                            else:
                                logger.warning(f"⚠️ Field {key} not supported for societes table")
                        
                        else:
                            logger.warning(f"⚠️ Field {key} not found on client model or related tables")
                
                # Handle related table updates (all fields from particuliers/societes tables)
                if related_updates:
                    logger.info(f"🔄 Processing {len(related_updates)} related table updates...")
                    logger.info(f"🔄 Related updates to process: {related_updates}")
                    for field_name, field_value in related_updates:
                        if client.typeClient == 'PARTICULIER':
                            # Update fields in particuliers table
                            logger.debug(f"📝 Updating {field_name} in particuliers table: {field_value}")
                            
                            # Map field names to database columns (handle case sensitivity)
                            field_mapping = {
                                'nom': 'nom',
                                'prenom': 'prenom',
                                'titre': 'titre',
                                'sexe': 'sexe',
                                'nationalite': 'nationalite',
                                'lieuNaissance': 'lieuNaissance',
                                'dateNaissance': 'dateNaissance',
                                'date_deces': 'date_deces',
                                'datePermis': 'datePermis',
                                'cin': 'cin',
                                'profession': 'profession',
                                'typeDocIdentite': 'typeDocIdentite',
                                'situationFamiliale': 'situationFamiliale',
                                'nombreEnfants': 'nombreEnfants',
                                'moyenContactPrefere': 'moyenContactPrefere',
                                'optoutTelephone': 'optoutTelephone',
                                'optoutEmail': 'optoutEmail'
                            }
                            
                            if field_name in field_mapping:
                                db_column = field_mapping[field_name]
                                
                                # Convert date fields to proper date objects
                                processed_value = field_value
                                if field_name in ['dateNaissance', 'date_deces', 'datePermis']:
                                    if field_value and field_value.strip():  # Only process if not empty
                                        try:
                                            from datetime import datetime
                                            processed_value = datetime.strptime(field_value, '%Y-%m-%d').date()
                                            logger.debug(f"🔍 Converted date field {field_name}: {field_value} → {processed_value}")
                                        except ValueError as date_error:
                                            logger.warning(f"⚠️ Invalid date format for {field_name}: {field_value}, skipping update")
                                            continue
                                    else:
                                        # Empty string or None, set to None for database
                                        processed_value = None
                                        logger.debug(f"🔍 Empty date field {field_name}, setting to None")
                                
                                logger.debug(f"🔍 Executing SQL: UPDATE particuliers SET \"{db_column}\" = :value WHERE \"idClient\" = :client_id")
                                logger.debug(f"🔍 Parameters: value={processed_value}, client_id={client_id}")
                                
                                # First, let's check if the particulier record exists
                                check_result = await self.session.execute(
                                    text('SELECT COUNT(*) FROM particuliers WHERE "idClient" = :client_id'),
                                    {"client_id": client_id}
                                )
                                count = check_result.scalar()
                                logger.info(f"🔍 Found {count} particulier records for client {client_id}")
                                
                                if count > 0:
                                    # Record exists, proceed with update
                                    result = await self.session.execute(
                                        text(f'UPDATE particuliers SET "{db_column}" = :value WHERE "idClient" = :client_id'),
                                        {"value": processed_value, "client_id": client_id}
                                    )
                                    
                                    logger.debug(f"🔍 SQL result: rowcount={result.rowcount}")
                                    
                                    if result.rowcount > 0:
                                        updated_fields.append(f"particulier.{field_name}: → {processed_value}")
                                        logger.info(f"✅ Updated particulier.{field_name} to: {processed_value}")
                                    else:
                                        logger.warning(f"⚠️ Update failed for particulier.{field_name} - rowcount was 0")
                                else:
                                    logger.warning(f"⚠️ No particulier record found for client {client_id} - creating one...")
                                    # Create the particulier record if it doesn't exist
                                    try:
                                        insert_result = await self.session.execute(
                                            text(f'INSERT INTO particuliers ("idClient", "{db_column}") VALUES (:client_id, :value)'),
                                            {"client_id": client_id, "value": processed_value}
                                        )
                                        logger.info(f"✅ Created new particulier record for client {client_id} with {field_name}: {processed_value}")
                                        updated_fields.append(f"particulier.{field_name}: → {processed_value} (created)")
                                    except Exception as insert_error:
                                        logger.error(f"❌ Failed to create particulier record: {insert_error}")
                                        raise
                            else:
                                logger.warning(f"⚠️ Field {field_name} not supported for particuliers table")
                        
                        elif client.typeClient == 'SOCIETE':
                            # Update fields in societes table
                            logger.debug(f"📝 Updating {field_name} in societes table: {field_value}")
                            
                            # Map field names to database columns (handle case sensitivity)
                            field_mapping = {
                                'nom': 'nom',
                                'formeJuridique': 'formeJuridique',
                                'capital': 'capital',
                                'registreCom': 'registreCom',
                                'taxePro': 'taxePro',
                                'idFiscal': 'idFiscal',
                                'CNSS': 'CNSS',
                                'ICE': 'ICE',
                                'siteWeb': 'siteWeb',
                                'societeMere': 'societeMere',
                                'raisonSociale': 'raisonSociale',
                                'sigle': 'sigle',
                                'tribunalCommerce': 'tribunalCommerce',
                                'secteurActivite': 'secteurActivite',
                                'dateCreationSociete': 'dateCreationSociete',
                                'nomContactPrincipal': 'nomContactPrincipal',
                                'fonctionContactPrincipal': 'fonctionContactPrincipal'
                            }
                            
                            if field_name in field_mapping:
                                db_column = field_mapping[field_name]
                                
                                # Convert date fields to proper date objects
                                processed_value = field_value
                                if field_name == 'dateCreationSociete':
                                    if field_value and field_value.strip():  # Only process if not empty
                                        try:
                                            from datetime import datetime
                                            processed_value = datetime.strptime(field_value, '%Y-%m-%d').date()
                                            logger.debug(f"🔍 Converted date field {field_name}: {field_value} → {processed_value}")
                                        except ValueError as date_error:
                                            logger.warning(f"⚠️ Invalid date format for {field_name}: {field_value}, skipping update")
                                            continue
                                    else:
                                        # Empty string or None, set to None for database
                                        processed_value = None
                                        logger.debug(f"🔍 Empty date field {field_name}, setting to None")
                                
                                logger.debug(f"🔍 Executing SQL: UPDATE societes SET \"{db_column}\" = :value WHERE \"idClient\" = :client_id")
                                logger.debug(f"🔍 Parameters: value={processed_value}, client_id={client_id}")
                                
                                # First, let's check if the societe record exists
                                check_result = await self.session.execute(
                                    text('SELECT COUNT(*) FROM societes WHERE "idClient" = :client_id'),
                                    {"client_id": client_id}
                                )
                                count = check_result.scalar()
                                logger.info(f"🔍 Found {count} societe records for client {client_id}")
                                
                                if count > 0:
                                    # Record exists, proceed with update
                                    result = await self.session.execute(
                                        text(f'UPDATE societes SET "{db_column}" = :value WHERE "idClient" = :client_id'),
                                        {"value": processed_value, "client_id": client_id}
                                    )
                                    
                                    logger.debug(f"🔍 SQL result: rowcount={result.rowcount}")
                                    
                                    if result.rowcount > 0:
                                        updated_fields.append(f"societe.{field_name}: → {processed_value}")
                                        logger.info(f"✅ Updated societe.{field_name} to: {processed_value}")
                                    else:
                                        logger.warning(f"⚠️ Update failed for societe.{field_name} - rowcount was 0")
                                else:
                                    logger.warning(f"⚠️ No societe record found for client {client_id} - creating one...")
                                    # Create the societe record if it doesn't exist
                                    try:
                                        insert_result = await self.session.execute(
                                            text(f'INSERT INTO societes ("idClient", "{db_column}") VALUES (:client_id, :value)'),
                                            {"client_id": client_id, "value": processed_value}
                                        )
                                        logger.info(f"✅ Created new societe record for client {client_id} with {field_name}: {processed_value}")
                                        updated_fields.append(f"societe.{field_name}: → {processed_value} (created)")
                                    except Exception as insert_error:
                                        logger.error(f"❌ Failed to create societe record: {insert_error}")
                                        raise
                            else:
                                logger.warning(f"⚠️ Field {field_name} not supported for societes table")
                
                # Always commit if we have any updates
                if updated_fields or related_updates:
                    logger.info(f"💾 Committing {len(updated_fields)} updates for client {client_id}...")
                    logger.info(f"💾 Total fields to commit: {len(updated_fields)} client fields + {len(related_updates)} related fields")
                    logger.info(f"💾 Updated fields details: {updated_fields}")
                    
                    # Check the current transaction status
                    logger.info(f"🔍 Session is active: {self.session.is_active}")
                    
                    await self.session.commit()
                    logger.info(f"✅ Commit completed successfully")
                    
                    # Verify the changes were actually persisted
                    await self.session.refresh(client)
                    logger.info(f"✅ Client refreshed after commit")
                    
                    # Double-check that the particulier/societe records were actually updated
                    if client.typeClient == 'PARTICULIER':
                        for field_name, field_value in related_updates:
                            if field_name in ['nom', 'prenom', 'cin']:  # Check key fields
                                verify_result = await self.session.execute(
                                    text('SELECT "{field}" FROM particuliers WHERE "idClient" = :client_id'.format(field=field_name)),
                                    {"client_id": client_id}
                                )
                                actual_value = verify_result.scalar()
                                logger.info(f"🔍 Verification: particulier.{field_name} = '{actual_value}' (expected: '{field_value}')")
                    
                    logger.info(f"✅ Successfully updated client {client_id}: {', '.join(updated_fields)}")
                else:
                    logger.info(f"ℹ️ No fields to update for client {client_id}")
                
                return client
            else:
                logger.warning(f"⚠️ Client {client_id} not found for update")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error updating client {client_id}: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            logger.debug(f"🔄 Rolling back update transaction for client {client_id}...")
            await self.session.rollback()
            raise

    async def delete_client(self, client_id: int) -> bool:
        """Delete a client and all related records"""
        logger.info(f"🗑️ Starting deletion of client {client_id}...")
        try:
            # Get the client first
            logger.debug(f"🔍 Fetching client {client_id} for deletion...")
            client = await self.get_client_by_id(client_id)
            if not client:
                logger.warning(f"⚠️ Client {client_id} not found for deletion")
                return False
            
            logger.info(f"✅ Client {client_id} found, type: {client.typeClient}")
            
            # Delete related records first (in reverse dependency order)
            # 1. Delete client relations (both as principal and as associate)
            logger.debug(f"🗑️ Deleting client relations for client {client_id}...")
            
            # First, log what relations will be affected
            relations_to_delete = await self.session.execute(
                text('SELECT "idClientPrincipal", "idClientLie" FROM clients_relations WHERE "idClientPrincipal" = :client_id OR "idClientLie" = :client_id'),
                {"client_id": client_id}
            )
            relations_list = relations_to_delete.fetchall()
            
            if relations_list:
                logger.info(f"📋 Found {len(relations_list)} relations to delete for client {client_id}:")
                for rel in relations_list:
                    if rel[0] == client_id:
                        logger.info(f"   - Client {client_id} is principal for associate {rel[1]}")
                    else:
                        logger.info(f"   - Client {client_id} is associate of principal {rel[0]}")
            
            # Now delete the relations
            result = await self.session.execute(
                text('DELETE FROM clients_relations WHERE "idClientPrincipal" = :client_id OR "idClientLie" = :client_id'),
                {"client_id": client_id}
            )
            deleted_relations = result.rowcount
            logger.info(f"🗑️ Deleted {deleted_relations} client relations for client {client_id}")
            
            # Log the impact on associated clients
            if deleted_relations > 0:
                logger.info(f"🔄 Associated clients will now return to the main clients table")
            
            # 2. Delete opportunities
            logger.debug(f"🗑️ Deleting opportunities for client {client_id}...")
            try:
                result = await self.session.execute(
                    text('DELETE FROM opportunites WHERE "idClient" = :client_id'),
                    {"client_id": client_id}
                )
                deleted_opportunities = result.rowcount
                logger.info(f"🗑️ Deleted {deleted_opportunities} opportunities for client {client_id}")
            except Exception as e:
                logger.error(f"❌ Error deleting opportunities: {e}")
                raise
            
            # 3. Delete contracts
            logger.debug(f"🗑️ Deleting contracts for client {client_id}...")
            try:
                result = await self.session.execute(
                    text('DELETE FROM contrats WHERE "idClient" = :client_id'),
                    {"client_id": client_id}
                )
                deleted_contracts = result.rowcount
                logger.info(f"🗑️ Deleted {deleted_contracts} contracts for client {client_id}")
            except Exception as e:
                logger.error(f"❌ Error deleting contracts: {e}")
                raise
            
            # 4. Delete adherents (flotte_auto, assure_sante, adherents_contrat)
            logger.debug(f"🗑️ Deleting flotte_auto records for client {client_id}...")
            try:
                result = await self.session.execute(
                    text('DELETE FROM flotte_auto WHERE "idClientSociete" = :client_id'),
                    {"client_id": client_id}
                )
                deleted_flotte_auto = result.rowcount
                logger.info(f"🗑️ Deleted {deleted_flotte_auto} flotte_auto records for client {client_id}")
            except Exception as e:
                logger.error(f"❌ Error deleting flotte_auto records: {e}")
                raise
            
            logger.debug(f"🗑️ Deleting assure_sante records for client {client_id}...")
            try:
                result = await self.session.execute(
                    text('DELETE FROM assure_sante WHERE "idClientSociete" = :client_id'),
                    {"client_id": client_id}
                )
                deleted_assure_sante = result.rowcount
                logger.info(f"🗑️ Deleted {deleted_assure_sante} assure_sante records for client {client_id}")
            except Exception as e:
                logger.error(f"❌ Error deleting assure_sante records: {e}")
                raise
            
            logger.debug(f"🗑️ Deleting adherents_contrat records for client {client_id}...")
            try:
                result = await self.session.execute(
                    text('DELETE FROM adherents_contrat WHERE "idClientSociete" = :client_id'),
                    {"client_id": client_id}
                )
                deleted_adherents_contrat = result.rowcount
                logger.info(f"🗑️ Deleted {deleted_adherents_contrat} adherents_contrat records for client {client_id}")
            except Exception as e:
                logger.error(f"❌ Error deleting adherents_contrat records: {e}")
                raise
            
            # 5. Delete documents
            logger.debug(f"🗑️ Deleting documents for client {client_id}...")
            try:
                result = await self.session.execute(
                    text('DELETE FROM documents WHERE "idEntite" = :client_id'),
                    {"client_id": client_id}
                )
                deleted_documents = result.rowcount
                logger.info(f"🗑️ Deleted {deleted_documents} documents for client {client_id}")
            except Exception as e:
                logger.error(f"❌ Error deleting documents: {e}")
                raise
            
            # 6. Delete particulier/societe records
            if client.typeClient == 'PARTICULIER':
                logger.debug(f"🗑️ Deleting particulier record for client {client_id}...")
                result = await self.session.execute(
                    text('DELETE FROM particuliers WHERE "idClient" = :client_id'),
                    {"client_id": client_id}
                )
                deleted_particulier = result.rowcount
                logger.info(f"🗑️ Deleted {deleted_particulier} particulier record for client {client_id}")
            elif client.typeClient == 'SOCIETE':
                logger.debug(f"🗑️ Deleting societe record for client {client_id}...")
                
                # First, update any other SOCIETEs that reference this one as societeMere
                logger.debug(f"🔄 Updating SOCIETEs that reference client {client_id} as societeMere...")
                try:
                    update_result = await self.session.execute(
                        text('UPDATE societes SET "societeMere" = NULL WHERE "societeMere" = :client_id'),
                        {"client_id": client_id}
                    )
                    updated_societes = update_result.rowcount
                    logger.info(f"✅ Updated {updated_societes} SOCIETEs that referenced client {client_id} as societeMere")
                except Exception as e:
                    logger.error(f"❌ Error updating societeMere references: {e}")
                    raise
                
                result = await self.session.execute(
                    text('DELETE FROM societes WHERE "idClient" = :client_id'),
                    {"client_id": client_id}
                )
                deleted_societe = result.rowcount
                logger.info(f"🗑️ Deleted {deleted_societe} societe record for client {client_id}")
            
            # 7. Finally delete the client
            logger.debug(f"🗑️ Deleting main client record {client_id}...")
            result = await self.session.execute(
                text('DELETE FROM clients WHERE id = :client_id'),
                {"client_id": client_id}
            )
            deleted_client = result.rowcount
            logger.info(f"🗑️ Deleted {deleted_client} client record for client {client_id}")
            
            # Commit all changes
            logger.debug(f"💾 Committing deletion transaction for client {client_id}...")
            await self.session.commit()
            
            # Verify that all relations were properly cleaned up
            logger.debug(f"🔍 Verifying cleanup of client relations for client {client_id}...")
            verification_result = await self.session.execute(
                text('SELECT COUNT(*) FROM clients_relations WHERE "idClientPrincipal" = :client_id OR "idClientLie" = :client_id'),
                {"client_id": client_id}
            )
            remaining_relations = verification_result.scalar()
            if remaining_relations == 0:
                logger.info(f"✅ Verification successful: No remaining relations for client {client_id}")
            else:
                logger.warning(f"⚠️ Verification failed: {remaining_relations} relations still exist for client {client_id}")
            
            logger.info(f"✅ Successfully deleted client {client_id} and all related records:")
            logger.info(f"   - Client relations: {deleted_relations}")
            logger.info(f"   - Opportunities: {deleted_opportunities}")
            logger.info(f"   - Contracts: {deleted_contracts}")
            logger.info(f"   - Flotte auto: {deleted_flotte_auto}")
            logger.info(f"   - Assure santé: {deleted_assure_sante}")
            logger.info(f"   - Adherents contrat: {deleted_adherents_contrat}")
            logger.info(f"   - Documents: {deleted_documents}")
            if client.typeClient == 'PARTICULIER':
                logger.info(f"   - Particulier record: {deleted_particulier}")
            elif client.typeClient == 'SOCIETE':
                logger.info(f"   - Societe record: {deleted_societe}")
            logger.info(f"   - Main client record: {deleted_client}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting client {client_id}: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            logger.debug(f"🔄 Rolling back deletion transaction for client {client_id}...")
            await self.session.rollback()
            raise

    def _compute_client_name(self, client: Client) -> str:
        """Compute the display name for a client (legacy method - not used anymore)"""
        if client.typeClient == 'PARTICULIER':
            if hasattr(client, 'particulier') and client.particulier:
                return f"{client.particulier.nom} {client.particulier.prenom}".strip()
            return "N/A"
        elif client.typeClient == 'SOCIETE':
            if hasattr(client, 'societe') and client.societe:
                return client.societe.nom
            return "N/A"
        return "N/A"
    
    def _compute_client_name_from_joined_data(self, typeClient: str, particulier_nom: str, particulier_prenom: str, societe_nom: str) -> str:
        """Compute the display name for a client from joined data (avoids lazy loading)"""
        if typeClient == 'PARTICULIER':
            if particulier_nom and particulier_prenom:
                return f"{particulier_nom} {particulier_prenom}".strip()
            elif particulier_nom:
                return particulier_nom
            elif particulier_prenom:
                return particulier_prenom
            return "N/A"
        elif typeClient == 'SOCIETE':
            if societe_nom:
                return societe_nom
            return "N/A"
        return "N/A"

    def get_client_types(self) -> List[str]:
        """Get all available client types"""
        logger.info("🔍 ClientRepository.get_client_types() called")
        try:
            result = ['PARTICULIER', 'SOCIETE']
            logger.info(f"✅ Returning client types: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ ClientRepository.get_client_types() failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise



    def get_client_importance_levels(self) -> List[str]:
        """Get all available importance levels"""
        return ['1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5']

    async def _is_client_associated(self, client_id: int) -> bool:
        """Check if a client is associated with another client (is a linked client)"""
        try:
            from model.client_relation import ClientRelation
            
            # Check if this client is linked to any other client
            result = await self.session.execute(
                select(ClientRelation).where(ClientRelation.idClientLie == client_id)
            )
            linked_relation = result.scalars().first()
            
            is_associated = linked_relation is not None
            logger.info(f"🔍 Client {client_id} association check: {is_associated}")
            return is_associated
            
        except Exception as e:
            logger.error(f"❌ Error checking client association for {client_id}: {str(e)}")
            # If there's an error, assume not associated to be safe
            return False
