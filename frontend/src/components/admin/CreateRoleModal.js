import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Typography,
  Alert,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useApi } from '../../hooks/useApi';
import { roleService } from '../../services/roleService';

const validationSchema = Yup.object({
  name: Yup.string()
    .min(2, 'Le nom doit contenir au moins 2 caractères')
    .max(50, 'Le nom ne peut pas dépasser 50 caractères')
    .required('Nom du rôle requis'),
  description: Yup.string()
    .max(500, 'La description ne peut pas dépasser 500 caractères'),
});

const CreateRoleModal = ({ open, onClose, onRoleCreated }) => {
  const { execute, loading, error } = useApi();

  const formik = useFormik({
    initialValues: {
      name: '',
      description: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        await execute(
          () => roleService.createRole(values),
          'Rôle créé avec succès !'
        );
        formik.resetForm();
        onRoleCreated();
        onClose();
      } catch (error) {
        // L'erreur est déjà gérée par useApi
      }
    },
  });

  const handleClose = () => {
    formik.resetForm();
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <AddIcon color="primary" />
          <Typography variant="h6">Créer un nouveau rôle</Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Box component="form" onSubmit={formik.handleSubmit} sx={{ mt: 1 }}>
          <TextField
            fullWidth
            id="name"
            name="name"
            label="Nom du rôle"
            value={formik.values.name}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.name && Boolean(formik.errors.name)}
            helperText={formik.touched.name && formik.errors.name}
            margin="normal"
            placeholder="Ex: courtier_senior"
          />
          
          <TextField
            fullWidth
            id="description"
            name="description"
            label="Description"
            value={formik.values.description}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.description && Boolean(formik.errors.description)}
            helperText={formik.touched.description && formik.errors.description}
            margin="normal"
            multiline
            rows={3}
            placeholder="Description du rôle et de ses permissions..."
          />
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Annuler
        </Button>
        <Button
          type="submit"
          variant="contained"
          onClick={formik.handleSubmit}
          disabled={loading}
          startIcon={<AddIcon />}
        >
          {loading ? 'Création...' : 'Créer le rôle'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateRoleModal; 