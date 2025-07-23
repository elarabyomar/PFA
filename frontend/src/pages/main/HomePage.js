import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Avatar,
  Chip,
  Divider,
} from '@mui/material';
import {
  Person as PersonIcon,
  Email as EmailIcon,
  CalendarToday as CalendarIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';

const HomePage = () => {
  const { user } = useAuth();

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Bienvenue, {user?.prenom} !
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Vous êtes connecté à Crystal Assur. Voici vos informations de profil.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={3}>
                <Avatar
                  sx={{
                    width: 64,
                    height: 64,
                    bgcolor: 'primary.main',
                    fontSize: '1.5rem',
                  }}
                >
                  {user?.prenom?.charAt(0)}{user?.nom?.charAt(0)}
                </Avatar>
                <Box>
                  <Typography variant="h5" component="h2">
                    {user?.prenom} {user?.nom}
                  </Typography>
                  <Chip
                    label={user?.role}
                    color={user?.role === 'admin' ? 'error' : 'primary'}
                    icon={<SecurityIcon />}
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1} mb={2}>
                    <EmailIcon color="action" />
                    <Typography variant="body2" color="text.secondary">
                      Email
                    </Typography>
                  </Box>
                  <Typography variant="body1" fontWeight="medium">
                    {user?.email}
                  </Typography>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1} mb={2}>
                    <CalendarIcon color="action" />
                    <Typography variant="body2" color="text.secondary">
                      Date de naissance
                    </Typography>
                  </Box>
                  <Typography variant="body1" fontWeight="medium">
                    {formatDate(user?.date_naissance)}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Informations système
              </Typography>
              
              <Box mt={2}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Statut de connexion
                </Typography>
                <Chip
                  label="Connecté"
                  color="success"
                  size="small"
                />
              </Box>

              <Box mt={2}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Permissions
                </Typography>
                <Chip
                  label={user?.role === 'admin' ? 'Administrateur' : 'Utilisateur'}
                  color={user?.role === 'admin' ? 'error' : 'primary'}
                  size="small"
                />
              </Box>

              {user?.role === 'admin' && (
                <Box mt={2}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Accès admin
                  </Typography>
                  <Chip
                    label="Dashboard Admin"
                    color="warning"
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  <Chip
                    label="Gestion Rôles"
                    color="warning"
                    size="small"
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default HomePage; 