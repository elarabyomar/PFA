# Frontend React - Système d'Authentification

Ce projet est le frontend React pour le système d'authentification.

## 🚀 Technologies utilisées

- **React 18** - Framework JavaScript
- **React Router DOM** - Routing
- **Material-UI** - Composants UI
- **Axios** - Client HTTP
- **JWT Decode** - Gestion des tokens
- **Formik & Yup** - Gestion des formulaires et validation
- **React Toastify** - Notifications

## 📦 Installation

### Développement local

```bash
# Installer les dépendances
npm install

# Démarrer en mode développement
npm start
```

### Avec Docker

```bash
# Build et démarrer en production
docker-compose up --build

# Démarrer en mode développement
docker-compose --profile dev up --build
```

## 🔧 Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

### Proxy

Le proxy est configuré dans `package.json` pour rediriger les appels API vers le backend.

## 📁 Structure du projet

```
frontend/
├── public/                 # Fichiers publics
├── src/
│   ├── components/         # Composants réutilisables
│   ├── pages/             # Pages de l'application
│   ├── services/          # Services API
│   ├── hooks/             # Hooks personnalisés
│   ├── utils/             # Utilitaires
│   ├── context/           # Context React
│   └── styles/            # Styles CSS
├── Dockerfile             # Configuration Docker production
├── Dockerfile.dev         # Configuration Docker développement
├── docker-compose.yml     # Configuration Docker Compose
└── nginx.conf            # Configuration Nginx
```

## 🐳 Docker

### Production

```bash
docker-compose up --build
```

### Développement

```bash
docker-compose --profile dev up --build
```

## 🔗 Endpoints API

Le frontend communique avec les endpoints suivants du backend :

- `POST /auth/login` - Connexion
- `GET /auth/me` - Informations utilisateur
- `GET /api/home` - Page principale
- `POST /admin/change-admin-default-password` - Changer mot de passe admin
- `POST /admin/test-password-strength` - Tester force mot de passe
- `GET /admin/roles` - Lister les rôles
- `POST /admin/roles` - Créer un rôle
- `PUT /admin/roles/{id}` - Modifier un rôle
- `DELETE /admin/roles/{id}` - Supprimer un rôle

## 🚀 Scripts disponibles

- `npm start` - Démarrer en développement
- `npm run build` - Build de production
- `npm test` - Lancer les tests
- `npm run lint` - Linter le code
- `npm run format` - Formater le code

## 📝 Notes

- L'application utilise JWT pour l'authentification
- Les tokens sont stockés dans le localStorage
- Le routing est géré par React Router DOM
- L'interface utilisateur utilise Material-UI
- Les formulaires sont gérés avec Formik et Yup 