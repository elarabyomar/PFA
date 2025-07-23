import { useState, useCallback } from 'react';
import { toast } from 'react-toastify';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (apiCall, successMessage = null) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiCall();
      
      if (successMessage) {
        toast.success(successMessage);
      }
      
      return result;
    } catch (err) {
      const errorMessage = err.message || 'Une erreur est survenue';
      setError(errorMessage);
      toast.error(errorMessage);
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