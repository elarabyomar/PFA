/* eslint-disable react/no-unescaped-entities */
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
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  OutlinedInput,
  Checkbox,
  ListItemText,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Lock as LockIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import { useApi } from '../../hooks/useApi';
import * as userService from '../../services/userService';
import { roleService } from '../../services/roleService';
import { formatDate } from '../../utils/validation';
import { useFormik } from 'formik';
import * as Yup from 'yup';

const validationSchema = Yup.object({
  nom: Yup.string()
    .min(2, 'Le nom doit contenir au moins 2 caractères')
    .max(50, 'Le nom ne peut pas dépasser 50 caractères')
    .required('Nom requis'),
  prenom: Yup.string()
    .min(2, 'Le prénom doit contenir au moins 2 caractères')
    .max(50, 'Le prénom ne peut pas dépasser 50 caractères')
    .required('Prénom requis'),
  email: Yup.string()
    .email('Email invalide')
    .required('Email requis'),
  date_naissance: Yup.date()
    .required('Date de naissance requise')
    .max(new Date(), 'La date de naissance ne peut pas être dans le futur'),
  roles: Yup.array()
    .min(1, 'Au moins un rôle doit être sélectionné')
    .required('Rôles requis'),
});

const UserManagementPage = () => {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [resetPasswordDialogOpen, setResetPasswordDialogOpen] = useState(false);

  const [selectedUser, setSelectedUser] = useState(null);
  const [generatedPassword, setGeneratedPassword] = useState('');
  const { execute, loading, error } = useApi();

  // Charger les utilisateurs et rôles au montage
  useEffect(() => {
    loadUsers();
    loadRoles();
  }, []);

  const loadUsers = async () => {
    try {
      const usersData = await execute(() => userService.getAllUsers());
      setUsers(usersData);
    } catch (error) {
      // L'erreur est déjà gérée par useApi
    }
  };

  const loadRoles = async () => {
    try {
      const rolesData = await execute(() => roleService.getAllRoles());
      setRoles(rolesData);
    } catch (error) {
      console.error('Erreur lors du chargement des rôles:', error);
    }
  };

  const formik = useFormik({
    initialValues: {
      nom: '',
      prenom: '',
      email: '',
      date_naissance: '',
      roles: [],
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        const result = await execute(
          () => userService.createUser(values),
          'Utilisateur créé avec succès !'
        );
        
        // Afficher le mot de passe généré
        setGeneratedPassword(result.password);
        setModalOpen(false);
        formik.resetForm();
        loadUsers();
      } catch (error) {
        // L'erreur est déjà gérée par useApi
      }
    },
  });

  const editFormik = useFormik({
    initialValues: {
      nom: '',
      prenom: '',
      email: '',
      date_naissance: '',
      roles: [],
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        await execute(
          () => userService.updateUser(selectedUser.id, values),
          'Utilisateur modifié avec succès !'
        );
        setEditModalOpen(false);
        setSelectedUser(null);
        editFormik.resetForm();
        loadUsers();
      } catch (error) {
        // L'erreur est déjà gérée par useApi
      }
    },
  });

  const handleCreateUser = () => {
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    formik.resetForm();
  };

  const handleEditUser = (user) => {
    setSelectedUser(user);
    editFormik.setValues({
      nom: user.nom,
      prenom: user.prenom,
      email: user.email,
      date_naissance: user.date_naissance,
      roles: user.roles ? user.roles.split(',').map(r => r.trim()) : [],
    });
    setEditModalOpen(true);
  };

  const handleCloseEditModal = () => {
    setEditModalOpen(false);
    setSelectedUser(null);
    editFormik.resetForm();
  };

  const handleDeleteUser = (user) => {
    setSelectedUser(user);
    setDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setSelectedUser(null);
  };

  const handleConfirmDelete = async () => {
    try {
      await execute(
        () => userService.deleteUser(selectedUser.id),
        'Utilisateur supprimé avec succès !'
      );
      setDeleteDialogOpen(false);
      setSelectedUser(null);
      loadUsers();
    } catch (error) {
      // L'erreur est déjà gérée par useApi
    }
  };

  const handleResetPassword = (user) => {
    setSelectedUser(user);
    setResetPasswordDialogOpen(true);
  };

  const handleCloseResetPasswordDialog = () => {
    setResetPasswordDialogOpen(false);
    setSelectedUser(null);
  };

  const handleConfirmResetPassword = async () => {
    try {
      await execute(
        () => userService.resetUserPassword(selectedUser.id),
        'Mot de passe réinitialisé avec succès !'
      );
      setResetPasswordDialogOpen(false);
      setSelectedUser(null);
      loadUsers();
    } catch (error) {
      // L'erreur est déjà gérée par useApi
    }
  };

  const formatRoles = (rolesString) => {
    if (!rolesString) return 'Aucun rôle';
    return rolesString.split(',').map(role => role.trim()).join(', ');
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Gestion des Utilisateurs
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          color="primary"
          onClick={handleCreateUser}
        >
          Nouvel Utilisateur
        </Button>
      </Box>

      <Typography variant="body1" color="text.secondary" paragraph>
        Gérez les utilisateurs de Crystal Assur. Les mots de passe sont générés automatiquement à partir de la date de naissance.
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
          {users.map((user) => (
            <Grid item xs={12} md={6} key={user.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6" component="h2">
                      {user.prenom} {user.nom}
                    </Typography>
                    <Chip 
                      label={user.email === 'admin@gmail.com' ? 'Admin Principal' : 'Utilisateur'} 
                      color={user.email === 'admin@gmail.com' ? 'error' : 'primary'} 
                      size="small" 
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Email:</strong> {user.email}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Date de naissance:</strong> {formatDate(user.date_naissance)}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Rôles:</strong> {formatRoles(user.roles)}
                  </Typography>
                  
                  <Typography variant="caption" color="text.secondary" display="block" mb={2}>
                    Créé le {formatDate(user.created_at)}
                  </Typography>
                  
                  <Box display="flex" gap={1}>
                    <Tooltip title="Modifier">
                      <IconButton 
                        size="small" 
                        onClick={() => handleEditUser(user)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    
                    <Tooltip title="Réinitialiser le mot de passe">
                      <IconButton 
                        size="small" 
                        color="warning"
                        onClick={() => handleResetPassword(user)}
                      >
                        <LockIcon />
                      </IconButton>
                    </Tooltip>
                    
                    <Tooltip title="Supprimer">
                      <IconButton 
                        size="small" 
                        color="error"
                        disabled={user.email === 'admin@gmail.com'}
                        onClick={() => handleDeleteUser(user)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Modal de création d'utilisateur */}
      <Dialog open={modalOpen} onClose={handleCloseModal} maxWidth="sm" fullWidth>
        <DialogTitle>Créer un nouvel utilisateur</DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={formik.handleSubmit} sx={{ mt: 1 }}>
            <TextField
              fullWidth
              id="nom"
              name="nom"
              label="Nom"
              value={formik.values.nom}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.nom && Boolean(formik.errors.nom)}
              helperText={formik.touched.nom && formik.errors.nom}
              margin="normal"
            />
            
            <TextField
              fullWidth
              id="prenom"
              name="prenom"
              label="Prénom"
              value={formik.values.prenom}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.prenom && Boolean(formik.errors.prenom)}
              helperText={formik.touched.prenom && formik.errors.prenom}
              margin="normal"
            />
            
            <TextField
              fullWidth
              id="email"
              name="email"
              label="Email"
              type="email"
              value={formik.values.email}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.email && Boolean(formik.errors.email)}
              helperText={formik.touched.email && formik.errors.email}
              margin="normal"
            />
            
            <TextField
              fullWidth
              id="date_naissance"
              name="date_naissance"
              label="Date de naissance"
              type="date"
              value={formik.values.date_naissance}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.date_naissance && Boolean(formik.errors.date_naissance)}
              helperText={formik.touched.date_naissance && formik.errors.date_naissance}
              margin="normal"
              InputLabelProps={{ shrink: true }}
            />
            
            <FormControl fullWidth margin="normal">
              <InputLabel id="roles-label">Rôles</InputLabel>
              <Select
                labelId="roles-label"
                id="roles"
                name="roles"
                multiple
                value={formik.values.roles}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.roles && Boolean(formik.errors.roles)}
                input={<OutlinedInput label="Rôles" />}
                renderValue={(selected) => selected.join(', ')}
              >
                {roles.map((role) => (
                  <MenuItem key={role.id} value={role.name}>
                    <Checkbox checked={formik.values.roles.indexOf(role.name) > -1} />
                    <ListItemText primary={role.name} />
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseModal}>Annuler</Button>
          <Button
            type="submit"
            variant="contained"
            onClick={formik.handleSubmit}
            disabled={loading}
          >
            {loading ? 'Création...' : 'Créer'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Modal de modification d'utilisateur */}
      <Dialog open={editModalOpen} onClose={handleCloseEditModal} maxWidth="sm" fullWidth>
        <DialogTitle>Modifier l&apos;utilisateur</DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={editFormik.handleSubmit} sx={{ mt: 1 }}>
            <TextField
              fullWidth
              id="edit-nom"
              name="nom"
              label="Nom"
              value={editFormik.values.nom}
              onChange={editFormik.handleChange}
              onBlur={editFormik.handleBlur}
              error={editFormik.touched.nom && Boolean(editFormik.errors.nom)}
              helperText={editFormik.touched.nom && editFormik.errors.nom}
              margin="normal"
            />
            
            <TextField
              fullWidth
              id="edit-prenom"
              name="prenom"
              label="Prénom"
              value={editFormik.values.prenom}
              onChange={editFormik.handleChange}
              onBlur={editFormik.handleBlur}
              error={editFormik.touched.prenom && Boolean(editFormik.errors.prenom)}
              helperText={editFormik.touched.prenom && editFormik.errors.prenom}
              margin="normal"
            />
            
            <TextField
              fullWidth
              id="edit-email"
              name="email"
              label="Email"
              type="email"
              value={editFormik.values.email}
              onChange={editFormik.handleChange}
              onBlur={editFormik.handleBlur}
              error={editFormik.touched.email && Boolean(editFormik.errors.email)}
              helperText={editFormik.touched.email && editFormik.errors.email}
              margin="normal"
            />
            
            <TextField
              fullWidth
              id="edit-date_naissance"
              name="date_naissance"
              label="Date de naissance"
              type="date"
              value={editFormik.values.date_naissance}
              onChange={editFormik.handleChange}
              onBlur={editFormik.handleBlur}
              error={editFormik.touched.date_naissance && Boolean(editFormik.errors.date_naissance)}
              helperText={editFormik.touched.date_naissance && editFormik.errors.date_naissance}
              margin="normal"
              InputLabelProps={{ shrink: true }}
            />
            
            <FormControl fullWidth margin="normal">
              <InputLabel id="edit-roles-label">Rôles</InputLabel>
              <Select
                labelId="edit-roles-label"
                id="edit-roles"
                name="roles"
                multiple
                value={editFormik.values.roles}
                onChange={editFormik.handleChange}
                onBlur={editFormik.handleBlur}
                error={editFormik.touched.roles && Boolean(editFormik.errors.roles)}
                input={<OutlinedInput label="Rôles" />}
                renderValue={(selected) => selected.join(', ')}
              >
                {roles.map((role) => (
                  <MenuItem key={role.id} value={role.name}>
                    <Checkbox checked={editFormik.values.roles.indexOf(role.name) > -1} />
                    <ListItemText primary={role.name} />
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditModal}>Annuler</Button>
          <Button
            type="submit"
            variant="contained"
            onClick={editFormik.handleSubmit}
            disabled={loading}
          >
            {loading ? 'Modification...' : 'Modifier'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de confirmation de suppression */}
      <Dialog open={deleteDialogOpen} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Confirmer la suppression</DialogTitle>
        <DialogContent>
          <Typography>
            Êtes-vous sûr de vouloir supprimer l&apos;utilisateur <strong>{selectedUser?.prenom} {selectedUser?.nom}</strong> ?
            Cette action est irréversible.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>Annuler</Button>
          <Button onClick={handleConfirmDelete} color="error" variant="contained">
            Supprimer
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de confirmation de réinitialisation de mot de passe */}
      <Dialog open={resetPasswordDialogOpen} onClose={handleCloseResetPasswordDialog}>
        <DialogTitle>Confirmer la réinitialisation</DialogTitle>
        <DialogContent>
          <Typography>
            Êtes-vous sûr de vouloir réinitialiser le mot de passe de l&apos;utilisateur <strong>{selectedUser?.prenom} {selectedUser?.nom}</strong> ?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Le nouveau mot de passe sera basé sur sa date de naissance au format YYYYMMDD.
            L&apos;utilisateur devra changer son mot de passe lors de sa prochaine connexion.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseResetPasswordDialog}>Annuler</Button>
          <Button onClick={handleConfirmResetPassword} color="warning" variant="contained">
            Réinitialiser
          </Button>
        </DialogActions>
      </Dialog>

    </Box>
  );
};

export default UserManagementPage; 