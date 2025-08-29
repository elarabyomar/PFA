import api from './api';

export const opportunityService = {
  // Get opportunities for a specific client
  async getOpportunitiesByClient(clientId) {
    try {
      const response = await api.get(`/api/opportunities/client/${clientId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching opportunities:', error);
      throw error;
    }
  },

  // Create a new opportunity
  async createOpportunity(opportunityData) {
    try {
      const response = await api.post('/api/opportunities/', opportunityData);
      return response.data;
    } catch (error) {
      console.error('Error creating opportunity:', error);
      throw error;
    }
  },

  // Update an opportunity
  async updateOpportunity(opportunityId, opportunityData) {
    try {
      const response = await api.put(`/api/opportunities/${opportunityId}`, opportunityData);
      return response.data;
    } catch (error) {
      console.error('Error updating opportunity:', error);
      throw error;
    }
  },

  // Delete an opportunity
  async deleteOpportunity(opportunityId) {
    try {
      const response = await api.delete(`/api/opportunities/${opportunityId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting opportunity:', error);
      throw error;
    }
  },

  // Get a single opportunity by ID
  async getOpportunity(opportunityId) {
    try {
      const response = await api.get(`/api/opportunities/${opportunityId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching opportunity:', error);
      throw error;
    }
  }
};
