# Crystal Assur - Système d'Authentification

Un système d'authentification complet avec gestion des utilisateurs et des rôles, développé avec FastAPI (backend) et React (frontend).

## 🏗️ Architecture

```
auth/
├── backend/                 # API FastAPI
│   ├── app/
│   │   └── main.py         # Point d'entrée de l'API
│   ├── controller/          # Contrôleurs API
│   ├── service/            # Logique métier
│   ├── model/              # Modèles de données
│   ├── repository/         # Accès aux données
│   ├── dto/               # Objets de transfert
│   ├── security/          # Middleware d'authentification
│   └── config/            # Configuration
├── frontend/               # Application React
│   ├── src/
│   │   ├── components/     # Composants réutilisables
│   │   ├── pages/         # Pages de l'application
│   │   ├── services/      # Services API
│   │   ├── context/       # Context React
│   │   ├── hooks/         # Hooks personnalisés
│   │   └── utils/         # Utilitaires
│   └── public/            # Fichiers statiques
└── docker-compose.yml      # Configuration Docker
```

## 🚀 Fonctionnalités

### Authentification
- ✅ Connexion avec email/mot de passe
- ✅ JWT tokens avec expiration
- ✅ Gestion des sessions
- ✅ Protection des routes

### Gestion des Utilisateurs
- ✅ CRUD complet des utilisateurs
- ✅ Génération automatique des mots de passe (format YYYYMMDD)
- ✅ Réinitialisation des mots de passe
- ✅ Gestion des rôles

### Gestion des Rôles
- ✅ Création/modification/suppression des rôles
- ✅ Rôles système (admin, user) protégés
- ✅ Permissions granulaires

### Interface Admin
- ✅ Dashboard administrateur
- ✅ Gestion des utilisateurs
- ✅ Gestion des rôles
- ✅ Changement du mot de passe admin par défaut

## 🛠️ Technologies

### Backend
- **FastAPI** - Framework web moderne et rapide
- **SQLAlchemy** - ORM pour PostgreSQL
- **PostgreSQL** - Base de données
- **JWT** - Authentification par tokens
- **Passlib** - Hachage des mots de passe
- **Alembic** - Migrations de base de données

### Frontend
- **React 18** - Interface utilisateur
- **Material-UI** - Composants UI
- **React Router** - Navigation
- **Axios** - Client HTTP
- **Formik + Yup** - Gestion des formulaires
- **React Toastify** - Notifications

### Infrastructure
- **Docker** - Conteneurisation
- **Docker Compose** - Orchestration
- **Nginx** - Serveur web et proxy
- **pgAdmin** - Interface de gestion PostgreSQL

## 📋 Prérequis

- Docker et Docker Compose
- Node.js 18+ (pour le développement)
- Python 3.11+ (pour le développement)

## 🚀 Installation et Démarrage

### 1. Cloner le projet
```bash
git clone <repository-url>
cd auth
```

### 2. Démarrer avec Docker Compose
```bash
docker-compose up -d
```

### 3. Accéder aux services
- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **pgAdmin** : http://localhost:5050

## 🔐 Comptes par défaut

### Administrateur
- **Email** : admin@gmail.com
- **Mot de passe** : admin
- **Rôle** : admin

### Utilisateur de test
- **Email** : user@gmail.com
- **Mot de passe** : 20031125 (format YYYYMMDD)
- **Rôle** : user

## 📚 API Endpoints

### Authentification
- `POST /auth/login` - Connexion utilisateur
- `GET /auth/me` - Informations utilisateur connecté


### Gestion des utilisateurs
- `GET /admin/users` - Liste des utilisateurs
- `POST /admin/users` - Créer un utilisateur
- `PUT /admin/users/{id}` - Modifier un utilisateur
- `DELETE /admin/users/{id}` - Supprimer un utilisateur


### Gestion des rôles
- `GET /admin/roles` - Liste des rôles
- `POST /admin/roles` - Créer un rôle
- `PUT /admin/roles/{id}` - Modifier un rôle
- `DELETE /admin/roles/{id}` - Supprimer un rôle

### Administration


## 🔧 Configuration

### Variables d'environnement

#### Backend
```env
DATABASE_URL=postgresql+asyncpg://postgrestest:SYS@db:5432/test3
JWT_SECRET=your_super_secret_key_change_in_production
```

#### Frontend
```env
REACT_APP_API_URL=http://localhost:8000
NODE_ENV=production
```

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

## 📦 Déploiement

### Production
```bash
# Build et démarrage en production
docker-compose -f docker-compose.prod.yml up -d
```

### Développement
```bash
# Démarrage avec hot reload
docker-compose up -d
```

## 🔒 Sécurité

### JWT
- Tokens avec expiration (30 minutes)
- Refresh automatique
- Gestion des sessions

### CORS
- Configuration pour le développement
- À configurer pour la production

## 🐛 Dépannage

### Problèmes courants

1. **Base de données non accessible**
   ```bash
   docker-compose logs db
   ```

2. **API non accessible**
   ```bash
   docker-compose logs backend
   ```

3. **Frontend non accessible**
   ```bash
   docker-compose logs frontend
   ```

### Logs
```bash
# Tous les services
docker-compose logs

# Service spécifique
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

## 📝 Changelog

### v1.0.0
- ✅ Système d'authentification complet
- ✅ Gestion des utilisateurs et rôles
- ✅ Interface administrateur
- ✅ Configuration Docker
- ✅ Documentation API

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Contacter l'équipe de développement

---

**Développé avec ❤️ pour Crystal Assur** 