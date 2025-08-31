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
  uploadDocument: async (fileOrFormData, clientId = null) => {
    let formData;
    
    if (fileOrFormData instanceof FormData) {
      // If FormData is passed directly, use it
      formData = fileOrFormData;
    } else {
      // If file object is passed, create FormData
      formData = new FormData();
      formData.append('file', fileOrFormData);
      if (clientId) {
        formData.append('client_id', clientId);
        formData.append('entity_type', 'CLIENT');
        formData.append('entity_id', clientId);
      }
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
  },

  // Get documents by entity type and ID
  getDocumentsByEntity: async (entityType, entityId) => {
    const response = await api.get(`/api/documents/entity/${entityType}/${entityId}`);
    return response.data;
  },

  // Link document to entity
  linkDocumentToEntity: async (documentId, entityType, entityId) => {
    const response = await api.put(`/api/documents/${documentId}/link`, {
      typeEntite: entityType,
      idEntite: entityId
    });
    return response.data;
  }
};
