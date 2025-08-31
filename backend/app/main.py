from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models to register them with SQLAlchemy
logger.info("📦 Importing models...")

try:
    from model.user import User
    logger.info("✅ User model imported")
except Exception as e:
    logger.error(f"❌ Failed to import User model: {e}")
    raise

try:
    from model.role import Role
    logger.info("✅ Role model imported")
except Exception as e:
    logger.error(f"❌ Failed to import Role model: {e}")
    raise

try:
    from model.client import Client, Particulier, Societe
    logger.info("✅ Client models imported")
except Exception as e:
    logger.error(f"❌ Failed to import Client models: {e}")
    raise

# Now import reference models after client models are imported
try:
    from model.reference import Compagnie, Banque, Ville, Branche, Duree
    logger.info("✅ Reference models imported")
except Exception as e:
    logger.error(f"❌ Failed to import Reference models: {e}")
    raise

try:
    from model.document import Document, Adherent
    logger.info("✅ Document models imported")
except Exception as e:
    logger.error(f"❌ Failed to import Document models: {e}")
    raise

try:
    from model.opportunity import Opportunity
    logger.info("✅ Opportunity models imported")
except Exception as e:
    logger.error(f"❌ Failed to import Opportunity models: {e}")
    raise

try:
    from model.contract import Contract
    logger.info("✅ Contract models imported")
except Exception as e:
    logger.error(f"❌ Failed to import Contract models: {e}")
    raise

try:
    from model.client_relation import ClientRelation, TypeRelation
    logger.info("✅ Client relation models imported")
except Exception as e:
    logger.error(f"❌ Failed to import Client relation models: {e}")
    raise

try:
    from model.produit import Produit, Garantie, SousGarantie
    logger.info("✅ Produit models imported")
except Exception as e:
    logger.error(f"❌ Failed to import Produit models: {e}")
    raise

try:
    from model.adherent import FlotteAuto, AssureSante, Marque, Carrosserie
    logger.info("✅ Adherent models imported")
except Exception as e:
    logger.error(f"❌ Failed to import Adherent models: {e}")
    raise





# Check SQLAlchemy model registration
logger.info("🔍 Checking SQLAlchemy model registration...")
try:
    from sqlalchemy import inspect
    # Skip engine inspection for now to avoid import issues
    logger.info("ℹ️ Skipping engine inspection to avoid import issues")
    pass
    
    # Simplified model registration check
    logger.info("✅ Models imported successfully")
    logger.info(f"🔍 Document model: {Document}")
    logger.info(f"🔍 Client model: {Client}")
        
except Exception as e:
    logger.error(f"❌ Error checking SQLAlchemy registration: {e}")
    import traceback
    logger.error(f"❌ Traceback: {traceback.format_exc()}")

from controller.auth_controller import router as auth_router
from controller.main_controller import router as main_router
from controller.admin_management_controller import router as admin_router
from controller.role_management_controller import router as role_management_router
from controller.user_management_controller import router as user_management_router
from controller.database_explorer_controller import router as database_explorer_router
from controller.client_controller import router as client_router
from controller.document_controller import router as document_router
from controller.opportunity_controller import router as opportunity_router
from controller.contract_controller import router as contract_router
from controller.client_relation_controller import router as client_relation_router
from controller.adherent_controller import router as adherent_router
from controller.csv_controller import router as csv_router

from controller.produit_controller import router as produit_router
from controller.reference_controller import router as reference_router

app = FastAPI(
    title="API d'Authentification",
    description="API pour la gestion de l'authentification des utilisateurs",
    version="1.0.0"
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"🌐 Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"🌐 Response status: {response.status_code}")
    return response

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"❌ Validation error: {exc}")
    logger.error(f"❌ Validation errors: {exc.errors()}")
    
    # Extract the first validation error message
    error_messages = []
    for error in exc.errors():
        field = error['loc'][-1] if error['loc'] else 'unknown'
        message = error['msg']
        error_messages.append(f"{field}: {message}")
    
    error_detail = "; ".join(error_messages)
    logger.error(f"❌ Formatted error: {error_detail}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": error_detail,
            "type": "validation_error"
        }
    )

# Inclure les routes d'authentification
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Inclure les routes principales (protégées)
app.include_router(main_router, prefix="/api", tags=["main"])

# Inclure les routes de gestion admin
app.include_router(admin_router, prefix="/admin", tags=["admin-management"])

# Inclure les routes de gestion des rôles
app.include_router(role_management_router, prefix="/admin", tags=["role-management"])

# Inclure les routes de gestion des utilisateurs
app.include_router(user_management_router, prefix="/admin", tags=["user-management"])

# Inclure les routes d'exploration de la base de données
app.include_router(database_explorer_router, prefix="/admin", tags=["database-explorer"])

# Inclure les routes de gestion des clients
logger.info("📦 Including client router...")
logger.info(f"🔍 Client router prefix: {client_router.prefix}")
logger.info(f"🔍 Client router tags: {client_router.tags}")
logger.info(f"🔍 Client router routes count: {len(client_router.routes)}")
for route in client_router.routes:
    if hasattr(route, 'path'):
        logger.info(f"🔍 Route: {route.methods} {route.path}")
app.include_router(client_router)
logger.info("✅ Client router included")

# Inclure les routes de gestion des documents
logger.info("📦 Including document router...")
logger.info(f"🔍 Document router prefix: {document_router.prefix}")
logger.info(f"🔍 Document router tags: {document_router.tags}")
logger.info(f"🔍 Document router routes count: {len(document_router.routes)}")
for route in document_router.routes:
    if hasattr(route, 'path'):
        logger.info(f"🔍 Route: {route.methods} {route.path}")
