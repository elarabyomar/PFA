import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Divider,
} from '@mui/material';
import {
  AdminPanelSettings as AdminIcon,
  Security as SecurityIcon,
  People as PeopleIcon,
  Settings as SettingsIcon,
  Group as GroupIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const DashboardPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const adminFeatures = [
    {
      title: 'Gestion des Utilisateurs',
      description: 'Créer, modifier et gérer les utilisateurs du système',
      icon: <GroupIcon sx={{ fontSize: 40 }} />,
      color: 'success',
      path: '/admin/users',
    },
    {
      title: 'Gestion des Rôles',
      description: 'Créer, modifier et supprimer les rôles utilisateurs',
      icon: <SecurityIcon sx={{ fontSize: 40 }} />,
      color: 'primary',
      path: '/admin/roles',
    },

  ];

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard Administrateur
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Bienvenue dans l&apos;interface d&apos;administration. Gérez les utilisateurs, les rôles et les paramètres de Crystal Assur.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <AdminIcon sx={{ fontSize: 40, color: 'primary.main' }} />
                <Box>
                  <Typography variant="h6" component="h2">
                    Administrateur
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {user?.prenom} {user?.nom}
                  </Typography>
                </Box>
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Permissions
                </Typography>
                <Chip
                  label="Super Admin"
                  color="error"
                  size="small"
                  sx={{ mr: 1 }}
                />
                <Chip
                  label="Gestion Utilisateurs"
                  color="success"
                  size="small"
                  sx={{ mr: 1 }}
                />
                <Chip
                  label="Gestion Rôles"
                  color="primary"
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {adminFeatures.map((feature, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <Box sx={{ color: `${feature.color}.main` }}>
                    {feature.icon}
                  </Box>
                  <Typography variant="h6" component="h2">
                    {feature.title}
                  </Typography>
                </Box>
                
                <Typography variant="body2" color="text.secondary" paragraph>
                  {feature.description}
                </Typography>
              </CardContent>
              
              <CardActions>
                <Button
                  size="small"
                  color={feature.color}
                  onClick={() => navigate(feature.path)}
                >
                  Accéder
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box mt={4}>
        <Typography variant="h5" gutterBottom>
          Informations système
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="primary">
                  Utilisateurs
                </Typography>
                <Typography variant="h4" component="div">
                  1
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Utilisateur actif
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="secondary">
                  Rôles
                </Typography>
                <Typography variant="h4" component="div">
                  2
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Rôles configurés
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="success">
                  Sécurité
                </Typography>
                <Typography variant="h4" component="div">
                  ✓
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Système sécurisé
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="info">
                  Statut
                </Typography>
                <Typography variant="h4" component="div">
                  🟢
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  En ligne
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default DashboardPage; 