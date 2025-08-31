#!/usr/bin/env python3
"""
Data initialization script for the PFA application
This script populates essential reference tables with data from INSURFORCE_DB.xlsx
"""

import asyncio
import sys
import os
from datetime import date
import logging

# Configure comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('init_data.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path to import models
# Handle both direct execution and subprocess execution
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
backend_dir = os.path.dirname(parent_dir)

# Add multiple possible paths
sys.path.insert(0, parent_dir)  # backend/
sys.path.insert(0, backend_dir)  # PFA/
sys.path.insert(0, os.path.join(backend_dir, 'backend'))  # PFA/backend/

logger.info("🚀 Starting database initialization script...")
logger.info(f"🔍 Current working directory: {os.getcwd()}")
logger.info(f"🔍 Current script directory: {current_dir}")
logger.info(f"🔍 Parent directory: {parent_dir}")
logger.info(f"🔍 Backend directory: {backend_dir}")
logger.info(f"🔍 Python path: {sys.path}")

try:
    logger.info("📦 Importing database configuration...")
    from config.database.database import get_session
    logger.info("✅ Database configuration imported successfully")
except Exception as e:
    logger.error(f"❌ Failed to import database configuration: {e}")
    logger.error(f"❌ Error type: {type(e).__name__}")
    import traceback
    logger.error(f"❌ Traceback: {traceback.format_exc()}")
    raise

try:
    logger.info("📦 Importing models...")
    from model.produit import Produit, Garantie, SousGarantie
    logger.info("✅ Produit models imported successfully")
    from model.adherent import Marque, Carrosserie
    logger.info("✅ Adherent models imported successfully")
    from model.client_relation import TypeRelation
    logger.info("✅ Client relation models imported successfully")
    from model.reference import Compagnie, Banque, Ville, Branche, Duree
    logger.info("✅ Reference models imported successfully")
    logger.info("✅ All models imported successfully")
except Exception as e:
    logger.error(f"❌ Failed to import models: {e}")
    logger.error(f"❌ Error type: {type(e).__name__}")
    import traceback
    logger.error(f"❌ Traceback: {traceback.format_exc()}")
    raise

async def check_data_exists(db, model_class, filter_field, filter_value):
    """Check if data already exists in the database"""
    try:
        from sqlalchemy import select
        query = select(model_class).where(getattr(model_class, filter_field) == filter_value)
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
    except Exception as e:
        logger.warning(f"⚠️ Could not check if {model_class.__name__} exists: {e}")
        return False

