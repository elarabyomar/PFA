import api from './api';

export const clientService = {
  // Get clients with pagination, search, and filtering
  getClients: async (params = {}) => {
    const {
      skip = 0,
      limit = 50,
      search = '',
      typeClient = '',
      importance = ''
    } = params;

    const queryParams = new URLSearchParams();
    if (skip > 0) queryParams.append('skip', skip);
    if (limit !== 50) queryParams.append('limit', limit);
    if (search) queryParams.append('search', search);
    if (typeClient) queryParams.append('typeClient', typeClient);
    if (importance) queryParams.append('importance', importance);

    const response = await api.get(`/api/clients?${queryParams.toString()}`);
    return response.data;
  },

  // Get a single client by ID
  getClient: async (clientId) => {
    const response = await api.get(`/api/clients/${clientId}`);
    return response.data;
  },

  // Create a new client
  createClient: async (clientData) => {
    const response = await api.post('/api/clients', clientData);
    return response.data;
  },

  // Update an existing client
  updateClient: async (clientId, clientData) => {
    const response = await api.put(`/api/clients/${clientId}`, clientData);
    return response.data;
  },

  // Delete a client
  deleteClient: async (clientId) => {
    const response = await api.delete(`/api/clients/${clientId}`);
    return response.data;
  },

  // Get client types
  getClientTypes: async () => {
    const response = await api.get('/api/clients/types/list');
    return response.data;
  },



  // Get client importance levels
  getClientImportanceLevels: async () => {
    const response = await api.get('/api/clients/importance/list');
    return response.data;
  },

  // Get client details
  getClientDetails: async (clientId) => {
    const response = await api.get(`/api/clients/${clientId}/details`);
    return response.data;
  }
};
