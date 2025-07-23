# Stage de build
FROM node:18-alpine as build

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer toutes les dépendances (incluant devDependencies pour le build)
RUN npm install

# Copier le code source
COPY . .

# Build de l'application
RUN npm run build

# Stage de production
FROM nginx:alpine

# Copier les fichiers buildés
COPY --from=build /app/build /usr/share/nginx/html

# Copier la configuration nginx personnalisée
COPY nginx.conf /etc/nginx/nginx.conf

# Exposer le port 80
EXPOSE 80

# Démarrer nginx
CMD ["nginx", "-g", "daemon off;"] 