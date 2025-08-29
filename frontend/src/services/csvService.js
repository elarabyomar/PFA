import api from './api';

export const csvService = {
  // Flotte Auto CSV data
  async getFlotteAutoCSV() {
    try {
      const response = await api.get('/csv/flotte-auto');
      return response.data;
    } catch (error) {
      console.error('Error fetching flotte auto CSV data:', error);
      throw error;
    }
  },

  async getFlotteAutoByClientCSV(clientSocieteId) {
    try {
      const response = await api.get(`/csv/flotte-auto/client/${clientSocieteId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching flotte auto CSV data by client:', error);
      throw error;
    }
  },

  // Assure Sante CSV data
  async getAssureSanteCSV() {
    try {
      const response = await api.get('/csv/assure-sante');
      return response.data;
    } catch (error) {
      console.error('Error fetching assure sante CSV data:', error);
      throw error;
    }
  },

  async getAssureSanteByClientCSV(clientSocieteId) {
    try {
      const response = await api.get(`/csv/assure-sante/client/${clientSocieteId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching assure sante CSV data by client:', error);
      throw error;
    }
  }
};
