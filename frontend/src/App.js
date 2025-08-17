import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';

// Layouts
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';

// Pages
import LoginPage from './pages/auth/LoginPage';
import ChangePasswordPage from './pages/auth/ChangePasswordPage';
import HomePage from './pages/main/HomePage';
import DashboardPage from './pages/admin/DashboardPage';
import RoleManagementPage from './pages/admin/RoleManagementPage';
import UserManagementPage from './pages/admin/UserManagementPage';
import DatabaseExplorerPage from './pages/admin/DatabaseExplorerPage';

import ProtectedRoute from './components/auth/ProtectedRoute';
import AdminRoute from './components/auth/AdminRoute';
import PasswordChangeRoute from './components/auth/PasswordChangeRoute';
import LoadingSpinner from './components/common/LoadingSpinner';

// Hooks
import { useAuth } from './context/AuthContext';

function App() {
  const { isAuthenticated, isLoading, requiresPasswordChange } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  // Fonction pour déterminer la redirection par défaut
  const getDefaultRedirect = () => {
    if (!isAuthenticated) return '/login';
    
    // Si un changement de mot de passe est requis, rediriger vers cette page
    if (requiresPasswordChange) return '/change-password';
    
    // Redirection normale selon le rôle
    return '/home';
  };

  return (
    <Box sx={{ minHeight: '100vh' }}>
      <Routes>
        {/* Routes publiques */}
        <Route
          path="/login"
          element={
            isAuthenticated ? (
              <Navigate to={getDefaultRedirect()} replace />
            ) : (
              <AuthLayout>
                <LoginPage />
              </AuthLayout>
            )
          }
        />

        {/* Route de changement de mot de passe */}
        <Route
          path="/change-password"
          element={
            <PasswordChangeRoute>
              <ChangePasswordPage />
            </PasswordChangeRoute>
          }
        />

        {/* Routes protégées */}
        <Route
          path="/home"
          element={
            <ProtectedRoute>
              <MainLayout>
                <HomePage />
              </MainLayout>
            </ProtectedRoute>
          }
        />

        {/* Routes admin */}
        <Route
          path="/admin"
          element={
            <AdminRoute>
              <MainLayout>
                <DashboardPage />
              </MainLayout>
            </AdminRoute>
          }
        />

        <Route
          path="/admin/roles"
          element={
            <AdminRoute>
              <MainLayout>
                <RoleManagementPage />
              </MainLayout>
            </AdminRoute>
          }
        />

        <Route
          path="/admin/users"
          element={
            <AdminRoute>
              <MainLayout>
                <UserManagementPage />
              </MainLayout>
            </AdminRoute>
          }
        />

        <Route
          path="/admin/database"
          element={
            <AdminRoute>
              <MainLayout>
                <DatabaseExplorerPage />
              </MainLayout>
            </AdminRoute>
          }
        />

        {/* Route par défaut */}
        <Route
          path="/"
          element={<Navigate to={getDefaultRedirect()} replace />}
        />

        {/* Route 404 */}
        <Route
          path="*"
          element={<Navigate to={getDefaultRedirect()} replace />}
        />
      </Routes>
    </Box>
  );
}

export default App; 