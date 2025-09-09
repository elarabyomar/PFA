# 🏢 PFA - Système de Gestion d'Assurance

## 📋 Description

Cette application est un système complet de gestion d'assurance développé dans le cadre d'un Projet de Fin d'Année (PFA). Elle permet la gestion des clients, des opportunités, des contrats et des utilisateurs avec une interface moderne et intuitive.

## 🚀 Installation et Configuration

### ⚠️ Important - Téléchargement du Projet

**Pour éviter tout problème de configuration, veuillez télécharger le projet au format ZIP depuis GitHub :**

1. Cliquez sur le bouton vert **"Code"** en haut à droite du dépôt
2. Sélectionnez **"Download ZIP"**
3. Extrayez le fichier ZIP dans votre dossier de travail

### 📁 Structure du Projet

```
PFA/
├── backend/          # API FastAPI (Python)
├── frontend/         # Interface React
├── docker-compose.yml
└── README.md
```

### 🛠️ Prérequis

- **Docker Desktop** : [Télécharger Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **IDE** : Visual Studio Code (recommandé) ou tout autre IDE de votre choix
- **Terminal** : PowerShell (Windows) ou Terminal (Mac/Linux)

### 🚀 Démarrage Rapide

1. **Ouvrir le projet dans votre IDE**
   - Ouvrez Visual Studio Code
   - File → Open Folder → Sélectionnez le dossier `PFA` (ou `PFA-master` si téléchargé en ZIP)

2. **Ouvrir Docker Desktop**
   - Lancez Docker Desktop sur votre machine
   - Attendez que l'icône Docker soit verte dans la barre des tâches

3. **Ouvrir le terminal dans le dossier racine**
   - Dans VS Code : `Ctrl + `` (backtick) ou Terminal → New Terminal
   - Naviguez vers le dossier racine : `cd PFA` (ou `cd PFA-master`)

4. **Lancer l'application**
   ```bash
   docker-compose up --build
   ```

5. **Accéder à l'application**
   - **Frontend** : http://localhost:3000
   - **Backend API** : http://localhost:8000
   - **Documentation API** : http://localhost:8000/docs
   - **pgAdmin** : http://localhost:5050

## 🐳 Commandes Docker Essentielles

### Commandes de Base
```bash
# Démarrer l'application
docker-compose up --build

# Démarrer en arrière-plan
docker-compose up -d --build

# Arrêter l'application
docker-compose down

# Voir les logs
docker-compose logs -f
```

### Commandes de Dépannage
```bash
# Supprimer les volumes (reset complet de la base de données)
docker-compose down -v

# Nettoyer les images et conteneurs inutilisés
docker system prune -a

# Reset complet (volumes + images + conteneurs)
docker-compose down -v
docker system prune -a
docker-compose up --build
```

## 🎯 Fonctionnalités Principales

### 👥 Page Clients
- **Ajouter un client** : Bouton vert "Ajouter un client"
- **Rechercher** : Barre de recherche globale
- **Filtrer** : Par type (Particulier/Société), statut, importance
- **Actions sur un client** :
  - Cliquer sur un client pour voir les détails
  - Modifier les informations
  - Supprimer un client
  - Voir les opportunités associées
  - Voir les contrats associés

### 💼 Page Opportunités
- **Gestion des opportunités** : Créer, modifier, supprimer
- **Suivi des prospects** : Statut, probabilité, budget
- **Filtrage avancé** : Par statut, montant, probabilité
- **Liaison avec les clients** : Chaque opportunité est liée à un client

### 📄 Page Contrats
- **Gestion des contrats** : Création, modification, suivi
- **Statuts des contrats** : En cours, signé, expiré
- **Documents associés** : Upload et gestion des documents
- **Renouvellements** : Suivi des échéances

### 🏠 Page d'Accueil
- **Tableau de bord** : Statistiques générales
- **Résumé des activités** : Dernières actions, alertes
- **Navigation rapide** : Accès direct aux fonctionnalités principales

### ⚙️ Administration (Accès Admin)
- **Gestion des utilisateurs** : Créer, modifier, supprimer des utilisateurs
- **Gestion des rôles** : Définir les permissions
- **Explorateur de base de données** : Visualiser et gérer les données
- **Statistiques avancées** : Rapports détaillés

## 🔐 Authentification

### 🚀 Accès Initial (Étape Essentielle)

Pour accéder à l'application, suivez ces étapes :

1. **Connexion Admin Initiale**
   - **Email** : `admin@gmail.com`
   - **Mot de passe** : `admin`
   - Vous serez automatiquement redirigé vers la page de changement de mot de passe

2. **Changement de Mot de Passe Admin**
   - Choisissez un nouveau mot de passe sécurisé
   - Une fois changé, vous aurez accès au profil administrateur

3. **Création d'Utilisateurs**
   - Depuis le profil admin, accédez à "Gestion des Utilisateurs"
   - Créez un nouvel utilisateur avec l'email de votre choix
   - L'utilisateur sera créé avec un mot de passe temporaire

4. **Connexion Utilisateur**
   - Déconnectez-vous du profil admin
   - Connectez-vous avec l'email créé
   - **Mot de passe** : Date de naissance au format `AAAAMMJJ` (ex: `20030705` pour le 5 juillet 2003)
   - Vous serez redirigé vers la page de changement de mot de passe

### Sécurité
- Authentification JWT
- Chiffrement des mots de passe
- Gestion des rôles et permissions
- Changement de mot de passe obligatoire au premier login
- Mot de passe temporaire basé sur la date de naissance

## 🗄️ Base de Données

### Accès pgAdmin
- **URL** : http://localhost:5050
- **Email** : admin@admin.com
- **Mot de passe** : admin

### Configuration de la Base
- **Type** : PostgreSQL 16
- **Nom** : test3
- **Utilisateur** : postgrestest
- **Mot de passe** : SYS
- **Port** : 5432

## 🛠️ Technologies Utilisées

### Backend
- **FastAPI** : Framework Python moderne et rapide
- **PostgreSQL** : Base de données relationnelle
- **SQLAlchemy** : ORM pour Python
- **JWT** : Authentification sécurisée
- **Pydantic** : Validation des données

### Frontend
- **React 18** : Bibliothèque JavaScript moderne
- **Material-UI** : Composants d'interface utilisateur
- **React Router** : Navigation côté client
- **Axios** : Client HTTP pour les API
- **Formik + Yup** : Gestion des formulaires et validation

### Infrastructure
- **Docker** : Conteneurisation
- **Docker Compose** : Orchestration des services
- **Nginx** : Serveur web pour le frontend
- **pgAdmin** : Interface d'administration PostgreSQL

## 📱 Interface Utilisateur

### Design
- **Material Design** : Interface moderne et intuitive
- **Responsive** : Compatible mobile, tablette et desktop
- **Thème sombre/clair** : Personnalisation de l'apparence
- **Navigation intuitive** : Menu latéral et breadcrumbs

### Fonctionnalités UX
- **Recherche en temps réel** : Filtrage instantané
- **Pagination infinie** : Chargement progressif des données
- **Notifications** : Feedback utilisateur en temps réel
- **Validation en temps réel** : Vérification des formulaires

## 🔧 Développement

### Structure du Code
```
backend/
├── app/              # Application principale
├── controller/       # Contrôleurs API
├── model/           # Modèles de données
├── service/         # Logique métier
├── repository/      # Accès aux données
└── security/        # Authentification

frontend/
├── src/
│   ├── components/  # Composants réutilisables
│   ├── pages/       # Pages de l'application
│   ├── services/    # Services API
│   ├── context/     # Gestion d'état global
│   └── utils/       # Utilitaires
```

### API Endpoints Principaux
- `GET /api/clients` - Liste des clients
- `POST /api/clients` - Créer un client
- `GET /api/opportunities` - Liste des opportunités
- `POST /api/opportunities` - Créer une opportunité
- `GET /api/contracts` - Liste des contrats
- `POST /api/contracts` - Créer un contrat

## 🐛 Dépannage

### Problèmes Courants

1. **Port déjà utilisé**
   ```bash
   # Arrêter tous les conteneurs
   docker-compose down
   # Relancer
   docker-compose up --build
   ```

2. **Base de données corrompue**
   ```bash
   # Reset complet
   docker-compose down -v
   docker system prune -a
   docker-compose up --build
   ```

3. **Problème de permissions Docker**
   - Vérifiez que Docker Desktop est en cours d'exécution
   - Redémarrez Docker Desktop si nécessaire

4. **Erreur de build**
   ```bash
   # Nettoyer le cache Docker
   docker builder prune -a
   docker-compose up --build
   ```

### Logs et Debugging
```bash
# Voir les logs de tous les services
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

## 📞 Support

Pour toute question ou problème :
1. Vérifiez d'abord la section Dépannage
2. Consultez les logs Docker
3. Vérifiez que tous les services sont en cours d'exécution
4. Redémarrez l'application si nécessaire

## 🎉 Félicitations !

Votre application de gestion d'assurance est maintenant prête à être utilisée ! Explorez les différentes fonctionnalités et n'hésitez pas à consulter la documentation API à l'adresse http://localhost:8000/docs pour plus de détails techniques.

---

**Développé avec ❤️ pour le PFA - Système de Gestion d'Assurance**
