import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../common/LoadingSpinner';

const PasswordChangeRoute = ({ children }) => {
  const { isAuthenticated, isLoading, requiresPasswordChange } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  // Si l'utilisateur n'est pas connecté, rediriger vers la page de connexion
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Si l'utilisateur n'a pas besoin de changer son mot de passe, rediriger vers la page d'accueil
  if (!requiresPasswordChange) {
    return <Navigate to="/home" replace />;
  }

  // Sinon, afficher la page de changement de mot de passe
  return children;
};

export default PasswordChangeRoute; 