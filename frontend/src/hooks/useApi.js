import { useState, useCallback } from 'react';


export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (apiCall, successMessage = null) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiCall();
      

      
      return result;
    } catch (err) {
      // Gérer les erreurs d'authentification de manière spécifique
      let errorMessage = 'Une erreur est survenue';
      
      if (err.response) {
        // Erreur de réponse du serveur
        const status = err.response.status;
        const detail = err.response.data?.detail || err.response.data?.message;
        
        if (status === 401) {
          errorMessage = detail || 'Email ou mot de passe incorrect';
        } else if (status === 400) {
          errorMessage = detail || 'Données invalides';
        } else if (status === 404) {
          errorMessage = detail || 'Ressource non trouvée';
        } else if (status === 500) {
          errorMessage = 'Erreur interne du serveur';
        } else {
          errorMessage = detail || err.message || 'Une erreur est survenue';
        }
      } else if (err.request) {
        // Erreur de réseau
        errorMessage = 'Erreur de connexion au serveur';
      } else {
        // Autre type d'erreur
        errorMessage = err.message || 'Une erreur est survenue';
      }
      
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const resetError = useCallback(() => {
    setError(null);
  }, []);

  return {
    loading,
    error,
    execute,
    resetError,
  };
}; 