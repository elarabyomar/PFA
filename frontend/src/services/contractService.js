import api from './api';

export const contractService = {
  // Get contracts for a specific client
  async getContractsByClient(clientId) {
    try {
      const response = await api.get(`/api/contracts/client/${clientId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching contracts:', error);
      throw error;
    }
  },

  // Create a new contract
  async createContract(contractData) {
    try {
      const response = await api.post('/api/contracts/', contractData);
      return response.data;
    } catch (error) {
      console.error('Error creating contract:', error);
      throw error;
    }
  },

  // Update a contract
  async updateContract(contractId, contractData) {
    try {
      const response = await api.put(`/api/contracts/${contractId}`, contractData);
      return response.data;
    } catch (error) {
      console.error('Error updating contract:', error);
      throw error;
    }
  },

  // Delete a contract
  async deleteContract(contractId) {
    try {
      const response = await api.delete(`/api/contracts/${contractId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting contract:', error);
      throw error;
    }
  },

  // Get a single contract by ID
  async getContract(contractId) {
    try {
      const response = await api.get(`/api/contracts/${contractId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching contract:', error);
      throw error;
    }
  },

  // Transform opportunity to contract
  async transformOpportunityToContract(opportunityId, contractData) {
    try {
      const response = await api.post(`/api/contracts/transform-opportunity/${opportunityId}`, contractData);
      return response.data;
    } catch (error) {
      console.error('Error transforming opportunity to contract:', error);
      throw error;
    }
  }
};
