from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controller.auth_controller import router as auth_router
from controller.main_controller import router as main_router
from controller.admin_management_controller import router as admin_router
from controller.role_management_controller import router as role_management_router
from controller.user_management_controller import router as user_management_router


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

            "docs": "/docs"
        },

    }
