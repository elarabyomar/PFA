# 🎯 Libellés d'Affichage pour les Colonnes de Base de Données

## 📋 Vue d'ensemble

Ce système permet d'afficher des noms de colonnes compréhensibles dans votre application au lieu des noms techniques de la base de données.

## 🔧 Fonctionnalités

### 1. **Colonne "Libellé Affichage" dans DBTABLES.csv**
- Chaque colonne a maintenant un libellé d'affichage compréhensible
- Exemple : `idClient` → `Code Client`
- Exemple : `dateDebut` → `Date de Souscription`

### 2. **Commentaires dans la Base de Données**
- Les libellés sont stockés comme commentaires sur les colonnes
- Accessibles via `col_description()` en PostgreSQL

### 3. **Vues d'Affichage Automatiques**
- Création automatique de vues `{table}_display`
- Les colonnes sont renommées avec leurs libellés d'affichage

## 📊 Exemples de Libellés

### **Tables MASTER (Clients, Utilisateurs)**
```csv
clients,idClient,Code interne client,,FALSE,FALSE,VARCHAR(50),MASTER,Code Client
clients,typeClient,Type de client,PARTICULIER/SOCIETE,FALSE,FALSE,VARCHAR(20),MASTER,Type Client
clients,dateDebut,Date de souscription,YYYY-MM-DD,FALSE,FALSE,DATE,MASTER,Date Souscription
```

### **Tables REFERENCE (Produits, Garanties)**
```csv
produits,codeProduit,Code interne produit,,FALSE,FALSE,VARCHAR(50),REFERENCE,Code Produit
produits,libelle,Nom du produit,,FALSE,FALSE,VARCHAR(255),REFERENCE,Nom Produit
```

### **Tables TRANSACTIONAL (Devis, Production)**
```csv
devis,montantEstime,Montant estimé,,FALSE,FALSE,"DECIMAL(12,2)",TRANSACTIONAL,Montant Estimé
production,numPolice,Numéro de police unique,,FALSE,FALSE,VARCHAR(100),TRANSACTIONAL,Numéro Police
```

## 🚀 Utilisation

### **1. Dans vos Requêtes SQL**

#### **Utiliser la table normale avec commentaires :**
```sql
-- Récupérer les libellés des colonnes
SELECT column_name, col_description((table_name)::regclass, ordinal_position) as libelle
FROM information_schema.columns 
WHERE table_name = 'clients' 
AND table_schema = 'public'
ORDER BY ordinal_position;
```

#### **Utiliser les vues d'affichage :**
```sql
-- Les colonnes sont déjà renommées avec leurs libellés
SELECT * FROM clients_display;

-- Résultat : Code Client, Type Client, Date Souscription, etc.
```

### **2. Dans votre Application Frontend**

#### **Récupérer les libellés pour les en-têtes de tableaux :**
```javascript
// API pour récupérer la structure d'une table avec libellés
const getTableStructure = async (tableName) => {
  const response = await fetch(`/api/database/table-structure/${tableName}`);
  const columns = await response.json();
  
  // Utiliser les libellés pour les en-têtes
  return columns.map(col => ({
    field: col.column_name,
    headerName: col.comment || col.column_name,
    type: col.data_type
  }));
};
```

#### **Afficher les données avec les vues d'affichage :**
```javascript
// Utiliser la vue d'affichage pour avoir des noms de colonnes clairs
const getTableData = async (tableName) => {
  const response = await fetch(`/api/database/table-data/${tableName}_display`);
  return await response.json();
};
```

### **3. Dans vos Modèles Pydantic**

```python
from pydantic import BaseModel, Field

class ClientDisplay(BaseModel):
    code_client: str = Field(..., alias="Code Client", description="Code Client")
    type_client: str = Field(..., alias="Type Client", description="Type Client")
    date_souscription: str = Field(..., alias="Date Souscription", description="Date Souscription")
    
    class Config:
        allow_population_by_field_name = True
```

## 🛠️ Maintenance

