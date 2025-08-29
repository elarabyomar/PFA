import api from './api';

export const documentService = {
  // Create a client with documents and adherents
  createClientWithDocuments: async (clientData) => {
    const response = await api.post('/api/documents/clients', clientData);
    return response.data;
  },

  // Get documents for a specific client
  getClientDocuments: async (clientId) => {
    const response = await api.get(`/api/documents/clients/${clientId}/documents`);
    return response.data;
  },

  // Get adherents for a specific client
  getClientAdherents: async (clientId) => {
    const response = await api.get(`/api/documents/clients/${clientId}/adherents`);
    return response.data;
  },

  // Upload a document file
  uploadDocument: async (file, clientId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (clientId) {
      formData.append('client_id', clientId);
    }
    
    const response = await api.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Delete a document
  deleteDocument: async (documentId) => {
    const response = await api.delete(`/api/documents/${documentId}`);
    return response.data;
  }
};
