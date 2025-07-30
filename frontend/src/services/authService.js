import api from './api';

export const login = async (credentials) => {
  const response = await api.post('/auth/login', credentials);
  return response.data;
};

export const logout = async () => {
  // Optionnel : appeler un endpoint de déconnexion côté serveur
  // const response = await api.post('/auth/logout');
  return { success: true };
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

export const changePassword = async (passwordData) => {
  const response = await api.post('/auth/change-password', passwordData);
  return response.data;
};

 