async def init_data():
    """Initialize the database with sample data"""
    logger.info("🔄 Starting init_data function...")
    
    try:
        logger.info("🔄 Getting database session...")
        async for db in get_session():
            logger.info("✅ Database session obtained successfully")
            
            try:
                logger.info("🚀 Initializing database with reference data...")
                
                # Initialize villes (cities) - essential for addresses
                logger.info("🏙️ Creating villes...")
                try:
                    villes_data = [
                        ("CASA", "Casablanca"),
                        ("RABAT", "Rabat"),
                        ("FES", "Fès"),
                        ("MARRAKECH", "Marrakech"),
                        ("TANGER", "Tanger"),
                        ("AGADIR", "Agadir"),
                        ("OUJDA", "Oujda"),
                        ("KENITRA", "Kénitra"),
                        ("TETOUAN", "Tétouan"),
                        ("MEKNES", "Meknès")
                    ]
                    
                    villes_created = 0
                    for code, libelle in villes_data:
                        # Check if ville already exists
                        if not await check_data_exists(db, Ville, "codeVilles", code):
                            ville = Ville(codeVilles=code, libelle=libelle)
                            logger.debug(f"📝 Adding new ville: {code} - {libelle}")
                            db.add(ville)
                            villes_created += 1
                        else:
                            logger.debug(f"ℹ️ Ville {code} already exists, skipping")
                    
                    if villes_created > 0:
                        logger.info("💾 Committing new villes to database...")
                        await db.commit()
                        logger.info(f"✅ Successfully created {villes_created} new villes")
                    else:
                        logger.info("ℹ️ All villes already exist, no new ones created")
                except Exception as e:
                    logger.error(f"❌ Error creating villes: {e}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    raise
                
                # Initialize compagnies (insurance companies)
                logger.info("🏢 Creating compagnies...")
                try:
                    compagnies_data = [
                        ("AXA", "AXA Assurance Maroc", "Casablanca", "+212 5 22 99 99 99", True),
                        ("ALLIANZ", "Allianz Maroc", "Casablanca", "+212 5 22 99 99 99", True),
                        ("GENERALI", "Generali Maroc", "Casablanca", "+212 5 22 99 99 99", True),
                        ("RMA", "RMA Watanya", "Casablanca", "+212 5 22 99 99 99", True),
                        ("WAFAA", "Wafa Assurance", "Casablanca", "+212 5 22 99 99 99", True),
                        ("ATLANTA", "Atlanta Sanad", "Casablanca", "+212 5 22 99 99 99", True),
                        ("CNIA", "CNIA Saada", "Casablanca", "+212 5 22 99 99 99", True),
                        ("MCMA", "MCMA Chifaa", "Casablanca", "+212 5 22 99 99 99", True)
                    ]
                    
                    compagnies_created = 0
                    for code, nom, adresse, contact, actif in compagnies_data:
                        # Check if compagnie already exists
                        if not await check_data_exists(db, Compagnie, "codeCIE", code):
                            compagnie = Compagnie(codeCIE=code, nom=nom, adresse=adresse, contact=contact, actif=actif)
                            logger.debug(f"📝 Adding new compagnie: {code} - {nom}")
                            db.add(compagnie)
                            compagnies_created += 1
                        else:
                            logger.debug(f"ℹ️ Compagnie {code} already exists, skipping")
                    
                    if compagnies_created > 0:
                        logger.info("💾 Committing new compagnies to database...")
                        await db.commit()
                        logger.info(f"✅ Successfully created {compagnies_created} new compagnies")
                    else:
                        logger.info("ℹ️ All compagnies already exist, no new ones created")
                except Exception as e:
                    logger.error(f"❌ Error creating compagnies: {e}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    raise
                
                # Initialize banques (banks)
                logger.info("🏦 Creating banques...")
                try:
                    banques_data = [
                        ("ATW", "Attijariwafa Bank"),
                        ("BMCE", "BMCE Bank"),
                        ("SGMB", "Société Générale Maroc"),
                        ("CFG", "CFG Bank"),
                        ("BMCI", "BMCI"),
                        ("CIH", "CIH Bank"),
                        ("ALBARID", "Al Barid Bank"),
                        ("BANK_ALMAGHRIB", "Bank Al-Maghrib")
                    ]
                    
                    banques_created = 0
                    for code, libelle in banques_data:
                        # Check if banque already exists
                        if not await check_data_exists(db, Banque, "codeBanques", code):
                            banque = Banque(codeBanques=code, libelle=libelle)
                            logger.debug(f"📝 Adding new banque: {code} - {libelle}")
                            db.add(banque)
                            banques_created += 1
                        else:
                            logger.debug(f"ℹ️ Banque {code} already exists, skipping")
                    
                    if banques_created > 0:
                        logger.info("💾 Committing new banques to database...")
                        await db.commit()
                        logger.info(f"✅ Successfully created {banques_created} new banques")
                    else:
                        logger.info("ℹ️ All banques already exist, no new ones created")
                except Exception as e:
                    logger.error(f"❌ Error creating banques: {e}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    raise
                
                # Initialize marques (car brands)
                logger.info("🚗 Creating marques...")
                try:
                    marques_data = [
                        ("HONDA", "Honda"),
                        ("MERCEDES", "Mercedes-Benz"),
                        ("BMW", "BMW"),
                        ("AUDI", "Audi"),
                        ("TOYOTA", "Toyota"),
                        ("NISSAN", "Nissan"),
                        ("VOLKSWAGEN", "Volkswagen"),
                        ("PEUGEOT", "Peugeot"),
                        ("RENAULT", "Renault"),
                        ("FORD", "Ford"),
                        ("HYUNDAI", "Hyundai"),
                        ("KIA", "Kia"),
                        ("MAZDA", "Mazda"),
                        ("MITSUBISHI", "Mitsubishi"),
                        ("OPEL", "Opel"),
                        ("CITROEN", "Citroën"),
                        ("SKODA", "Škoda"),
                        ("SEAT", "Seat"),
                        ("FIAT", "Fiat"),
                        ("ALFA_ROMEO", "Alfa Romeo")
                    ]
                    
                    marques_created = 0
                    for code, libelle in marques_data:
                        # Check if marque already exists
                        if not await check_data_exists(db, Marque, "codeMarques", code):
                            marque = Marque(codeMarques=code, libelle=libelle)
                            logger.debug(f"📝 Adding new marque: {code} - {libelle}")
                            db.add(marque)
                            marques_created += 1
                        else:
                            logger.debug(f"ℹ️ Marque {code} already exists, skipping")
                    
                    if marques_created > 0:
                        logger.info("💾 Committing new marques to database...")
                        await db.commit()
                        logger.info(f"✅ Successfully created {marques_created} new marques")
                    else:
                        logger.info("ℹ️ All marques already exist, no new ones created")
                except Exception as e:
                    logger.error(f"❌ Error creating marques: {e}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    raise
                
                # Initialize carrosseries (car body types)
                logger.info("🚙 Creating carrosseries...")
                try:
                    carrosseries_data = [
                        ("BERLINE", "Berline"),
                        ("SUV", "SUV"),
                        ("BREAK", "Break"),
                        ("COUPE", "Coupé"),
                        ("CABRIOLET", "Cabriolet"),
                        ("MONOSPACE", "Monospace"),
                        ("PICKUP", "Pick-up"),
                        ("FOURGON", "Fourgon"),
                        ("CITADINE", "Citadine"),
                        ("ROUTIERE", "Routière")
                    ]
                    
                    carrosseries_created = 0
                    for code, libelle in carrosseries_data:
                        # Check if carrosserie already exists
                        if not await check_data_exists(db, Carrosserie, "codeCarrosseries", code):
                            carrosserie = Carrosserie(codeCarrosseries=code, libelle=libelle)
                            logger.debug(f"📝 Adding new carrosserie: {code} - {libelle}")
                            db.add(carrosserie)
                            carrosseries_created += 1
                        else:
                            logger.debug(f"ℹ️ Carrosserie {code} already exists, skipping")
                    
                    if carrosseries_created > 0:
                        logger.info("💾 Committing new carrosseries to database...")
                        await db.commit()
                        logger.info(f"✅ Successfully created {carrosseries_created} new carrosseries")
                    else:
                        logger.info("ℹ️ All carrosseries already exist, no new ones created")
                except Exception as e:
                    logger.error(f"❌ Error creating carrosseries: {e}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    raise
                
                # Initialize durees (duration types) - essential for contracts
                logger.info("⏱️ Creating durees...")
                try:
                    durees_data = [
                        ("MENSUEL", "Mensuel", 1),
                        ("TRIMESTRIEL", "Trimestriel", 3),
                        ("SEMESTRIEL", "Semestriel", 6),
                        ("ANNUEL", "Annuel", 12)
                    ]
                    
                    durees_created = 0
                    for code_duree, libelle, nb_mois in durees_data:
                        # Check if duree already exists
                        if not await check_data_exists(db, Duree, "codeDuree", code_duree):
                            duree = Duree(codeDuree=code_duree, libelle=libelle, nbMois=nb_mois)
                            logger.debug(f"📝 Adding new duree: {code_duree} - {libelle} ({nb_mois} mois)")
                            db.add(duree)
                            durees_created += 1
                        else:
                            logger.debug(f"ℹ️ Duree {code_duree} already exists, skipping")
                    
                    if durees_created > 0:
                        logger.info("💾 Committing new durees to database...")
                        await db.commit()
                        logger.info(f"✅ Successfully created {durees_created} new durees")
                    else:
                        logger.info("ℹ️ All durees already exist, no new ones created")
                except Exception as e:
                    logger.error(f"❌ Error creating durees: {e}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    raise
                
                # Initialize produits (products) - essential for opportunities and contracts
                logger.info("📦 Creating produits...")
                try:
                    produits_data = [
                        ("FLOTTE_AUTO", "Flotte Automobile", "Assurance flotte automobile pour entreprises"),
                        ("SANTE", "Santé", "Assurance santé collective pour entreprises"),
                        ("HABITATION", "Habitation", "Assurance habitation"),
                        ("AUTOMOBILE", "Automobile", "Assurance automobile individuelle"),
                        ("VIE", "Vie", "Assurance vie"),
                        ("TRANSPORT", "Transport", "Assurance transport de marchandises"),
                        ("RESPONSABILITE", "Responsabilité Civile", "Assurance responsabilité civile"),
                        ("AGRICOLE", "Agricole", "Assurance agricole")
                    ]
                    
                    produits_created = 0
                    produits = []
                    for code, libelle, description in produits_data:
                        # Check if produit already exists
                        if not await check_data_exists(db, Produit, "codeProduit", code):
                            produit = Produit(codeProduit=code, libelle=libelle, description=description)
                            logger.debug(f"📝 Adding new produit: {code} - {libelle}")
                            db.add(produit)
                            produits.append(produit)
                            produits_created += 1
                        else:
                            logger.debug(f"ℹ️ Produit {code} already exists, skipping")
                    
                    if produits_created > 0:
                        logger.info("💾 Committing new produits to database...")
                        await db.commit()
                        logger.info(f"✅ Successfully created {produits_created} new produits")
                    else:
                        logger.info("ℹ️ All produits already exist, no new ones created")
                except Exception as e:
                    logger.error(f"❌ Error creating produits: {e}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    raise
                
                # Initialize garanties (guarantees) - essential for products
                logger.info("🛡️ Creating garanties...")
                try:
                    garanties_data = [
                        ("VOL", "Vol"),
                        ("INCENDIE", "Incendie"),
                        ("COLLISION", "Collision"),
                        ("VOL_AGRAVATION", "Vol avec aggravation"),
                        ("BAGAGES", "Bagages"),
                        ("DEFENSE_RECOURS", "Défense et recours"),
                        ("ASSISTANCE", "Assistance"),
                        ("PROTECTION_JURIDIQUE", "Protection juridique"),
                        ("DOMICILE", "Dommage au domicile"),
                        ("CATASTROPHES", "Catastrophes naturelles")
                    ]
                    
                    garanties_created = 0
                    garanties = []
                    for code, libelle in garanties_data:
                        # Check if garantie already exists
                        if not await check_data_exists(db, Garantie, "codeGarantie", code):
                            garantie = Garantie(codeGarantie=code, libelle=libelle)
                            logger.debug(f"📝 Adding new garantie: {code} - {libelle}")
                            db.add(garantie)
                            garanties.append(garantie)
                            garanties_created += 1
                        else:
                            logger.debug(f"ℹ️ Garantie {code} already exists, skipping")
                    
                    if garanties_created > 0:
                        logger.info("💾 Committing new garanties to database...")
                        await db.commit()
                        logger.info(f"✅ Successfully created {garanties_created} new garanties")
                    else:
                        logger.info("ℹ️ All garanties already exist, no new ones created")
                except Exception as e:
                    logger.error(f"❌ Error creating garanties: {e}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    raise
                
                # Initialize sous_garanties (sub-guarantees)
                logger.info("🔒 Creating sous_garanties...")
                try:
                    sous_garanties_data = [
                        ("VOL_SIMPLE", "Vol simple"),
                        ("VOL_AGRAVE", "Vol aggravé"),
                        ("INCENDIE_SIMPLE", "Incendie simple"),
                        ("INCENDIE_ETENDU", "Incendie étendu"),
                        ("COLLISION_SIMPLE", "Collision simple"),
                        ("COLLISION_ETENDU", "Collision étendu"),
                        ("BAGAGES_MAIN", "Bagages à main"),
                        ("BAGAGES_SOUTE", "Bagages en soute"),
                        ("ASSISTANCE_0KM", "Assistance 0 km"),
                        ("ASSISTANCE_ROUTE", "Assistance route")
                    ]
                    
                    sous_garanties_created = 0
                    sous_garanties = []
                    for code, libelle in sous_garanties_data:
                        # Check if sous_garantie already exists
                        if not await check_data_exists(db, SousGarantie, "codeSousGarantie", code):
                            sous_garantie = SousGarantie(codeSousGarantie=code, libelle=libelle)
                            logger.debug(f"📝 Adding new sous_garantie: {code} - {libelle}")
                            db.add(sous_garantie)
                            sous_garanties.append(sous_garantie)
                            sous_garanties_created += 1
                        else:
                            logger.debug(f"ℹ️ Sous_garantie {code} already exists, skipping")
                    
                    if sous_garanties_created > 0:
                        logger.info("💾 Committing new sous_garanties to database...")
                        await db.commit()
                        logger.info(f"✅ Successfully created {sous_garanties_created} new sous_garanties")
                    else:
                        logger.info("ℹ️ All sous_garanties already exist, no new ones created")
                except Exception as e:
                    logger.error(f"❌ Error creating sous_garanties: {e}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    raise
                
                # Initialize branches (insurance branches)
                logger.info("🌿 Creating branches...")
                try:
                    branches_data = [
                        ("AUTO", "Automobile"),
                        ("HABITATION", "Habitation"),
                        ("SANTE", "Santé"),
                        ("VIE", "Vie"),
                        ("TRANSPORT", "Transport"),
                        ("RESPONSABILITE", "Responsabilité Civile"),
                        ("AGRICOLE", "Agricole"),
                        ("AVIATION", "Aviation"),
                        ("MARITIME", "Maritime"),
                        ("ENGINEERING", "Engineering")
                    ]
                    
                    branches_created = 0
                    for code, libelle in branches_data:
                        # Check if branche already exists
                        if not await check_data_exists(db, Branche, "codeBranche", code):
                            branche = Branche(codeBranche=code, libelle=libelle)
                            logger.debug(f"📝 Adding new branche: {code} - {libelle}")
                            db.add(branche)
                            branches_created += 1
                        else:
                            logger.debug(f"ℹ️ Branche {code} already exists, skipping")
                    
                    if branches_created > 0:
                        logger.info("💾 Committing new branches to database...")
                        await db.commit()
                        logger.info(f"✅ Successfully created {branches_created} new branches")
                    else:
                        logger.info("ℹ️ All branches already exist, no new ones created")
                except Exception as e:
                    logger.error(f"❌ Error creating branches: {e}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    raise
                
                # Initialize type relations (client relationship types)
                logger.info("🔗 Creating type relations...")
                try:
                    type_relations_data = [
                        ("FAMILLE", "Famille"),
                        ("COLLEGUE", "Collègue"),
                        ("PARTENAIRE", "Partenaire"),
                        ("CLIENT", "Client"),
                        ("FOURNISSEUR", "Fournisseur"),
                        ("ACTIONNAIRE", "Actionnaire"),
                        ("DIRIGEANT", "Dirigeant"),
                        ("EMPLOYE", "Employé"),
                        ("CONCURRENT", "Concurrent"),
                        ("SOUS_TRAITANT", "Sous-traitant")
                    ]
                    
                    type_relations_created = 0
                    for code, libelle in type_relations_data:
                        # Check if type_relation already exists
                        if not await check_data_exists(db, TypeRelation, "codeTypeRelation", code):
                            type_relation = TypeRelation(codeTypeRelation=code, libelle=libelle)
                            logger.debug(f"📝 Adding new type_relation: {code} - {libelle}")
                            db.add(type_relation)
                            type_relations_created += 1
                        else:
                            logger.debug(f"ℹ️ Type_relation {code} already exists, skipping")
                    
                    if type_relations_created > 0:
                        logger.info("💾 Committing new type relations to database...")
                        await db.commit()
                        logger.info(f"✅ Successfully created {type_relations_created} new type relations")
                    else:
                        logger.info("ℹ️ All type relations already exist, no new ones created")
                except Exception as e:
                    logger.error(f"❌ Error creating type relations: {e}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    raise
                
                # Now establish relationships between produits, garanties, and sous_garanties
                logger.info("🔗 Establishing relationships between produits, garanties, and sous_garanties...")
                try:
                    # Link produits to garanties and sous_garanties
                    for produit in produits:
                        if produit.codeProduit == "FLOTTE_AUTO":
                            produit.codeGarantie = "VOL"
                            produit.codeSousGarantie = "VOL_SIMPLE"
                        elif produit.codeProduit == "AUTOMOBILE":
                            produit.codeGarantie = "COLLISION"
                            produit.codeSousGarantie = "COLLISION_SIMPLE"
                        elif produit.codeProduit == "HABITATION":
                            produit.codeGarantie = "INCENDIE"
                            produit.codeSousGarantie = "INCENDIE_SIMPLE"
                        elif produit.codeProduit == "TRANSPORT":
                            produit.codeGarantie = "VOL"
                            produit.codeSousGarantie = "VOL_AGRAVE"
                        elif produit.codeProduit == "RESPONSABILITE":
                            produit.codeGarantie = "PROTECTION_JURIDIQUE"
                            produit.codeSousGarantie = None
                        else:
                            # Default values for other products
                            produit.codeGarantie = "ASSISTANCE"
                            produit.codeSousGarantie = "ASSISTANCE_0KM"
                    
                    # Link sous_garanties to garanties
                    for sous_garantie in sous_garanties:
                        if "VOL" in sous_garantie.codeSousGarantie:
                            # Find the VOL garantie
                            vol_garantie = next((g for g in garanties if g.codeGarantie == "VOL"), None)
                            if vol_garantie:
                                sous_garantie.idGarantie = vol_garantie.id
                        elif "INCENDIE" in sous_garantie.codeSousGarantie:
                            # Find the INCENDIE garantie
                            incendie_garantie = next((g for g in garanties if g.codeGarantie == "INCENDIE"), None)
                            if incendie_garantie:
                                sous_garantie.idGarantie = incendie_garantie.id
                        elif "COLLISION" in sous_garantie.codeSousGarantie:
                            # Find the COLLISION garantie
                            collision_garantie = next((g for g in garanties if g.codeGarantie == "COLLISION"), None)
                            if collision_garantie:
                                sous_garantie.idGarantie = collision_garantie.id
                        elif "ASSISTANCE" in sous_garantie.codeSousGarantie:
                            # Find the ASSISTANCE garantie
                            assistance_garantie = next((g for g in garanties if g.codeGarantie == "ASSISTANCE"), None)
                            if assistance_garantie:
                                sous_garantie.idGarantie = assistance_garantie.id
                        elif "BAGAGES" in sous_garantie.codeSousGarantie:
                            # Find the BAGAGES garantie
                            bagages_garantie = next((g for g in garanties if g.codeGarantie == "BAGAGES"), None)
                            if bagages_garantie:
                                sous_garantie.idGarantie = bagages_garantie.id
                    
                    logger.info("💾 Committing relationship updates to database...")
                    await db.commit()
                    logger.info("✅ Successfully established relationships")
                except Exception as e:
                    logger.error(f"❌ Error establishing relationships: {e}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    raise
                    
                logger.info("🎉 Database initialization completed successfully!")
                logger.info("📊 Summary of created records:")
                logger.info(f"   - {villes_created} villes")
                logger.info(f"   - {compagnies_created} compagnies")
                logger.info(f"   - {banques_created} banques")
                logger.info(f"   - {marques_created} marques")
                logger.info(f"   - {carrosseries_created} carrosseries")
                logger.info(f"   - {durees_created} durees")
                logger.info(f"   - {produits_created} produits")
                logger.info(f"   - {garanties_created} garanties")
                logger.info(f"   - {sous_garanties_created} sous_garanties")
                logger.info(f"   - {branches_created} branches")
                logger.info(f"   - {type_relations_created} type relations")
                
            except Exception as e:
                logger.error(f"❌ Error during initialization: {e}")
                logger.error(f"❌ Error type: {type(e).__name__}")
                import traceback
                logger.error(f"❌ Traceback: {traceback.format_exc()}")
                await db.rollback()
                raise
            finally:
                logger.info("🔄 Closing database session...")
                await db.close()
                logger.info("✅ Database session closed")
                    
    except Exception as e:
        logger.error(f"❌ Critical error in init_data: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    logger.info("🚀 Script started - running init_data...")
    try:
        asyncio.run(init_data())
        logger.info("🎉 Script completed successfully!")
    except Exception as e:
        logger.error(f"❌ Script failed: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        sys.exit(1)
