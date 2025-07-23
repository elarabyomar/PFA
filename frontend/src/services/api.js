import axios from 'axios';
import { API_BASE_URL, JWT_STORAGE_KEY } from '../config/api';

// Créer une instance axios avec la configuration de base
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'authentification à chaque requête
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(JWT_STORAGE_KEY);
    console.log('Token trouvé:', token ? 'Oui' : 'Non');
    console.log('URL de la requête:', config.url);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('Headers Authorization ajouté');
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les réponses et les erreurs
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Si l'erreur est 401 (non autorisé), rediriger vers la page de connexion
    if (error.response?.status === 401) {
      localStorage.removeItem(JWT_STORAGE_KEY);
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api; 