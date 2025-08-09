# Script de Création Automatique des Tables

## 📁 Fichiers

- **`create_tables.py`** - Script principal qui lit le CSV et crée les tables
- **`startup.sh`** - Script de démarrage qui exécute la création puis lance l'app
- **`DBTABLES.csv`** - Fichier CSV avec la définition des tables

## 🚀 Utilisation

### **Premier Lancement**
```bash
docker-compose up --build
```

Le script va automatiquement :
1. ✅ Attendre que PostgreSQL soit prêt
2. ✅ Lire le fichier `DBTABLES.csv`
3. ✅ Créer toutes les tables
4. ✅ Insérer des données initiales
5. ✅ Lancer l'application FastAPI

### **Lancements Suivants**
```bash
docker-compose up
```

Les tables existent déjà, l'application démarre directement.

## 📊 Fonctionnalités

### **✅ Générique**
- Lit n'importe quel fichier CSV avec la structure appropriée
- Gère tous les types de données PostgreSQL
- Crée les relations entre tables automatiquement

### **✅ Robuste**
- Attend que la base de données soit disponible
- Gère les erreurs et les retries
- Logs détaillés pour le débogage

### **✅ Simple**
- Un seul fichier Python
- Pas de dépendances complexes
- Facile à modifier et maintenir

## 📋 Structure du CSV

Le fichier `DBTABLES.csv` doit avoir ces colonnes :
- `Table` - Nom de la table
- `Colonne` - Nom de la colonne
- `Description` - Description de la colonne
- `Valeurs Possibles` - Valeurs possibles (optionnel)
- `Clé Primaire` - TRUE/FALSE
- `Clé Etrangère` - TRUE/FALSE
- `Format` - Type de données (VARCHAR(255), INTEGER, etc.)
- `Type Table` - MASTER/REFERENCE/TRANSACTIONAL

## 🔧 Personnalisation

### **Ajouter de Nouvelles Tables**
1. Ajouter les lignes dans `DBTABLES.csv`
2. Redémarrer avec `docker-compose up --build`

### **Modifier les Types de Données**
1. Modifier `convert_format_to_sql_type()` dans `create_tables.py`
2. Redémarrer avec `docker-compose up --build`

### **Changer les Données Initiales**
1. Modifier `insert_initial_data()` dans `create_tables.py`
2. Redémarrer avec `docker-compose up --build`

## 🐛 Dépannage

### **Erreur : Fichier CSV non trouvé**
```bash
# Vérifier que DBTABLES.csv est dans backend/scripts/
ls backend/scripts/DBTABLES.csv
```

### **Erreur : Base de données non disponible**
```bash
# Vérifier les logs
docker-compose logs backend
docker-compose logs db
```

### **Erreur : Tables non créées**
```bash
# Exécuter manuellement le script
docker exec -it auth-backend-1 python scripts/create_tables.py
```

## 📝 Exemple de Logs

```
🚀 Démarrage de l'application Crystal Assur...
================================================
📝 Initialisation de la base de données...
⏳ Attente de la base de données...
✅ Base de données disponible !
✅ Fichier CSV trouvé : /app/scripts/DBTABLES.csv
✅ 40 tables trouvées dans le CSV
📝 Création des tables...
✅ Création de la table : compagnies
✅ Création de la table : clients
...
✅ 40 tables créées avec succès !
📝 Insertion de données initiales...
✅ Données initiales insérées !
🎉 Initialisation terminée avec succès !
✅ Base de données prête pour l'application
✅ Base de données initialisée avec succès
🚀 Lancement de l'application FastAPI...
```

## 🎯 Avantages

- ✅ **Simple** : Un seul fichier Python
- ✅ **Générique** : Fonctionne avec n'importe quel CSV
- ✅ **Automatique** : Exécution au premier lancement
- ✅ **Robuste** : Gestion d'erreurs et retries
- ✅ **Maintenable** : Code clair et documenté 