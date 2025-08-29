import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Checkbox,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Stack,
  Chip,
  Alert,
  CircularProgress
} from '@mui/material';
import { clientService } from '../../services/clientService';
import { clientRelationService } from '../../services/clientRelationService';

const AddAssociateModal = ({ 
  open, 
  onClose, 
  onSuccess, 
  clientId
}) => {
  const [step, setStep] = useState(1); // 1: select clients, 2: input relations
  const [availableClients, setAvailableClients] = useState([]);
  const [selectedClients, setSelectedClients] = useState([]);
  const [relations, setRelations] = useState([]);
  const [typeRelations, setTypeRelations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (open) {
      loadData();
    }
  }, [open]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Load clients and type relations in parallel
      const [clientsResponse, typesResponse] = await Promise.all([
        clientService.getClients({ limit: 1000 }), // Get all clients
        clientRelationService.getTypeRelations()
      ]);
      
      console.log('📦 Clients response:', clientsResponse);
      console.log('📦 Types response:', typesResponse);
      
      // Handle different response structures for clients
      let allClients = [];
      if (Array.isArray(clientsResponse)) {
        allClients = clientsResponse;
      } else if (clientsResponse && clientsResponse.clients) {
        allClients = clientsResponse.clients;
      } else {
        console.warn('⚠️ Unexpected clients response structure:', clientsResponse);
        allClients = [];
      }
      
      // Filter out the current client and only show PARTICULIER clients
      // This ensures only individual clients can be associated, not companies
      const filteredClients = allClients.filter(client => 
        client.id !== clientId && 
        client.typeClient === 'PARTICULIER'
      );
      
      console.log('✅ Available clients after filtering:', filteredClients);
      
      setAvailableClients(filteredClients);
      setTypeRelations(typesResponse || []);
    } catch (error) {
      console.error('❌ Error loading data:', error);
      setError(`Erreur lors du chargement des données: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleClientSelection = (clientId, checked) => {
    if (checked) {
      setSelectedClients(prev => [...prev, clientId]);
    } else {
      setSelectedClients(prev => prev.filter(id => id !== clientId));
    }
  };

  const handleNext = () => {
    if (selectedClients.length === 0) {
      setError('Veuillez sélectionner au moins un client');
      return;
    }
    
    // Initialize relations for selected clients
    const initialRelations = selectedClients.map(clientId => ({
      idClientLie: clientId,
      idTypeRelation: '',
      description: ''
    }));
    setRelations(initialRelations);
    setStep(2);
    setError('');
  };

  const handleBack = () => {
    setStep(1);
    setSelectedClients([]);
    setRelations([]);
    setError('');
  };

  const handleRelationChange = (index, field, value) => {
    const updatedRelations = [...relations];
    updatedRelations[index] = {
      ...updatedRelations[index],
      [field]: value
    };
    setRelations(updatedRelations);
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Validate all relations have type selected
      const invalidRelations = relations.filter(rel => !rel.idTypeRelation);
      if (invalidRelations.length > 0) {
        setError('Veuillez sélectionner un type de relation pour tous les clients');
        return;
      }
      
      console.log('🔄 Creating relations:', relations);
      
      // Create relations for all selected clients
      for (const relation of relations) {
        console.log('🔄 Creating relation:', relation);
        const result = await clientRelationService.createClientRelation({
          idClientPrincipal: clientId,
          idClientLie: relation.idClientLie,
          idTypeRelation: relation.idTypeRelation,
          description: relation.description || '',
          dateDebut: new Date().toISOString().split('T')[0]
        });
        console.log('✅ Relation created:', result);
      }
      
      console.log('✅ All relations created successfully');
      console.log('🔄 Calling onSuccess callback');
      onSuccess();
      console.log('🔄 Closing modal');
      onClose();
    } catch (error) {
      console.error('❌ Error creating relations:', error);
      setError(`Erreur lors de la création des relations: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getClientName = (clientId) => {
    const client = availableClients.find(c => c.id === clientId);
    return client ? (client.nom || client.codeClient || 'N/A') : 'N/A';
  };

  const renderClientSelection = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Sélectionner les clients à associer
      </Typography>
      
      {availableClients.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography color="text.secondary">
            Aucun client disponible pour l&apos;association
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Tous les clients PARTICULIER sont déjà associés ou il n&apos;y en a pas d&apos;autres.
          </Typography>
        </Box>
      ) : (
        <>
          <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selectedClients.length === availableClients.length}
                      indeterminate={selectedClients.length > 0 && selectedClients.length < availableClients.length}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedClients(availableClients.map(c => c.id));
                        } else {
                          setSelectedClients([]);
                        }
                      }}
                    />
                  </TableCell>
                  <TableCell>Code Client</TableCell>
                  <TableCell>Nom</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Téléphone</TableCell>
                  <TableCell>Email</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {availableClients.map((client) => (
                  <TableRow key={client.id}>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selectedClients.includes(client.id)}
                        onChange={(e) => handleClientSelection(client.id, e.target.checked)}
                      />
                    </TableCell>
                    <TableCell>{client.codeClient || 'N/A'}</TableCell>
                    <TableCell>{client.nom || 'N/A'}</TableCell>
                    <TableCell>
                      <Chip 
                        label={client.typeClient} 
                        size="small"
                        color={client.typeClient === 'PARTICULIER' ? 'primary' : 'secondary'}
                      />
                    </TableCell>
                    <TableCell>{client.tel || '-'}</TableCell>
                    <TableCell>{client.email || '-'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
            <Button onClick={onClose} disabled={loading}>
              Annuler
            </Button>
            <Button 
              variant="contained" 
              onClick={handleNext}
              disabled={selectedClients.length === 0 || loading}
            >
              Suivant ({selectedClients.length} sélectionné{selectedClients.length > 1 ? 's' : ''})
            </Button>
          </Box>
        </>
      )}
    </Box>
  );

  const renderRelationInput = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Définir les relations
      </Typography>
      
      <Stack spacing={2}>
        {relations.map((relation, index) => (
          <Paper key={index} sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              {getClientName(relation.idClientLie)}
            </Typography>
            
            <Stack direction="row" spacing={2} alignItems="center">
              <FormControl size="small" sx={{ minWidth: 200 }}>
                <InputLabel>Type de relation *</InputLabel>
                <Select
                  value={relation.idTypeRelation}
                  onChange={(e) => handleRelationChange(index, 'idTypeRelation', e.target.value)}
                  label="Type de relation *"
                  required
                >
                  {typeRelations.map((type) => (
                    <MenuItem key={type.id} value={type.id}>
                      {type.libelle}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <TextField
                label="Description"
                value={relation.description}
                onChange={(e) => handleRelationChange(index, 'description', e.target.value)}
                size="small"
                sx={{ flexGrow: 1 }}
                placeholder="Description de la relation (optionnel)..."
              />
            </Stack>
          </Paper>
        ))}
      </Stack>
      
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
        <Button onClick={handleBack} disabled={loading}>
          Retour
        </Button>
        <Button 
          variant="contained" 
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? <CircularProgress size={20} /> : 'Confirmer'}
        </Button>
      </Box>
    </Box>
  );

  if (loading && step === 1) {
    return (
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogContent>
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Ajouter des associés
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {step === 1 ? renderClientSelection() : renderRelationInput()}
      </DialogContent>
    </Dialog>
  );
};

export default AddAssociateModal;
