import api from './api';

export const contractService = {
  // Get all contracts from all clients
  async getAllContracts() {
    try {
      const response = await api.get('/api/contracts/');
      return response.data;
    } catch (error) {
      console.error('Error fetching all contracts:', error);
      throw error;
    }
  },

  // Get contracts with pagination, search, and filters
  async getContracts(params = {}) {
    try {
      const {
        skip = 0,
        limit = 50,
        search = '',
        typeContrat = '',
        idTypeDuree = ''
      } = params;
      
      const queryParams = new URLSearchParams();
      if (skip > 0) queryParams.append('skip', skip);
      if (limit !== 50) queryParams.append('limit', limit);
      if (search) queryParams.append('search', search);
      if (typeContrat) queryParams.append('typeContrat', typeContrat);
      if (idTypeDuree) queryParams.append('idTypeDuree', idTypeDuree);
      
      const response = await api.get(`/api/contracts/?${queryParams.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching contracts:', error);
      throw error;
    }
  },

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
  async transformOpportunityToContract(opportunityId, contractData, documents = []) {
    try {
      // Create FormData to handle file uploads
      const formData = new FormData();
      
      // Add contract data
      Object.keys(contractData).forEach(key => {
        if (contractData[key] !== null && contractData[key] !== undefined && contractData[key] !== '') {
          formData.append(key, contractData[key]);
        }
      });
      
      // Add documents
      documents.forEach((doc, index) => {
        formData.append(`document_${index}`, doc);
      });
      
      const response = await api.post(`/api/contracts/transform-opportunity/${opportunityId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error transforming opportunity to contract:', error);
      throw error;
    }
  }
};
