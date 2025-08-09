# Utilise une image officielle de Python
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code de l'application
COPY . .

# Rendre le script de démarrage exécutable
RUN chmod +x scripts/startup.sh

# Utiliser le script de démarrage
CMD ["./scripts/startup.sh"]
