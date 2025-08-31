import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  InputAdornment,
  Snackbar,
  Alert
} from '@mui/material';

import { opportunityService } from '../../services/opportunityService';
import { produitService } from '../../services/produitService';

const EditOpportunityModal = ({ 
  open, 
  onClose, 
  opportunityData,
  onSuccess
}) => {
  const [formData, setFormData] = useState({
    idProduit: '',
    origine: 'Prospection',
    etape: 'Qualification',
    dateEcheance: '',
    description: '',
    budgetEstime: '',
    transformed: false,
    idContrat: null,
    dateTransformation: null
  });

  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [produits, setProduits] = useState([]);

  // Load products when modal opens
  useEffect(() => {
    if (open) {
      loadProduits();
    }
  }, [open]);

  // Populate form data when opportunity data is provided
  useEffect(() => {
    if (open && opportunityData) {
      setFormData({
        idProduit: opportunityData.idProduit || '',
        origine: opportunityData.origine || 'Prospection',
        etape: opportunityData.etape || 'Qualification',
        dateEcheance: opportunityData.dateEcheance || '',
        description: opportunityData.description || '',
        budgetEstime: opportunityData.budgetEstime || '',
        transformed: opportunityData.transformed || false,
        idContrat: opportunityData.idContrat || null,
        dateTransformation: opportunityData.dateTransformation || null
      });
    }
  }, [open, opportunityData]);

  const loadProduits = async () => {
    try {
      console.log('🔄 Loading produits...');
      const produitsData = await produitService.getProduits();
      console.log('✅ Produits loaded:', produitsData);
      setProduits(produitsData);
    } catch (error) {
      console.error('❌ Error loading produits:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage('');

    try {
      // Prepare data for submission
      const submitData = {
        idProduit: formData.idProduit ? parseInt(formData.idProduit) : null,
        origine: formData.origine,
        etape: formData.etape,
        dateEcheance: formData.dateEcheance || null,
        description: formData.description,
        budgetEstime: formData.budgetEstime ? parseFloat(formData.budgetEstime) : null
      };

      await opportunityService.updateOpportunity(opportunityData.id, submitData);
      
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error updating opportunity:', error);
      
      // Extract meaningful error message
      let errorMsg = 'Erreur lors de la modification de l&apos;opportunité';
      
      if (error.response?.data?.detail) {
        errorMsg = error.response.data.detail;
      } else if (error.message) {
        errorMsg = error.message;
      }
      
      setErrorMessage(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseError = () => {
    setErrorMessage('');
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Modifier l&apos;Opportunité</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          {/* Error Alert */}
          {errorMessage && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {errorMessage}
            </Alert>
          )}
          
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Produit</InputLabel>
                <Select
                  value={formData.idProduit}
                  onChange={(e) => handleChange('idProduit', e.target.value)}
                  label="Produit"
                  required
                >
                  {produits.length > 0 ? (
                    produits.map((produit) => (
                      <MenuItem key={produit.id} value={produit.id}>
                        {produit.libelle}
                      </MenuItem>
                    ))
                  ) : (
                    <MenuItem disabled>Aucun produit disponible</MenuItem>
                  )}
                </Select>
                {produits.length === 0 && (
                  <Typography variant="caption" color="text.secondary">
                    Chargement des produits...
                  </Typography>
                )}
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Origine</InputLabel>
                <Select
                  value={formData.origine}
                  onChange={(e) => handleChange('origine', e.target.value)}
                  label="Origine"
                >
                  <MenuItem value="Prospection">Prospection</MenuItem>
                  <MenuItem value="Référencement">Référencement</MenuItem>
                  <MenuItem value="Campagne Marketing">Campagne Marketing</MenuItem>
                  <MenuItem value="Appel entrant">Appel entrant</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Étape</InputLabel>
                <Select
                  value={formData.etape}
                  onChange={(e) => handleChange('etape', e.target.value)}
                  label="Étape"
                >
                  <MenuItem value="Qualification">Qualification</MenuItem>
                  <MenuItem value="Analyse besoin">Analyse besoin</MenuItem>
                  <MenuItem value="Proposition">Proposition</MenuItem>
                  <MenuItem value="Gagnée">Gagnée</MenuItem>
                  <MenuItem value="Perdue">Perdue</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Date d&apos;échéance"
                type="date"
                value={formData.dateEcheance}
                onChange={(e) => handleChange('dateEcheance', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Budget estimé (DH)"
                type="number"
                value={formData.budgetEstime}
                onChange={(e) => handleChange('budgetEstime', e.target.value)}
                placeholder="Budget estimé en dirhams"
                InputProps={{
                  startAdornment: <InputAdornment position="start">DH</InputAdornment>,
                }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                multiline
                rows={3}
                placeholder="Description de l&apos;opportunité"
              />
            </Grid>
          </Grid>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>
            Annuler
          </Button>
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={loading}
          >
            {loading ? 'Modification...' : 'Confirmer'}
          </Button>
        </DialogActions>
      </form>
      
      {/* Error Snackbar */}
      <Snackbar
        open={!!errorMessage}
        autoHideDuration={6000}
        onClose={handleCloseError}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseError} 
          severity="error" 
          sx={{ width: '100%' }}
        >
          {errorMessage}
        </Alert>
      </Snackbar>
    </Dialog>
  );
};

export default EditOpportunityModal;
