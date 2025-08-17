#!/bin/bash

echo "🚀 Démarrage de l'application Insurforce..."
echo "================================================"

# Attendre que la base de données soit prête
echo "⏳ Attente de la base de données..."
sleep 10

# Exécuter le script de création des tables
echo "📝 Initialisation de la base de données..."
python scripts/create_tables.py

if [ $? -eq 0 ]; then
    echo "✅ Base de données initialisée avec succès"
    echo "🚀 Lancement de l'application FastAPI..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "❌ Erreur lors de l'initialisation de la base de données"
    exit 1
fi 