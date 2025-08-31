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
import { clientService } from '../../services/clientService';

const AddOpportunityModal = ({ 
  open, 
  onClose, 
  onSuccess
}) => {
  const [formData, setFormData] = useState({
    idClient: '',
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
  const [clients, setClients] = useState([]);

  // Load products and clients when modal opens
  useEffect(() => {
    if (open) {
      // Reset form to initial state when modal opens
      setFormData({
        idClient: '',
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
      setErrorMessage('');
      loadProduits();
      loadClients();
    }
  }, [open]);

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

  const loadClients = async () => {
    try {
      console.log('🔄 Loading clients...');
      const clientsData = await clientService.getAllClients(); // Get all clients
      console.log('✅ Clients loaded:', clientsData);
      setClients(clientsData); // Direct array of clients
    } catch (error) {
      console.error('❌ Error loading clients:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage('');

    try {
      const opportunityData = {
        idClient: formData.idClient ? parseInt(formData.idClient) : null,
        idUser: 1, // Default user ID
        idProduit: formData.idProduit ? parseInt(formData.idProduit) : null,
        origine: formData.origine,
        etape: formData.etape,
        dateEcheance: formData.dateEcheance || null,
        description: formData.description,
        budgetEstime: formData.budgetEstime ? parseFloat(formData.budgetEstime) : null
      };

      await opportunityService.createOpportunity(opportunityData);
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error creating opportunity:', error);
      
      // Extract meaningful error message
      let errorMsg = 'Erreur lors de la création de l&apos;opportunité';
      
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

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleCloseError = () => {
    setErrorMessage('');
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Ajouter une Opportunité</DialogTitle>
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
                <InputLabel>Produit *</InputLabel>
                <Select
                  value={formData.idProduit}
                  onChange={(e) => handleChange('idProduit', e.target.value)}
                  label="Produit *"
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

            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Client *</InputLabel>
                <Select
                  value={formData.idClient}
                  onChange={(e) => handleChange('idClient', e.target.value)}
                  label="Client *"
                  required
                >
                                     {clients.length > 0 ? (
                     clients.map((client) => (
                       <MenuItem key={client.id} value={client.id}>
                         {client.nom || client.codeClient} - {client.typeClient}
                       </MenuItem>
                     ))
                   ) : (
                    <MenuItem disabled>Aucun client disponible</MenuItem>
                  )}
                </Select>
                {clients.length === 0 && (
                  <Typography variant="caption" color="text.secondary">
                    Chargement des clients...
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
            {loading ? 'Création...' : 'Créer'}
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

export default AddOpportunityModal;
