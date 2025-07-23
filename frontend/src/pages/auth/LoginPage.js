import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { Visibility, VisibilityOff, Email, Lock } from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../../hooks/useAuth';
import { useApi } from '../../hooks/useApi';
import { authService } from '../../services/authService';

const validationSchema = Yup.object({
  email: Yup.string()
    .email('Email invalide')
    .required('Email requis'),
  password: Yup.string()
    .min(5, 'Le mot de passe doit contenir au moins 5 caractères')
    .required('Mot de passe requis'),
});

const LoginPage = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [adminInfo, setAdminInfo] = useState(null);
  const { login } = useAuth();
  const { execute, loading, error } = useApi();
  const navigate = useNavigate();

  // Vérifier les informations de l'admin au chargement
  useEffect(() => {
    const checkAdminInfo = async () => {
      try {
        const info = await authService.getAdminInfo();
        setAdminInfo(info);
      } catch (error) {
        console.error('Erreur lors de la récupération des infos admin:', error);
      }
    };
    
    checkAdminInfo();
  }, []);

  const formik = useFormik({
    initialValues: {
      email: '',
      password: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        const response = await execute(
          () => login(values.email, values.password)
        );
        
        // Si c'est la première connexion admin, rediriger vers le changement de mot de passe
        if (response.first_admin_login) {
          navigate('/admin/password');
        } else {
          navigate('/home');
        }
      } catch (error) {
        // L'erreur est déjà gérée par useApi
      }
    },
  });

  const handleShowPassword = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Box component="form" onSubmit={formik.handleSubmit} sx={{ width: '100%' }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TextField
        fullWidth
        id="email"
        name="email"
        label="Email"
        value={formik.values.email}
        onChange={formik.handleChange}
        onBlur={formik.handleBlur}
        error={formik.touched.email && Boolean(formik.errors.email)}
        helperText={formik.touched.email && formik.errors.email}
        margin="normal"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Email />
            </InputAdornment>
          ),
        }}
      />

      <TextField
        fullWidth
        id="password"
        name="password"
        label="Mot de passe"
        type={showPassword ? 'text' : 'password'}
        value={formik.values.password}
        onChange={formik.handleChange}
        onBlur={formik.handleBlur}
        error={formik.touched.password && Boolean(formik.errors.password)}
        helperText={formik.touched.password && formik.errors.password}
        margin="normal"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Lock />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                aria-label="toggle password visibility"
                onClick={handleShowPassword}
                edge="end"
              >
                {showPassword ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </InputAdornment>
          ),
        }}
      />

      <Button
        type="submit"
        fullWidth
        variant="contained"
        size="large"
        disabled={loading}
        sx={{ mt: 3, mb: 2 }}
      >
        {loading ? 'Connexion...' : 'Se connecter'}
      </Button>

      <Typography variant="body2" color="text.secondary" textAlign="center">
        Utilisez vos identifiants pour accéder à Crystal Assur
      </Typography>
    </Box>
  );
};

export default LoginPage; 