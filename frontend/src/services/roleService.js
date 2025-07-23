import api from './api';
import { JWT_STORAGE_KEY } from '../config/api';

export const roleService = {
  // Récupérer tous les rôles
  async getAllRoles() {
    try {
      const response = await api.get('/admin/roles');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Erreur lors de la récupération des rôles');
    }
  },

  // Récupérer un rôle par ID
  async getRoleById(roleId) {
    try {
      const response = await api.get(`/admin/roles/${roleId}`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        throw new Error('Rôle non trouvé');
      }
      throw new Error(error.response?.data?.detail || 'Erreur lors de la récupération du rôle');
    }
  },

  // Créer un nouveau rôle
  async createRole(roleData) {
    try {
      const response = await api.post('/admin/roles', roleData);
      return response.data;
    } catch (error) {
      if (error.response?.status === 400) {
        throw new Error(error.response.data.detail);
      }
      throw new Error(error.response?.data?.detail || 'Erreur lors de la création du rôle');
    }
  },

  // Mettre à jour un rôle
  async updateRole(roleId, roleData) {
    try {
      const response = await api.put(`/admin/roles/${roleId}`, roleData);
      return response.data;
    } catch (error) {
      if (error.response?.status === 400) {
        throw new Error(error.response.data.detail);
      }
      if (error.response?.status === 404) {
        throw new Error('Rôle non trouvé');
      }
      throw new Error(error.response?.data?.detail || 'Erreur lors de la modification du rôle');
    }
  },

  // Supprimer un rôle
  async deleteRole(roleId) {
    try {
      const response = await api.delete(`/admin/roles/${roleId}`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 400) {
        throw new Error(error.response.data.detail);
      }
      if (error.response?.status === 404) {
        throw new Error('Rôle non trouvé');
      }
      throw new Error(error.response?.data?.detail || 'Erreur lors de la suppression du rôle');
    }
  },

  // Vérifier si un nom de rôle existe déjà
  async checkRoleNameExists(name, excludeId = null) {
    try {
      const roles = await this.getAllRoles();
      return roles.some(role => 
        role.name.toLowerCase() === name.toLowerCase() && 
        (!excludeId || role.id !== excludeId)
      );
    } catch (error) {
      console.error('Erreur lors de la vérification du nom de rôle:', error);
      return false;
    }
  },
}; 