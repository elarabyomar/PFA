import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Alert,
} from '@mui/material';
import { Delete as DeleteIcon, Warning as WarningIcon } from '@mui/icons-material';
import { useApi } from '../../hooks/useApi';
import { roleService } from '../../services/roleService';

const DeleteRoleDialog = ({ open, onClose, role, onRoleDeleted }) => {
  const { execute, loading, error } = useApi();

  const handleDelete = async () => {
    try {
      await execute(
        () => roleService.deleteRole(role.id),
        'Rôle supprimé avec succès !'
      );
      onRoleDeleted();
      onClose();
    } catch (error) {
      // L'erreur est déjà gérée par useApi
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <WarningIcon color="warning" />
          <Typography variant="h6">Confirmer la suppression</Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Box sx={{ mt: 2 }}>
          <Typography variant="body1" paragraph>
            Êtes-vous sûr de vouloir supprimer le rôle <strong>&quot;{role?.name}&quot;</strong> ?
          </Typography>
          
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2">
              Cette action est irréversible. Tous les utilisateurs ayant ce rôle devront être réassignés.
            </Typography>
          </Alert>
          
          {role?.description && (
            <Typography variant="body2" color="text.secondary">
              <strong>Description :</strong> {role.description}
            </Typography>
          )}
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Annuler
        </Button>
        <Button
          variant="contained"
          color="error"
          onClick={handleDelete}
          disabled={loading}
          startIcon={<DeleteIcon />}
        >
          {loading ? 'Suppression...' : 'Supprimer le rôle'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DeleteRoleDialog; 