app.include_router(document_router)
logger.info("✅ Document router included")

# Add static file serving for uploaded documents
try:
    # Create uploads directory if it doesn't exist
    # Use the same path as the document controller (backend/uploads)
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(current_dir)
    uploads_dir = os.path.join(backend_dir, "uploads")
    
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        logger.info(f"📁 Created uploads directory: {uploads_dir}")
    else:
        logger.info(f"📁 Uploads directory already exists: {uploads_dir}")
    
    # Mount the uploads directory for static file serving
    app.mount("/api/documents/files", StaticFiles(directory=uploads_dir), name="document-files")
    logger.info("✅ Static file serving mounted for documents at /api/documents/files")
    logger.info(f"📁 Serving files from: {uploads_dir}")
except Exception as e:
    logger.error(f"❌ Failed to mount static file serving: {e}")
    logger.error(f"❌ Error type: {type(e).__name__}")
    import traceback
    logger.error(f"❌ Traceback: {traceback.format_exc()}")

# Inclure les routes de gestion des opportunités
logger.info("📦 Including opportunity router...")
app.include_router(opportunity_router)
logger.info("✅ Opportunity router included")

# Inclure les routes de gestion des contrats
logger.info("📦 Including contract router...")
app.include_router(contract_router)
logger.info("✅ Contract router included")

# Inclure les routes de gestion des relations clients
logger.info("📦 Including client relation router...")
app.include_router(client_relation_router)
logger.info("✅ Client relation router included")

# Inclure les routes de gestion des adhérents
logger.info("📦 Including adherent router...")
app.include_router(adherent_router)
logger.info("✅ Adherent router included")

# Inclure les routes de gestion des données CSV
logger.info("📦 Including CSV router...")
app.include_router(csv_router)
logger.info("✅ CSV router included")

# Inclure les routes de gestion des données CSV adhérents
logger.info("📦 Including CSV adherents router...")

logger.info("✅ CSV adherents router included")

# Inclure les routes de gestion des produits
logger.info("📦 Including produit router...")
app.include_router(produit_router)
logger.info("✅ Produit router included")

# Inclure les routes de gestion des références
logger.info("📦 Including reference router...")
app.include_router(reference_router, prefix="/api/references")
logger.info("✅ Reference router included")

# Log all registered routes
logger.info("🔍 Logging all registered routes...")
for route in app.routes:
    if hasattr(route, 'path'):
        # Handle regular routes
        if hasattr(route, 'methods'):
            logger.info(f"🔍 App Route: {route.methods} {route.path}")
        else:
            # Handle mounted routes (like static file serving)
            logger.info(f"🔍 App Mount: {route.path}")
    else:
        # Handle other types of routes
        logger.info(f"🔍 App Route: {type(route).__name__}")
@app.get("/health")
def health_check():
    """Endpoint de vérification de santé pour Docker"""
    return {"status": "healthy", "timestamp": "2025-08-11T19:37:00Z"}

@app.get("/")
def root():
    logger.info("🔍 Root endpoint called")
    return {
        "message": "Bienvenue dans l'API d'Authentification !",
        "version": "1.0.0",
        "endpoints": {
            "login": "/auth/login",
            "me": "/auth/me",

            "home": "/api/home",

            "create_role": "/admin/roles",
            "list_roles": "/admin/roles",
            "get_role": "/admin/roles/{role_id}",
            "update_role": "/admin/roles/{role_id}",
            "delete_role": "/admin/roles/{role_id}",
            "create_user": "/admin/users",
            "list_users": "/admin/users",
            "get_user": "/admin/users/{user_id}",
            "update_user": "/admin/users/{user_id}",
            "delete_user": "/admin/users/{user_id}",
            "reset_password": "/admin/users/{user_id}/reset-password",

            "database_explorer": "/admin/tables",
            "table_structure": "/admin/tables/{table_name}/structure",
            "table_data": "/admin/tables/{table_name}/data",
            "create_row": "/admin/tables/{table_name}/rows",
            "update_row": "/admin/tables/{table_name}/rows/{row_id}",
            "delete_row": "/admin/tables/{table_name}/rows/{row_id}",

            "clients": "/api/clients",
            "get_client": "/api/clients/{client_id}",
            "create_client": "/api/clients",
            "update_client": "/api/clients/{client_id}",
            "delete_client": "/api/clients/{client_id}",
            "verify_cleanup": "/api/clients/{client_id}/verify-cleanup",
            "cleanup_orphaned": "/api/clients/cleanup-orphaned-relations",
            "client_types": "/api/clients/types/list",
    
            "client_importance": "/api/clients/importance/list",

            "docs": "/docs"
        },
    }

# Add a catch-all handler for unmatched routes
@app.exception_handler(404)
async def not_found_handler(request, exc):
    # Skip handling for static file paths - let them be handled by the static file middleware
    if request.url.path.startswith("/api/documents/files/"):
        # Let the static file middleware handle this
        raise exc
    
    logger.error(f"❌ 404 Not Found: {request.method} {request.url.path}")
    logger.error(f"❌ Available routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            # Handle regular routes
            if hasattr(route, 'methods'):
                logger.error(f"❌   {route.methods} {route.path}")
            else:
                # Handle mounted routes (like static file serving)
                logger.error(f"❌   MOUNT {route.path}")
        else:
            # Handle other types of routes
            logger.error(f"❌   {type(route).__name__}")
    # Return a proper JSONResponse instead of a dict
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={"detail": "Not Found", "path": request.url.path}
    )
