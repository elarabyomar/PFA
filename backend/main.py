from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controller.auth_controller import router as auth_router
from controller.main_controller import router as main_router
from controller.admin_management_controller import router as admin_router
from controller.role_management_controller import router as role_management_router
from controller.user_management_controller import router as user_management_router
from controller.database_explorer_controller import router as database_explorer_router
from controller.client_controller import router as client_router


app = FastAPI(
    title="API d'Authentification",
    description="API pour la gestion de l'authentification des utilisateurs",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(client_router)


@app.get("/health")
def health_check():
    """Endpoint de vérification de santé pour Docker"""
    return {"status": "healthy", "timestamp": "2025-08-11T19:37:00Z"}

@app.get("/")
def root():
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
            "client_types": "/api/clients/types/list",
            "client_statuts": "/api/clients/statuts/list",
            "client_importance": "/api/clients/importance/list",

            "docs": "/docs"
        },

    }
