import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Alert,
  InputAdornment,
  IconButton,
  Grid,
  Chip,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Security as SecurityIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useApi } from '../../hooks/useApi';
import { useAuth } from '../../hooks/useAuth';
import { authService } from '../../services/authService';
import { JWT_STORAGE_KEY } from '../../config/api';

const validationSchema = Yup.object({
  currentPassword: Yup.string()
    .required('Mot de passe actuel requis'),
  newPassword: Yup.string()
    .min(12, 'Le mot de passe doit contenir au moins 12 caractères')
    .required('Nouveau mot de passe requis'),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('newPassword'), null], 'Les mots de passe doivent correspondre')
    .required('Confirmation du mot de passe requise'),
});

const AdminPasswordPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });
  const [passwordStrength, setPasswordStrength] = useState(null);
  const { execute, loading, error } = useApi();

  // Debug: vérifier l'état de l'authentification
  console.log('Utilisateur connecté:', user);
  console.log('Token dans localStorage:', localStorage.getItem(JWT_STORAGE_KEY));

  const formik = useFormik({
    initialValues: {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        await execute(
          () => authService.changeAdminPassword(
            values.currentPassword,
            values.newPassword,
            values.confirmPassword
          ),
          'Mot de passe admin changé avec succès !'
        );
        formik.resetForm();
        setPasswordStrength(null);
        
        // Rediriger vers le dashboard admin après le changement de mot de passe
        navigate('/admin');
      } catch (error) {
        // L'erreur est déjà gérée par useApi
      }
    },
  });

  const handlePasswordTest = async (password) => {
    if (password.length >= 12) {
      try {
        const result = await authService.testPasswordStrength(password);
        setPasswordStrength(result);
      } catch (error) {
        console.error('Erreur lors du test de force:', error);
      }
    } else {
      setPasswordStrength(null);
    }
  };

  const handleShowPassword = (field) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field],
    }));
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Changer le Mot de Passe Admin
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Modifiez le mot de passe administrateur avec des règles de sécurité renforcées.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={3}>
                <SecurityIcon sx={{ fontSize: 40, color: 'warning.main' }} />
                <Box>
                  <Typography variant="h6" component="h2">
                    Sécurité Renforcée
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Règles strictes pour le mot de passe admin
                  </Typography>
                </Box>
              </Box>

              <Box component="form" onSubmit={formik.handleSubmit}>
                <TextField
                  fullWidth
                  id="currentPassword"
                  name="currentPassword"
                  label="Mot de passe actuel"
                  type={showPasswords.current ? 'text' : 'password'}
                  value={formik.values.currentPassword}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  error={formik.touched.currentPassword && Boolean(formik.errors.currentPassword)}
                  helperText={formik.touched.currentPassword && formik.errors.currentPassword}
                  margin="normal"
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => handleShowPassword('current')}
                          edge="end"
                        >
                          {showPasswords.current ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />

                <TextField
                  fullWidth
                  id="newPassword"
                  name="newPassword"
                  label="Nouveau mot de passe"
                  type={showPasswords.new ? 'text' : 'password'}
                  value={formik.values.newPassword}
                  onChange={(e) => {
                    formik.handleChange(e);
                    handlePasswordTest(e.target.value);
                  }}
                  onBlur={formik.handleBlur}
                  error={formik.touched.newPassword && Boolean(formik.errors.newPassword)}
                  helperText={formik.touched.newPassword && formik.errors.newPassword}
                  margin="normal"
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => handleShowPassword('new')}
                          edge="end"
                        >
                          {showPasswords.new ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />

                <TextField
                  fullWidth
                  id="confirmPassword"
                  name="confirmPassword"
                  label="Confirmer le nouveau mot de passe"
                  type={showPasswords.confirm ? 'text' : 'password'}
                  value={formik.values.confirmPassword}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  error={formik.touched.confirmPassword && Boolean(formik.errors.confirmPassword)}
                  helperText={formik.touched.confirmPassword && formik.errors.confirmPassword}
                  margin="normal"
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => handleShowPassword('confirm')}
                          edge="end"
                        >
                          {showPasswords.confirm ? <VisibilityOff /> : <Visibility />}
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
                  sx={{ mt: 3 }}
                >
                  {loading ? 'Changement en cours...' : 'Changer le mot de passe'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Règles de Sécurité
              </Typography>
              
              <Box mt={2}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Le mot de passe doit contenir :
                </Typography>
                <Box component="ul" sx={{ pl: 2 }}>
                  <Typography component="li" variant="body2" color="text.secondary">
                    Au moins 12 caractères
                  </Typography>
                  <Typography component="li" variant="body2" color="text.secondary">
                    3 catégories minimum (majuscules, minuscules, chiffres, spéciaux)
                  </Typography>
                  <Typography component="li" variant="body2" color="text.secondary">
                    Pas plus de 2 caractères identiques consécutifs
                  </Typography>
                  <Typography component="li" variant="body2" color="text.secondary">
                    Pas de mots du dictionnaire commun
                  </Typography>
                  <Typography component="li" variant="body2" color="text.secondary">
                    Pas de séquences communes (123, abc, etc.)
                  </Typography>
                </Box>
              </Box>

              {passwordStrength && (
                <Box mt={3}>
                  <Typography variant="h6" gutterBottom>
                    Test de Force
                  </Typography>
                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    {passwordStrength.is_valid ? (
                      <CheckIcon color="success" />
                    ) : (
                      <ErrorIcon color="error" />
                    )}
                    <Chip
                      label={passwordStrength.is_valid ? 'Valide' : 'Invalide'}
                      color={passwordStrength.is_valid ? 'success' : 'error'}
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {passwordStrength.message}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdminPasswordPage; 