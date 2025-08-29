import api from './api';

export const produitService = {
  // Get all products
  async getProduits() {
    try {
      const response = await api.get('/api/produits/');
      return response.data;
    } catch (error) {
      console.error('Error fetching produits:', error);
      throw error;
    }
  },

  // Get a single product by ID
  async getProduit(id) {
    try {
      const response = await api.get(`/api/produits/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching produit:', error);
      throw error;
    }
  }
};
