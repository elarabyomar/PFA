// Configuration de l'API
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Timeouts
export const API_TIMEOUT = process.env.REACT_APP_API_TIMEOUT || 10000;

// Configuration JWT
export const JWT_STORAGE_KEY = process.env.REACT_APP_JWT_STORAGE_KEY || 'auth_token';

// Configuration des notifications
export const TOAST_POSITION = process.env.REACT_APP_TOAST_POSITION || 'top-right';
export const TOAST_AUTO_CLOSE = process.env.REACT_APP_TOAST_AUTO_CLOSE || 5000;

// Endpoints API
export const API_ENDPOINTS = {
  // Authentification
  LOGIN: '/auth/login',
  ME: '/auth/me',
  
  // Pages principales
  HOME: '/api/home',
  
  // Gestion admin

  
  // Gestion des rôles
  ROLES: '/admin/roles',
  ROLE_BY_ID: (id) => `/admin/roles/${id}`,
  
  // Gestion des utilisateurs
  USERS: '/admin/users',
  USER_BY_ID: (id) => `/admin/users/${id}`,

};

// Codes de statut HTTP
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
};

// Messages d'erreur
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Erreur de connexion réseau',
  UNAUTHORIZED: 'Session expirée. Veuillez vous reconnecter.',
  FORBIDDEN: 'Accès refusé. Permissions insuffisantes.',
  NOT_FOUND: 'Ressource non trouvée.',
  SERVER_ERROR: 'Erreur serveur. Veuillez réessayer plus tard.',
  VALIDATION_ERROR: 'Données invalides. Veuillez vérifier vos informations.',
}; 