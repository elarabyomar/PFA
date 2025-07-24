import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { changePassword } from '../../services/authService';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
  Paper,
  Grid,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Container,
  AppBar,
  Toolbar,
  Avatar
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Security,
  CheckCircle,
  Cancel,
  Person
} from '@mui/icons-material';

const ChangePasswordPage = () => {
  const navigate = useNavigate();
  const { user, passwordChanged } = useAuth();
  const [formData, setFormData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [passwordValid, setPasswordValid] = useState(false);

  // Règles de sécurité
  const securityRules = [
    "Au moins 12 caractères",
    "3 catégories minimum (majuscules, minuscules, chiffres, spéciaux)",
    "Pas plus de 2 caractères identiques consécutifs",
    "Pas de mots du dictionnaire commun",
    "Pas de séquences communes (123, abc, etc.)"
  ];

  // Validation du mot de passe
  const validatePassword = (password) => {
    const checks = {
      length: password.length >= 12,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      numbers: /\d/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
      consecutive: !/(.)\1{2,}/.test(password),
      dictionary: !['password', 'admin', 'user', 'test', '123456'].some(word => 
        password.toLowerCase().includes(word)
      ),
      sequences: !/(123|abc|qwe|asd|zxc)/i.test(password)
    };

    const validChecks = Object.values(checks).filter(Boolean).length;
    const strength = Math.round((validChecks / Object.keys(checks).length) * 100);
    
    setPasswordStrength(strength);
    setPasswordValid(strength >= 80);
    
    return checks;
  };

  useEffect(() => {
    if (formData.newPassword) {
      validatePassword(formData.newPassword);
    }
  }, [formData.newPassword]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const togglePasswordVisibility = (field) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Validation côté client
      if (formData.newPassword !== formData.confirmPassword) {
        setError('Les mots de passe doivent correspondre');
        setLoading(false);
        return;
      }

      if (!passwordValid) {
        setError('Le mot de passe ne respecte pas les règles de sécurité');
        setLoading(false);
        return;
      }

      await changePassword({
        current_password: formData.currentPassword,
        new_password: formData.newPassword,
        confirm_password: formData.confirmPassword
      });

      setSuccess('Mot de passe changé avec succès !');
      
      // Mettre à jour le contexte
      passwordChanged();
      
      // Rediriger après 2 secondes
      setTimeout(() => {
        navigate('/home');
      }, 2000);

    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors du changement de mot de passe');
    } finally {
      setLoading(false);
    }
  };

  const getStrengthColor = () => {
    if (passwordStrength >= 80) return 'success';
    if (passwordStrength >= 60) return 'warning';
    if (passwordStrength >= 40) return 'error';
    return 'error';
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'grey.50' }}>
      {/* Header */}
      <AppBar position="static" sx={{ bgcolor: 'primary.main' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Crystal Assur
          </Typography>
          <Avatar sx={{ bgcolor: 'white', color: 'primary.main' }}>
            <Person />
          </Avatar>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Titre et description */}
        <Box textAlign="center" mb={4}>
          <Typography variant="h3" component="h1" gutterBottom>
            Changer le Mot de Passe Admin
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Modifiez le mot de passe admin par défaut pour des raisons de sécurité.
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {/* Formulaire */}
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 4 }}>
              <Box display="flex" alignItems="center" mb={3}>
                <Security color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography variant="h5" component="h2">
                    Sécurité du Compte
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Règles strictes pour le mot de passe admin
                  </Typography>
                </Box>
              </Box>

              <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
                {/* Mot de passe actuel */}
                <TextField
                  fullWidth
                  label="Mot de passe actuel"
                  type={showPasswords.current ? 'text' : 'password'}
                  name="currentPassword"
                  value={formData.currentPassword}
                  onChange={handleInputChange}
                  margin="normal"
                  required
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => togglePasswordVisibility('current')}
                          edge="end"
                        >
                          {showPasswords.current ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />

                {/* Nouveau mot de passe */}
                <TextField
                  fullWidth
                  label="Nouveau mot de passe"
                  type={showPasswords.new ? 'text' : 'password'}
                  name="newPassword"
                  value={formData.newPassword}
                  onChange={handleInputChange}
                  margin="normal"
                  required
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => togglePasswordVisibility('new')}
                          edge="end"
                        >
                          {showPasswords.new ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
                
                {/* Force du mot de passe */}
                {formData.newPassword && (
                  <Box sx={{ mt: 2, mb: 2 }}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2" color="text.secondary">
                        Force du mot de passe
                      </Typography>
                      <Typography variant="body2" fontWeight="medium">
                        {passwordStrength}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={passwordStrength}
                      color={getStrengthColor()}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                )}

                {/* Confirmer le nouveau mot de passe */}
                <TextField
                  fullWidth
                  label="Confirmer le nouveau mot de passe"
                  type={showPasswords.confirm ? 'text' : 'password'}
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  margin="normal"
                  required
                  error={formData.confirmPassword && formData.newPassword !== formData.confirmPassword}
                  helperText={
                    formData.confirmPassword && formData.newPassword !== formData.confirmPassword
                      ? 'Les mots de passe doivent correspondre'
                      : ''
                  }
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => togglePasswordVisibility('confirm')}
                          edge="end"
                        >
                          {showPasswords.confirm ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />

                {/* Messages d'erreur et de succès */}
                {error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {error}
                  </Alert>
                )}

                {success && (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    {success}
                  </Alert>
                )}

                {/* Bouton de soumission */}
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={loading || !passwordValid || formData.newPassword !== formData.confirmPassword}
                  sx={{ mt: 3 }}
                >
                  {loading ? 'Changement en cours...' : 'Changer le mot de passe'}
                </Button>
              </Box>
            </Paper>
          </Grid>

          {/* Règles de sécurité */}
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 4 }}>
              <Typography variant="h5" component="h2" gutterBottom>
                Règles de Sécurité
              </Typography>
              
              <List sx={{ mb: 4 }}>
                {securityRules.map((rule, index) => (
                  <ListItem key={index} sx={{ py: 0.5 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <Typography variant="body2" color="text.secondary">
                        •
                      </Typography>
                    </ListItemIcon>
                    <ListItemText primary={rule} />
                  </ListItem>
                ))}
              </List>

              {/* Test de force */}
              {formData.newPassword && (
                <Box sx={{ borderTop: 1, borderColor: 'divider', pt: 3 }}>
                  <Box display="flex" alignItems="center" mb={2}>
                    <CheckCircle color="success" sx={{ mr: 1 }} />
                    <Typography variant="body2" fontWeight="medium">
                      Test de Force
                    </Typography>
                  </Box>
                  
                  {passwordValid ? (
                    <Box display="flex" alignItems="center">
                      <Chip
                        label="Valide"
                        color="success"
                        size="small"
                        sx={{ mr: 2 }}
                      />
                      <Typography variant="body2" color="success.main">
                        Mot de passe conforme aux règles de sécurité
                      </Typography>
                    </Box>
                  ) : (
                    <Box display="flex" alignItems="center">
                      <Chip
                        label="Invalide"
                        color="error"
                        size="small"
                        sx={{ mr: 2 }}
                      />
                      <Typography variant="body2" color="error.main">
                        Le mot de passe ne respecte pas toutes les règles
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default ChangePasswordPage; 