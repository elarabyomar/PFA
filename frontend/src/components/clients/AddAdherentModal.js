import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  Alert,
  Tabs,
  Tab,
  Grid
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { fr } from 'date-fns/locale';
import { adherentService } from '../../services/adherentService';

const AddAdherentModal = ({ 
  open, 
  onClose, 
  onSuccess, 
  clientId,
  adherentType // 'flotte_auto' or 'assure_sante'
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [marques, setMarques] = useState([]);
  const [carrosseries, setCarrosseries] = useState([]);
  
  // Flotte Auto form data
  const [flotteAutoData, setFlotteAutoData] = useState({
    matricule: '',
    idMarque: '',
    modele: '',
    idCarrosserie: '',
    dateMiseCirculation: null,
    valeurNeuve: '',
    valeurVenale: ''
  });
  
  // Assure Sante form data
  const [assureSanteData, setAssureSanteData] = useState({
    nom: '',
    prenom: '',
    cin: '',
    dateNaissance: null,
    numImmatriculation: '',
    categorie: '',
    lienParente: ''
  });

  useEffect(() => {
    if (open && adherentType === 'flotte_auto') {
      loadReferenceData();
    }
  }, [open, adherentType]);

  const loadReferenceData = async () => {
    try {
      const [marquesData, carrosseriesData] = await Promise.all([
        adherentService.getMarques(),
        adherentService.getCarrosseries()
      ]);
      setMarques(marquesData);
      setCarrosseries(carrosseriesData);
    } catch (error) {
      console.error('Error loading reference data:', error);
      setError('Erreur lors du chargement des données de référence');
    }
  };

  const handleFlotteAutoChange = (field, value) => {
    setFlotteAutoData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAssureSanteChange = (field, value) => {
    setAssureSanteData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError('');

      if (adherentType === 'flotte_auto') {
        // Validate required fields
        if (!flotteAutoData.matricule || !flotteAutoData.modele) {
          setError('Veuillez remplir tous les champs obligatoires');
          return;
        }

        const data = {
          ...flotteAutoData,
          idClientSociete: clientId,
          dateMiseCirculation: flotteAutoData.dateMiseCirculation?.toISOString().split('T')[0],
          valeurNeuve: flotteAutoData.valeurNeuve ? parseFloat(flotteAutoData.valeurNeuve) : null,
          valeurVenale: flotteAutoData.valeurVenale ? parseFloat(flotteAutoData.valeurVenale) : null
        };

        await adherentService.createFlotteAuto(data);
      } else {
        // Validate required fields
        if (!assureSanteData.nom || !assureSanteData.prenom) {
          setError('Veuillez remplir tous les champs obligatoires');
          return;
        }

        const data = {
          ...assureSanteData,
          idClientSociete: clientId,
          dateNaissance: assureSanteData.dateNaissance?.toISOString().split('T')[0]
        };

        await adherentService.createAssureSante(data);
      }

      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error creating adherent:', error);
      setError('Erreur lors de la création de l\'adhérent');
    } finally {
      setLoading(false);
    }
  };

  const renderFlotteAutoForm = () => (
    <Stack spacing={2}>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            label="Matricule *"
            value={flotteAutoData.matricule}
            onChange={(e) => handleFlotteAutoChange('matricule', e.target.value)}
            fullWidth
            required
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Marque</InputLabel>
            <Select
              value={flotteAutoData.idMarque}
              onChange={(e) => handleFlotteAutoChange('idMarque', e.target.value)}
              label="Marque"
            >
              {marques.map((marque) => (
                <MenuItem key={marque.id} value={marque.id}>
                  {marque.libelle}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            label="Modèle *"
            value={flotteAutoData.modele}
            onChange={(e) => handleFlotteAutoChange('modele', e.target.value)}
            fullWidth
            required
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Carrosserie</InputLabel>
            <Select
              value={flotteAutoData.idCarrosserie}
              onChange={(e) => handleFlotteAutoChange('idCarrosserie', e.target.value)}
              label="Carrosserie"
            >
              {carrosseries.map((carrosserie) => (
                <MenuItem key={carrosserie.id} value={carrosserie.id}>
                  {carrosserie.libelle}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6}>
          <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={fr}>
            <DatePicker
              label="Date de mise en circulation"
              value={flotteAutoData.dateMiseCirculation}
              onChange={(date) => handleFlotteAutoChange('dateMiseCirculation', date)}
              renderInput={(params) => <TextField {...params} fullWidth />}
            />
          </LocalizationProvider>
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            label="Valeur à neuf"
            type="number"
            value={flotteAutoData.valeurNeuve}
            onChange={(e) => handleFlotteAutoChange('valeurNeuve', e.target.value)}
            fullWidth
            inputProps={{ step: "0.01", min: "0" }}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            label="Valeur vénale"
            type="number"
            value={flotteAutoData.valeurVenale}
            onChange={(e) => handleFlotteAutoChange('valeurVenale', e.target.value)}
            fullWidth
            inputProps={{ step: "0.01", min: "0" }}
          />
        </Grid>
      </Grid>
    </Stack>
  );

  const renderAssureSanteForm = () => (
    <Stack spacing={2}>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            label="Nom *"
            value={assureSanteData.nom}
            onChange={(e) => handleAssureSanteChange('nom', e.target.value)}
            fullWidth
            required
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            label="Prénom *"
            value={assureSanteData.prenom}
            onChange={(e) => handleAssureSanteChange('prenom', e.target.value)}
            fullWidth
            required
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            label="CIN"
            value={assureSanteData.cin}
            onChange={(e) => handleAssureSanteChange('cin', e.target.value)}
            fullWidth
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={fr}>
            <DatePicker
              label="Date de naissance"
              value={assureSanteData.dateNaissance}
              onChange={(date) => handleAssureSanteChange('dateNaissance', date)}
              renderInput={(params) => <TextField {...params} fullWidth />}
            />
          </LocalizationProvider>
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            label="Numéro d'immatriculation"
            value={assureSanteData.numImmatriculation}
            onChange={(e) => handleAssureSanteChange('numImmatriculation', e.target.value)}
            fullWidth
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Catégorie</InputLabel>
            <Select
              value={assureSanteData.categorie}
              onChange={(e) => handleAssureSanteChange('categorie', e.target.value)}
              label="Catégorie"
            >
              <MenuItem value="CADRE">CADRE</MenuItem>
              <MenuItem value="NON-CADRE">NON-CADRE</MenuItem>
              <MenuItem value="DIRIGEANT">DIRIGEANT</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12}>
          <FormControl fullWidth>
            <InputLabel>Lien de parenté</InputLabel>
            <Select
              value={assureSanteData.lienParente}
              onChange={(e) => handleAssureSanteChange('lienParente', e.target.value)}
              label="Lien de parenté"
            >
              <MenuItem value="ASSURE_PRINCIPAL">Assuré Principal</MenuItem>
              <MenuItem value="CONJOINT">Conjoint</MenuItem>
              <MenuItem value="ENFANT">Enfant</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>
    </Stack>
  );

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Ajouter un adhérent - {adherentType === 'flotte_auto' ? 'Flotte Automobile' : 'Assuré Santé'}
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {adherentType === 'flotte_auto' ? renderFlotteAutoForm() : renderAssureSanteForm()}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Annuler
        </Button>
        <Button 
          variant="contained" 
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? 'Création...' : 'Créer'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddAdherentModal;
