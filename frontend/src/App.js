import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';

// Layouts
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';

// Pages
import LoginPage from './pages/auth/LoginPage';
import HomePage from './pages/main/HomePage';
import DashboardPage from './pages/admin/DashboardPage';
import RoleManagementPage from './pages/admin/RoleManagementPage';
import AdminPasswordPage from './pages/admin/AdminPasswordPage';

// Components
import ProtectedRoute from './components/auth/ProtectedRoute';
import AdminRoute from './components/auth/AdminRoute';
import LoadingSpinner from './components/common/LoadingSpinner';

// Hooks
import { useAuth } from './hooks/useAuth';

function App() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <Box sx={{ minHeight: '100vh' }}>
      <Routes>
        {/* Routes publiques */}
        <Route
          path="/login"
          element={
            isAuthenticated ? (
              <Navigate to="/home" replace />
            ) : (
              <AuthLayout>
                <LoginPage />
              </AuthLayout>
            )
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
          path="/admin/password"
          element={
            <AdminRoute>
              <MainLayout>
                <AdminPasswordPage />
              </MainLayout>
            </AdminRoute>
          }
        />

        {/* Route par défaut */}
        <Route
          path="/"
          element={<Navigate to={isAuthenticated ? '/home' : '/login'} replace />}
        />

        {/* Route 404 */}
        <Route
          path="*"
          element={<Navigate to={isAuthenticated ? '/home' : '/login'} replace />}
        />
      </Routes>
    </Box>
  );
}

export default App; 