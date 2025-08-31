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

  // Get all opportunities from all clients
  async getAllOpportunities() {
    try {
      const response = await api.get('/api/opportunities/');
      return response.data;
    } catch (error) {
      console.error('Error fetching all opportunities:', error);
      throw error;
    }
  },

  // Get opportunities with pagination, search, and filters
  async getOpportunities(params = {}) {
    try {
      const {
        skip = 0,
        limit = 50,
        search = '',
        etape = '',
        origine = '',
        transformed = ''
      } = params;
      
      const queryParams = new URLSearchParams();
      if (skip > 0) queryParams.append('skip', skip);
      if (limit !== 50) queryParams.append('limit', limit);
      if (search) queryParams.append('search', search);
      if (etape) queryParams.append('etape', etape);
      if (origine) queryParams.append('origine', origine);
      if (transformed !== '') queryParams.append('transformed', transformed);
      
      const response = await api.get(`/api/opportunities/?${queryParams.toString()}`);
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