### **Ajouter un Nouveau Libellé**
1. Ouvrir `DBTABLES.csv`
2. Ajouter le libellé dans la colonne `Libellé Affichage`
3. Exécuter `create_tables.py` pour mettre à jour la base

### **Modifier un Libellé Existant**
1. Modifier la valeur dans `DBTABLES.csv`
2. Exécuter `create_tables.py` pour recréer les vues

### **Supprimer un Libellé**
1. Vider la cellule dans `DBTABLES.csv`
2. Le système utilisera le nom de la colonne par défaut

## 🔍 Scripts Disponibles

### **`add_display_labels.py`**
- Ajoute automatiquement les libellés manquants
- Génère des libellés par défaut basés sur les descriptions

### **`test_display_labels.py`**
- Vérifie que les libellés fonctionnent correctement
- Teste la base de données et les vues

### **`create_tables.py`**
- Crée les tables avec commentaires
- Génère automatiquement les vues d'affichage

## 📝 Bonnes Pratiques

### **1. Noms de Libellés**
- ✅ **Clairs et concis** : `Code Client` au lieu de `Identifiant unique du client`
- ✅ **En français** : Respecter la langue de l'application
- ✅ **Cohérents** : Même style pour toutes les tables

### **2. Gestion des Caractères Spéciaux**
- ✅ **Espaces** : `Date de Création`
- ✅ **Accents** : `Numéro de Police`
- ⚠️ **Caractères spéciaux** : Éviter `()`, `-`, etc. dans les noms de vues

### **3. Longueur des Libellés**
- ✅ **Court** : `Code` au lieu de `Code d'identification unique`
- ✅ **Descriptif** : `Date de Souscription` au lieu de `Date`

## 🎨 Exemples d'Interface Utilisateur

### **Avant (noms techniques) :**
```
| idClient | typeClient | dateDebut | montantEstime |
|----------|------------|-----------|----------------|
| CL001    | SOCIETE    | 2024-01-15| 1500.00       |
```

### **Après (libellés d'affichage) :**
```
| Code Client | Type Client | Date Souscription | Montant Estimé |
|-------------|-------------|-------------------|-----------------|
| CL001       | SOCIETE     | 2024-01-15        | 1500.00         |
```

## 🔗 Intégration avec l'API

### **Endpoint pour récupérer la structure d'une table :**
```python
@router.get("/table-structure/{table_name}")
async def get_table_structure(table_name: str, session: AsyncSession = Depends(get_session)):
    """Récupère la structure d'une table avec ses libellés d'affichage"""
    
    query = text("""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            col_description((table_name)::regclass, ordinal_position) as comment
        FROM information_schema.columns 
        WHERE table_name = :table_name 
        AND table_schema = 'public'
        ORDER BY ordinal_position
    """)
    
    result = await session.execute(query, {"table_name": table_name})
    columns = result.fetchall()
    
    return [
        {
            "column_name": col.column_name,
            "data_type": col.data_type,
            "is_nullable": col.is_nullable,
            "display_name": col.comment or col.column_name
        }
        for col in columns
    ]
```

## 🎯 Avantages

1. **Interface utilisateur claire** : Noms de colonnes compréhensibles
2. **Maintenance facile** : Centralisé dans le fichier CSV
3. **Flexibilité** : Modification sans toucher au code
4. **Cohérence** : Même style pour toutes les tables
5. **Multilingue** : Possibilité d'ajouter des colonnes pour différentes langues

## 🚨 Limitations

1. **PostgreSQL uniquement** : Utilise `col_description()` spécifique à PostgreSQL
2. **Noms de vues** : Les caractères spéciaux sont remplacés dans les noms de vues
3. **Performance** : Les vues ajoutent une couche supplémentaire

## 🔮 Évolutions Futures

1. **Support multilingue** : Colonnes pour différentes langues
2. **Validation des libellés** : Vérification de la cohérence
3. **Interface d'administration** : Gestion des libellés via l'interface web
4. **Export/Import** : Synchronisation avec d'autres environnements
