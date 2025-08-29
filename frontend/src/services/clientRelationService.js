import api from './api';

export const clientRelationService = {
  // Get client relations for a specific client
  async getClientRelations(clientId) {
    try {
      const response = await api.get(`/api/client-relations/client/${clientId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching client relations:', error);
      throw error;
    }
  },

  // Create a new client relation
  async createClientRelation(relationData) {
    try {
      const response = await api.post('/api/client-relations/', relationData);
      return response.data;
    } catch (error) {
      console.error('Error creating client relation:', error);
      throw error;
    }
  },

  // Update a client relation
  async updateClientRelation(relationId, relationData) {
    try {
      const response = await api.put(`/api/client-relations/${relationId}`, relationData);
      return response.data;
    } catch (error) {
      console.error('Error updating client relation:', error);
      throw error;
    }
  },

  // Delete a client relation
  async deleteClientRelation(relationId) {
    try {
      const response = await api.delete(`/api/client-relations/${relationId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting client relation:', error);
      throw error;
    }
  },

  // Get a single client relation by ID
  async getClientRelation(relationId) {
    try {
      const response = await api.get(`/api/client-relations/${relationId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching client relation:', error);
      throw error;
    }
  },

  // Get all type relations
  async getTypeRelations() {
    try {
      const response = await api.get('/api/client-relations/types/list');
      return response.data;
    } catch (error) {
      console.error('Error fetching type relations:', error);
      throw error;
    }
  },

  // Create a new type relation
  async createTypeRelation(typeRelationData) {
    try {
      const response = await api.post('/api/client-relations/types/', typeRelationData);
      return response.data;
    } catch (error) {
      console.error('Error creating type relation:', error);
      throw error;
    }
  }
};
