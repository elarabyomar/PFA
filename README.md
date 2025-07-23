# Système d'Authentification - Backend + Frontend

Un système d'authentification complet avec backend FastAPI et frontend React.

## 🏗️ Architecture

```
auth/
├── backend/          # API FastAPI
│   ├── app/         # Point d'entrée
│   ├── config/      # Configuration DB
│   ├── controller/  # Contrôleurs API
│   ├── service/     # Logique métier
│   ├── repository/  # Accès aux données
│   ├── model/       # Modèles SQLAlchemy
│   ├── dto/         # Data Transfer Objects
│   └── security/    # Middleware auth
├── frontend/        # Application React
│   ├── src/         # Code source
│   ├── public/      # Fichiers publics
│   └── Dockerfile   # Configuration Docker
└── docker-compose.yml  # Orchestration complète
```

## 🚀 Technologies

### Backend
- **FastAPI** - Framework web Python
- **SQLAlchemy** - ORM
- **PostgreSQL** - Base de données
- **JWT** - Authentification
- **bcrypt** - Hachage des mots de passe

### Frontend
- **React 18** - Framework JavaScript
- **Material-UI** - Composants UI
- **React Router** - Routing
- **Axios** - Client HTTP
- **Formik & Yup** - Formulaires et validation

## 📦 Installation et démarrage

### Option 1: Docker (Recommandé)

```bash
# Cloner le projet
git clone <repository-url>
cd auth

# Démarrer tous les services
docker-compose up --build

# Ou démarrer avec le frontend en mode développement
docker-compose --profile dev up --build
```

### Option 2: Développement local

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

## 🌐 Services disponibles

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **pgAdmin** : http://localhost:5050 (admin@admin.com / admin)

## 🔐 Authentification

### Utilisateur admin par défaut
- **Email** : admin@gmail.com
- **Mot de passe** : admin
- **Rôle** : admin

### Première connexion
Lors de la première connexion admin, le système détecte automatiquement l'utilisation du mot de passe par défaut et demande de le changer avec des règles de sécurité strictes.

## 📋 Fonctionnalités

### Backend
- ✅ Authentification JWT
- ✅ Gestion des utilisateurs
- ✅ Gestion des rôles (CRUD)
- ✅ Changement de mot de passe admin
- ✅ Validation stricte des mots de passe
- ✅ Middleware de sécurité
- ✅ Documentation automatique (Swagger)

### Frontend
- ✅ Interface utilisateur moderne
- ✅ Authentification sécurisée
- ✅ Gestion des rôles
- ✅ Formulaires validés
- ✅ Notifications toast
- ✅ Routing protégé
- ✅ Design responsive

## 🔧 Configuration

### Variables d'environnement

#### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://postgrestest:SYS@db:5432/test3
JWT_SECRET=your_super_secret_key_change_in_production
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

## 📁 Structure détaillée

### Backend
```
backend/
├── app/main.py                    # Point d'entrée FastAPI
├── config/database/
│   ├── database.py               # Configuration DB
│   └── init.sql                  # Script d'initialisation
├── controller/
│   ├── auth_controller.py        # Contrôleur authentification
│   ├── main_controller.py        # Contrôleur principal
│   ├── admin_management_controller.py  # Gestion admin
│   └── role_management_controller.py   # Gestion rôles
├── service/
│   ├── auth_service.py           # Service authentification
│   ├── admin_management_service.py     # Service admin
│   └── role_management_service.py      # Service rôles
├── repository/
│   ├── user_repository.py        # Repository utilisateurs
│   └── role_repository.py        # Repository rôles
├── model/
│   ├── user.py                   # Modèle utilisateur
│   └── role.py                   # Modèle rôle
├── dto/
│   ├── user_dto.py               # DTO utilisateur
│   ├── admin_password_dto.py     # DTO mot de passe admin
│   └── role_dto.py               # DTO rôles
└── security/
    └── auth_middleware.py        # Middleware JWT
```

### Frontend
```
frontend/
├── src/
│   ├── components/               # Composants réutilisables
│   ├── pages/                   # Pages de l'application
│   ├── services/                # Services API
│   ├── hooks/                   # Hooks personnalisés
│   ├── utils/                   # Utilitaires
│   ├── context/                 # Context React
│   └── styles/                  # Styles CSS
├── public/                      # Fichiers publics
├── Dockerfile                   # Docker production
├── Dockerfile.dev               # Docker développement
└── nginx.conf                   # Configuration Nginx
```

## 🛡️ Sécurité

### Backend
- **JWT** avec expiration (30 minutes)
- **bcrypt** pour le hachage des mots de passe
- **Validation stricte** des mots de passe admin
- **Middleware** de vérification des rôles
- **CORS** configuré
- **Headers de sécurité** dans nginx

### Frontend
- **Stockage sécurisé** des tokens JWT
- **Validation** des formulaires côté client
- **Protection des routes** selon les rôles
- **Gestion des erreurs** centralisée

## 🧪 Tests

### Backend
```bash
cd backend
python -m pytest
```

### Frontend
```bash
cd frontend
npm test
```

## 📝 API Endpoints

### Authentification
- `POST /auth/login` - Connexion utilisateur
- `GET /auth/me` - Informations utilisateur connecté

### Pages protégées
- `GET /api/home` - Page principale

### Gestion admin
- `POST /admin/change-admin-default-password` - Changer mot de passe admin
- `POST /admin/test-password-strength` - Tester force mot de passe

### Gestion des rôles
- `GET /admin/roles` - Lister tous les rôles
- `POST /admin/roles` - Créer un nouveau rôle
- `GET /admin/roles/{id}` - Récupérer un rôle
- `PUT /admin/roles/{id}` - Modifier un rôle
- `DELETE /admin/roles/{id}` - Supprimer un rôle

## 🚀 Déploiement

### Production
```bash
# Build et déploiement
docker-compose -f docker-compose.prod.yml up --build
```

### Développement
```bash
# Mode développement avec hot reload
docker-compose --profile dev up --build
```

## 📊 Monitoring

- **Health checks** : `/health` sur chaque service
- **Logs** : Accessibles via `docker-compose logs`
- **pgAdmin** : Interface web pour la base de données

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails. 