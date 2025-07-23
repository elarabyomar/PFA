import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useApi } from '../../hooks/useApi';
import { roleService } from '../../services/roleService';
import CreateRoleModal from '../../components/admin/CreateRoleModal';
import EditRoleModal from '../../components/admin/EditRoleModal';
import DeleteRoleDialog from '../../components/admin/DeleteRoleDialog';

const RoleManagementPage = () => {
  const [roles, setRoles] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState(null);
  const { execute, loading, error } = useApi();

  // Charger les rôles au montage du composant
  useEffect(() => {
    loadRoles();
  }, []);

  const loadRoles = async () => {
    try {
      const rolesData = await execute(() => roleService.getAllRoles());
      setRoles(rolesData);
    } catch (error) {
      // L'erreur est déjà gérée par useApi
    }
  };

  const handleCreateRole = () => {
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
  };

  const handleRoleCreated = () => {
    // Recharger la liste des rôles après création
    loadRoles();
  };

  const handleEditRole = (role) => {
    setSelectedRole(role);
    setEditModalOpen(true);
  };

  const handleCloseEditModal = () => {
    setEditModalOpen(false);
    setSelectedRole(null);
  };

  const handleRoleUpdated = () => {
    loadRoles();
  };

  const handleDeleteRole = (role) => {
    setSelectedRole(role);
    setDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setSelectedRole(null);
  };

  const handleRoleDeleted = () => {
    loadRoles();
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('fr-FR');
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Gestion des Rôles
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          color="primary"
          onClick={handleCreateRole}
        >
          Nouveau Rôle
        </Button>
      </Box>

      <Typography variant="body1" color="text.secondary" paragraph>
        Gérez les rôles utilisateurs et leurs permissions dans Crystal Assur.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {roles.map((role) => (
            <Grid item xs={12} md={6} key={role.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6" component="h2">
                      {role.name}
                    </Typography>
                    <Chip 
                      label={role.name === 'admin' || role.name === 'user' ? 'Système' : 'Personnalisé'} 
                      color={role.name === 'admin' || role.name === 'user' ? 'error' : 'primary'} 
                      size="small" 
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {role.description || 'Aucune description'}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block" mb={2}>
                    Créé le {formatDate(role.created_at)}
                  </Typography>
                  <Box display="flex" gap={1}>
                    <Button 
                      size="small" 
                      variant="outlined"
                      onClick={() => handleEditRole(role)}
                    >
                      Modifier
                    </Button>
                    <Button 
                      size="small" 
                      variant="outlined" 
                      color="error" 
                      disabled={role.name === 'admin' || role.name === 'user'}
                      onClick={() => handleDeleteRole(role)}
                    >
                      Supprimer
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Box mt={4}>
        <Typography variant="h6" gutterBottom>
          Informations
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • Les rôles système (admin, user) ne peuvent pas être supprimés
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • Vous pouvez créer de nouveaux rôles personnalisés
        </Typography>
        <Typography variant="body2" color="text.secondary">
          • Chaque rôle peut avoir des permissions spécifiques
        </Typography>
      </Box>

      <CreateRoleModal
        open={modalOpen}
        onClose={handleCloseModal}
        onRoleCreated={handleRoleCreated}
      />

      <EditRoleModal
        open={editModalOpen}
        onClose={handleCloseEditModal}
        role={selectedRole}
        onRoleUpdated={handleRoleUpdated}
      />

      <DeleteRoleDialog
        open={deleteDialogOpen}
        onClose={handleCloseDeleteDialog}
        role={selectedRole}
        onRoleDeleted={handleRoleDeleted}
      />
    </Box>
  );
};

export default RoleManagementPage; 