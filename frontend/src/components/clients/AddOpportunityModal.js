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
  Grid
} from '@mui/material';

import { opportunityService } from '../../services/opportunityService';
import { produitService } from '../../services/produitService';

const AddOpportunityModal = ({ 
  open, 
  onClose, 
  clientId,
  onSuccess,
  clientType 
}) => {
  const [formData, setFormData] = useState({
    idProduit: '',
    origine: 'Prospection',
    etape: 'Qualification',
    dateEcheance: '',
    description: ''
  });

  const [loading, setLoading] = useState(false);
  const [produits, setProduits] = useState([]);

  // Load products when modal opens
  useEffect(() => {
    if (open) {
      loadProduits();
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      const opportunityData = {
        idClient: clientId,
        idUser: 1, // TODO: Get from auth context
        ...formData,
        dateEcheance: formData.dateEcheance || null
      };
      
      await opportunityService.createOpportunity(opportunityData);
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error creating opportunity:', error);
      alert('Erreur lors de la création de l\'opportunité');
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

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Ajouter une Opportunité</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
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
                label="Date d'échéance"
                type="date"
                value={formData.dateEcheance}
                onChange={(e) => handleChange('dateEcheance', e.target.value)}
                InputLabelProps={{ shrink: true }}
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
                placeholder="Description de l'opportunité"
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
            disabled={loading}
          >
            {loading ? 'Création...' : 'Créer'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default AddOpportunityModal;
