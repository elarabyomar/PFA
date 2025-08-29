import api from './api';

export const adherentService = {
  // Flotte Auto
  async getFlotteAutoByClient(clientSocieteId) {
    try {
      const response = await api.get(`/adherents/flotte-auto/client/${clientSocieteId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching flotte auto:', error);
      throw error;
    }
  },

  async createFlotteAuto(flotteAutoData) {
    try {
      const response = await api.post('/adherents/flotte-auto', flotteAutoData);
      return response.data;
    } catch (error) {
      console.error('Error creating flotte auto:', error);
      throw error;
    }
  },

  async updateFlotteAuto(id, flotteAutoData) {
    try {
      const response = await api.put(`/adherents/flotte-auto/${id}`, flotteAutoData);
      return response.data;
    } catch (error) {
      console.error('Error updating flotte auto:', error);
      throw error;
    }
  },

  async deleteFlotteAuto(id) {
    try {
      const response = await api.delete(`/adherents/flotte-auto/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting flotte auto:', error);
      throw error;
    }
  },

  // Assure Sante
  async getAssureSanteByClient(clientSocieteId) {
    try {
      const response = await api.get(`/adherents/assure-sante/client/${clientSocieteId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching assure sante:', error);
      throw error;
    }
  },

  async createAssureSante(assureSanteData) {
    try {
      const response = await api.post('/adherents/assure-sante', assureSanteData);
      return response.data;
    } catch (error) {
      console.error('Error creating assure sante:', error);
      throw error;
    }
  },

  async updateAssureSante(id, assureSanteData) {
    try {
      const response = await api.put(`/adherents/assure-sante/${id}`, assureSanteData);
      return response.data;
    } catch (error) {
      console.error('Error updating assure sante:', error);
      throw error;
    }
  },

  async deleteAssureSante(id) {
    try {
      const response = await api.delete(`/adherents/assure-sante/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting assure sante:', error);
      throw error;
    }
  },

  // Reference data
  async getMarques() {
    try {
      const response = await api.get('/adherents/marques');
      return response.data;
    } catch (error) {
      console.error('Error fetching marques:', error);
      throw error;
    }
  },

  async getCarrosseries() {
    try {
      const response = await api.get('/adherents/carrosseries');
      return response.data;
    } catch (error) {
      console.error('Error fetching carrosseries:', error);
      throw error;
    }
  }
};
