import axios from 'axios';
import jwtDecode from 'jwt-decode';
import api from './api';
import { JWT_STORAGE_KEY } from '../config/api';

// Les intercepteurs sont déjà configurés dans api.js

export const authService = {
  // Connexion utilisateur
  async login(email, password) {
    try {
      const response = await api.post('/auth/login', {
        email,
        password,
      });
      return response.data;
    } catch (error) {
      if (error.response?.status === 401) {
        throw new Error('Email ou mot de passe incorrect');
      }
      throw new Error(error.response?.data?.detail || 'Erreur de connexion');
    }
  },

  // Récupérer les informations de l'utilisateur connecté
  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      throw new Error('Erreur lors de la récupération des informations utilisateur');
    }
  },

  // Récupérer les informations de l'admin
  async getAdminInfo() {
    try {
      const response = await api.get('/auth/admin-info');
      return response.data;
    } catch (error) {
      throw new Error('Erreur lors de la récupération des informations admin');
    }
  },

  // Changer le mot de passe admin
  async changeAdminPassword(currentPassword, newPassword, confirmPassword) {
    try {
      console.log('Tentative de changement de mot de passe admin...');
      const response = await api.post('/admin/change-admin-default-password', {
        current_admin_password: currentPassword,
        new_admin_password: newPassword,
        confirm_new_password: confirmPassword,
      });
      console.log('Réponse du serveur:', response.data);
      return response.data;
    } catch (error) {
      console.error('Erreur détaillée:', error);
      console.error('Réponse d\'erreur:', error.response?.data);
      if (error.response?.status === 400) {
        throw new Error(error.response.data.detail);
      }
      throw new Error(error.response?.data?.detail || 'Erreur lors du changement de mot de passe');
    }
  },

  // Tester la force d'un mot de passe
  async testPasswordStrength(password) {
    try {
      const response = await api.post('/admin/test-password-strength', {
        password,
      });
      return response.data;
    } catch (error) {
      throw new Error('Erreur lors du test de force du mot de passe');
    }
  },

  // Vérifier si l'utilisateur est connecté
  isAuthenticated() {
    const token = localStorage.getItem(JWT_STORAGE_KEY);
    if (!token) return false;
    
    try {
      const decoded = jwtDecode(token);
      const currentTime = Date.now() / 1000;
      return decoded.exp > currentTime;
    } catch {
      return false;
    }
  },

  // Déconnexion
  logout() {
    localStorage.removeItem(JWT_STORAGE_KEY);
    localStorage.removeItem('user');
  },
}; 