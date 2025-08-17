import api from './api';

export const databaseExplorerService = {
  // Récupérer la liste de tous les tableaux
  async getAllTables() {
    try {
      const response = await api.get('/admin/tables');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Erreur lors de la récupération des tables');
    }
  },

  // Récupérer la structure d'une table
  async getTableStructure(tableName) {
    try {
      const response = await api.get(`/admin/tables/${tableName}/structure`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Erreur lors de la récupération de la structure');
    }
  },

  // Récupérer les données d'une table
  async getTableData(tableName, limit = 100, offset = 0) {
    try {
      const response = await api.get(`/admin/tables/${tableName}/data`, {
        params: { limit, offset }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Erreur lors de la récupération des données');
    }
  },

  // Récupérer le nombre de lignes d'une table
  async getTableRowCount(tableName) {
    try {
      const response = await api.get(`/admin/tables/${tableName}/count`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Erreur lors du comptage des lignes');
    }
  },

  // Créer une nouvelle ligne
  async createTableRow(tableName, rowData) {
    try {
      const response = await api.post(`/admin/tables/${tableName}/rows`, rowData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Erreur lors de la création de la ligne');
    }
  },

  // Mettre à jour une ligne existante
  async updateTableRow(tableName, rowId, rowData) {
    try {
      const response = await api.put(`/admin/tables/${tableName}/rows/${rowId}`, rowData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Erreur lors de la mise à jour de la ligne');
    }
  },

  // Supprimer une ligne
  async deleteTableRow(tableName, rowId) {
    try {
      const response = await api.delete(`/admin/tables/${tableName}/rows/${rowId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Erreur lors de la suppression de la ligne');
    }
  }
}; 