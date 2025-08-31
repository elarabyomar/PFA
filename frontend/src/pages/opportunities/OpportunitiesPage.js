import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Stack,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
  Grid,
  InputAdornment
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Transform as TransformIcon,
  FileUpload as FileUploadIcon,
  Description as DescriptionIcon
} from '@mui/icons-material';
import { opportunityService } from '../../services/opportunityService';
import { produitService } from '../../services/produitService';
import { clientService } from '../../services/clientService';
import { contractService } from '../../services/contractService';
import AddOpportunityModal from '../../components/opportunities/AddOpportunityModal';
import EditOpportunityModal from '../../components/opportunities/EditOpportunityModal';

const OpportunitiesPage = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [skip, setSkip] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  
  // Search and filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    etape: '',
    origine: '',
    transformed: ''
  });
  
  // Filter options
  const [filterOptions, setFilterOptions] = useState({
    etapes: ['Qualification', 'Analyse besoin', 'Proposition', 'Gagnée', 'Perdue'],
    origines: ['Prospection', 'Référencement', 'Campagne Marketing', 'Appel entrant'],
    transformedOptions: ['Tous', 'Transformées', 'Non transformées']
  });

  // Modal states
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedOpportunity, setSelectedOpportunity] = useState(null);
  const [transformModalOpen, setTransformModalOpen] = useState(false);
  const [transformFormData, setTransformFormData] = useState({
    typeContrat: 'Duree ferme',
    dateDebut: '',
    dateFin: '',
    prime: '',
    idCompagnie: '',
    idTypeDuree: ''
  });
  const [companies, setCompanies] = useState([]);
  const [durationTypes, setDurationTypes] = useState([]);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  
  // Document handling functions
  const handleTransformDocumentUpload = (event) => {
    const files = Array.from(event.target.files);
    const pdfFiles = files.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length !== files.length) {
      alert('Seuls les fichiers PDF sont acceptés');
      return;
    }
    
    setSelectedDocuments(prev => [...prev, ...pdfFiles]);
  };

  const removeTransformDocument = (index) => {
    setSelectedDocuments(prev => prev.filter((_, i) => i !== index));
  };

  // Document click handler for transform modal
  const handleTransformDocumentClick = (document) => {
    console.log('📄 Transform document clicked:', document);
    
    // For transformation documents, we can show a preview or download
    if (document && document.name) {
      // Create a temporary URL for the file
      const fileUrl = URL.createObjectURL(document);
      
      // Open the file in a new window/tab
      const newWindow = window.open(fileUrl, '_blank');
      if (!newWindow) {
        console.error('❌ Failed to open document window');
        alert('Impossible d\'ouvrir le document dans une nouvelle fenêtre. Vérifiez les bloqueurs de popup.');
      } else {
        console.log('✅ Transform document window opened successfully');
      }
      
      // Clean up the URL after a delay
      setTimeout(() => URL.revokeObjectURL(fileUrl), 1000);
    }
  };
  
  // Delete confirmation modal state
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [opportunityToDelete, setOpportunityToDelete] = useState(null);
  
  // Success message state
  const [successMessage, setSuccessMessage] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [showError, setShowError] = useState(false);

  const limit = 50;

  // Load opportunities
  const loadOpportunities = useCallback(async (reset = false) => {
    if (reset) {
      setSkip(0);
    }
    setLoading(true);
    try {
      const currentSkip = reset ? 0 : skip;
      const params = {
        skip: currentSkip,
        limit,
        search: searchTerm,
        ...filters
      };
      
      const response = await opportunityService.getOpportunities(params);
      
      if (reset) {
        setOpportunities(response.opportunities || response);
        setSkip(limit);
      } else {
        setOpportunities(prev => [...prev, ...(response.opportunities || response)]);
        setSkip(prev => prev + limit);
      }
      
      setTotalCount(response.total_count || (response.opportunities || response).length);
      setHasMore(response.has_more || (response.opportunities || response).length >= limit);
    } catch (error) {
      console.error('Error loading opportunities:', error);
      setErrorMessage('Erreur lors du chargement des opportunités');
      setShowError(true);
    } finally {
      setLoading(false);
    }
  }, [skip, limit, searchTerm, filters]);

  useEffect(() => {
    loadOpportunities(true);
  }, [searchTerm, filters]);

  // Filter opportunities based on search and filters
  const filteredOpportunities = opportunities.filter(opp => {
         const matchesSearch = !searchTerm || 
       (opp.produit?.libelle && opp.produit.libelle.toLowerCase().includes(searchTerm.toLowerCase())) ||
       (opp.client?.nom && opp.client.nom.toLowerCase().includes(searchTerm.toLowerCase())) ||
       (opp.client?.codeClient && opp.client.codeClient.toLowerCase().includes(searchTerm.toLowerCase())) ||
       (opp.origine && opp.origine.toLowerCase().includes(searchTerm.toLowerCase())) ||
       (opp.etape && opp.etape.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesEtape = !filters.etape || opp.etape === filters.etape;
    const matchesOrigine = !filters.origine || opp.origine === filters.origine;
    
    let matchesTransformed = true;
    if (filters.transformed === 'Transformées') {
      matchesTransformed = opp.transformed === true;
    } else if (filters.transformed === 'Non transformées') {
      matchesTransformed = opp.transformed === false;
    }

    return matchesSearch && matchesEtape && matchesOrigine && matchesTransformed;
  });

  // Handle add opportunity
  const handleAddOpportunity = () => {
    setAddModalOpen(true);
  };

  // Handle edit opportunity
  const handleEditOpportunity = (opportunity) => {
    setSelectedOpportunity(opportunity);
    setEditModalOpen(true);
  };

  // Handle delete opportunity
  const handleDeleteOpportunity = (opportunityId) => {
    const opportunity = opportunities.find(opp => opp.id === opportunityId);
    setOpportunityToDelete(opportunity);
    setDeleteModalOpen(true);
  };

  // Confirm delete
  const confirmDelete = async () => {
    if (!opportunityToDelete) return;
    
    try {
             await opportunityService.deleteOpportunity(opportunityToDelete.id);
       setSuccessMessage('Opportunité supprimée avec succès');
       setShowSuccess(true);
       loadOpportunities(true); // Reset the list when deleting opportunity
    } catch (error) {
      console.error('Error deleting opportunity:', error);
      setErrorMessage('Erreur lors de la suppression de l&apos;opportunité');
      setShowError(true);
    } finally {
      setDeleteModalOpen(false);
      setOpportunityToDelete(null);
    }
  };

  // Handle transform opportunity
  const handleTransformOpportunity = async (opportunityId) => {
    const opportunity = opportunities.find(opp => opp.id === opportunityId);
    if (!opportunity) {
      console.error('❌ Opportunity not found:', opportunityId);
      return;
    }
    
    setSelectedOpportunity(opportunity);
    // Set default dateDebut to today
    const today = new Date().toISOString().split('T')[0];
    
    setTransformFormData({
      typeContrat: 'Duree ferme',
      dateDebut: today,
      dateFin: '',
      prime: '',
      idCompagnie: '',
      idTypeDuree: ''
    });
    setTransformModalOpen(true);
    
    // Load companies and duration types when opening the modal
    await loadCompanies();
    await loadDurationTypes();
  };

  const loadCompanies = async () => {
    try {
      const response = await fetch('/api/references/compagnies');
      if (response.ok) {
        const data = await response.json();
        setCompanies(data);
      }
    } catch (error) {
      console.error('❌ Error loading companies:', error);
    }
  };

  const loadDurationTypes = async () => {
    try {
      const response = await fetch('/api/references/duree');
      if (response.ok) {
        const data = await response.json();
        setDurationTypes(data);
      }
    } catch (error) {
      console.error('❌ Error loading duration types:', error);
    }
  };

  const handleTransformSubmit = async () => {
    try {
      console.log('🔄 Starting opportunity transformation for ID:', selectedOpportunity.id);
      
      if (!transformFormData.dateDebut || !transformFormData.dateFin) {
        setErrorMessage('Les dates de début et de fin sont obligatoires');
        setShowError(true);
        return;
      }

      const contractData = {
        typeContrat: transformFormData.typeContrat,
        dateDebut: transformFormData.dateDebut,
        dateFin: transformFormData.dateFin,
        prime: transformFormData.prime ? parseFloat(transformFormData.prime) : null,
        idCompagnie: transformFormData.idCompagnie ? parseInt(transformFormData.idCompagnie) : null,
        idTypeDuree: transformFormData.idTypeDuree ? parseInt(transformFormData.idTypeDuree) : null
      };
      
      console.log('📋 Contract data to send:', contractData);

      const result = await contractService.transformOpportunityToContract(selectedOpportunity.id, contractData, selectedDocuments);
      console.log('✅ Transformation successful, result:', result);
      
             setSuccessMessage('Opportunité transformée en contrat avec succès');
       setShowSuccess(true);
       setTransformModalOpen(false);
       setSelectedDocuments([]);
       await loadOpportunities(true); // Reset the list when transforming opportunity
    } catch (error) {
      console.error('❌ Error transforming opportunity:', error);
      console.error('❌ Error details:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        stack: error.stack
      });
      setErrorMessage(`Erreur lors de la transformation: ${error.message}`);
      setShowError(true);
    }
  };

  // Handle modal close
  const handleModalClose = () => {
    setAddModalOpen(false);
    setEditModalOpen(false);
    setSelectedOpportunity(null);
    setTransformModalOpen(false);
    setTransformFormData({
      typeContrat: 'Duree ferme',
      prime: '',
      dateDebut: '',
      dateFin: '',
      idCompagnie: '',
      idTypeDuree: ''
    });
    setSelectedDocuments([]);
  };

  // Handle success
  const handleSuccess = () => {
    loadOpportunities(true); // Reset the list when adding new opportunity
    handleModalClose();
  };

  // Handle search
  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
    setSkip(0);
  };

  // Handle filter change
  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
    setSkip(0);
  };

  // Handle refresh
  const handleRefresh = () => {
    setSkip(0);
    loadOpportunities(true);
  };

  // Clear filters
  const clearFilters = () => {
    setFilters({
      etape: '',
      origine: '',
      transformed: ''
    });
    setSearchTerm('');
    setSkip(0);
    loadOpportunities(true);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Toutes les Opportunités
      </Typography>
      
      {/* Search and Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
          <TextField
            label="Rechercher..."
            value={searchTerm}
                         onChange={handleSearch}
            size="small"
            sx={{ minWidth: 200 }}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
            }}
          />
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Étape</InputLabel>
            <Select
              value={filters.etape}
              onChange={(e) => handleFilterChange('etape', e.target.value)}
              label="Étape"
            >
              <MenuItem value="">Toutes</MenuItem>
              {filterOptions.etapes.map((etape) => (
                <MenuItem key={etape} value={etape}>{etape}</MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Origine</InputLabel>
            <Select
              value={filters.origine}
              onChange={(e) => handleFilterChange('origine', e.target.value)}
              label="Origine"
            >
              <MenuItem value="">Toutes</MenuItem>
              {filterOptions.origines.map((origine) => (
                <MenuItem key={origine} value={origine}>{origine}</MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Statut</InputLabel>
            <Select
              value={filters.transformed}
              onChange={(e) => handleFilterChange('transformed', e.target.value)}
              label="Statut"
            >
              <MenuItem value="">Tous</MenuItem>
              {filterOptions.transformedOptions.slice(1).map((option) => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <Button
            variant="outlined"
            onClick={clearFilters}
            startIcon={<CloseIcon />}
            size="small"
          >
            Effacer
          </Button>
          
          <Button
            variant="outlined"
                         onClick={handleRefresh}
            startIcon={<RefreshIcon />}
            size="small"
          >
            Actualiser
          </Button>
        </Stack>
        
        <Typography variant="body2" color="text.secondary">
          {filteredOpportunities.length} opportunité(s) trouvée(s) sur {totalCount} total
        </Typography>
      </Paper>

      {/* Add Opportunity Button */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddOpportunity}
        >
          Ajouter Opportunité
        </Button>
      </Box>

      {/* Opportunities Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Produit</TableCell>
              <TableCell>Client</TableCell>
              <TableCell>Origine</TableCell>
              <TableCell>Étape</TableCell>
              <TableCell>Date de Création</TableCell>
              <TableCell>Date d&apos;Échéance</TableCell>
              <TableCell>Budget</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : filteredOpportunities.length > 0 ? (
              filteredOpportunities.map((opp) => (
                <TableRow key={opp.id}>
                  <TableCell>
                    {opp.produit ? opp.produit.libelle : opp.idProduit || 'N/A'}
                  </TableCell>
                                     <TableCell>
                     {opp.client ? (
                       <Box>
                         <Typography variant="body2" fontWeight="medium">
                           {opp.client.nom || 'N/A'}
                         </Typography>
                         <Typography variant="caption" color="text.secondary">
                           {opp.client.typeClient}
                         </Typography>
                       </Box>
                     ) : 'N/A'}
                   </TableCell>
                  <TableCell>{opp.origine || 'N/A'}</TableCell>
                  <TableCell>
                    <Chip 
                      label={opp.etape || 'N/A'} 
                      size="small"
                      color={
                        opp.etape === 'Gagnée' ? 'success' :
                        opp.etape === 'Perdue' ? 'error' :
                        opp.etape === 'Proposition' ? 'warning' :
                        'default'
                      }
                    />
                  </TableCell>
                  <TableCell>{opp.dateCreation || 'N/A'}</TableCell>
                  <TableCell>{opp.dateEcheance || 'N/A'}</TableCell>
                  <TableCell>
                    {opp.budgetEstime ? `${opp.budgetEstime} DH` : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {opp.transformed ? (
                      <Box>
                        <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                          Transformée en contrat
                        </Typography>
                        {opp.dateTransformation && (
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                            {new Date(opp.dateTransformation).toLocaleDateString()}
                          </Typography>
                        )}
                        {opp.contract && (
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', fontSize: '0.75rem' }}>
                            Contrat #{opp.contract.numPolice}
                          </Typography>
                        )}
                      </Box>
                    ) : (
                      <>
                        <IconButton
                          size="small"
                          onClick={() => handleTransformOpportunity(opp.id)}
                          color="primary"
                          title="Transformer en contrat"
                        >
                          <TransformIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleEditOpportunity(opp)}
                          color="secondary"
                          title="Modifier l&apos;opportunité"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteOpportunity(opp.id)}
                          color="error"
                          title="Supprimer l&apos;opportunité"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </>
                    )}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  Aucune opportunité trouvée
                </TableCell>
              </TableRow>
                         )}
             
             {/* Loading row */}
             {loading && hasMore && (
               <TableRow>
                 <TableCell colSpan={8} align="center">
                   <CircularProgress size={24} />
                 </TableCell>
               </TableRow>
             )}
             
             {/* No more data row */}
             {!hasMore && opportunities.length > 0 && (
               <TableRow>
                 <TableCell colSpan={8} align="center">
                   <Typography variant="body2" color="text.secondary">
                     Fin de la liste
                   </Typography>
                 </TableCell>
               </TableRow>
             )}
           </TableBody>
         </Table>
       </TableContainer>

      {/* Add Opportunity Modal */}
      <AddOpportunityModal
        open={addModalOpen}
        onClose={handleModalClose}
        onSuccess={handleSuccess}
      />

      {/* Edit Opportunity Modal */}
      {selectedOpportunity && (
        <EditOpportunityModal
          open={editModalOpen}
          onClose={handleModalClose}
          onSuccess={handleSuccess}
          opportunityData={selectedOpportunity}
        />
      )}

      {/* Transform Opportunity Modal */}
      <Dialog open={transformModalOpen} onClose={() => setTransformModalOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Transformer l&apos;opportunité en contrat
            </Typography>
            <IconButton onClick={() => setTransformModalOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Produit: <strong>{selectedOpportunity?.produit?.libelle || 'N/A'}</strong>
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Type de contrat</InputLabel>
                  <Select
                    value={transformFormData.typeContrat}
                    onChange={(e) => setTransformFormData(prev => ({ ...prev, typeContrat: e.target.value }))}
                    label="Type de contrat"
                  >
                    <MenuItem value="Duree ferme">Durée ferme</MenuItem>
                    <MenuItem value="Duree campagne">Durée campagne</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Prime annuel (DH)"
                  type="number"
                  value={transformFormData.prime}
                  onChange={(e) => setTransformFormData(prev => ({ ...prev, prime: e.target.value }))}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">DH</InputAdornment>,
                  }}
                  sx={{ mb: 2 }}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Date de début"
                  type="date"
                  value={transformFormData.dateDebut}
                  onChange={(e) => setTransformFormData(prev => ({ ...prev, dateDebut: e.target.value }))}
                  InputLabelProps={{ shrink: true }}
                  required
                  sx={{ mb: 2 }}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Date de fin"
                  type="date"
                  value={transformFormData.dateFin}
                  onChange={(e) => setTransformFormData(prev => ({ ...prev, dateFin: e.target.value }))}
                  InputLabelProps={{ shrink: true }}
                  required
                  sx={{ mb: 2 }}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Compagnie</InputLabel>
                  <Select
                    value={transformFormData.idCompagnie}
                    onChange={(e) => setTransformFormData(prev => ({ ...prev, idCompagnie: e.target.value }))}
                    label="Compagnie"
                  >
                    <MenuItem value="">
                      <em>Sélectionner une compagnie</em>
                    </MenuItem>
                                         {companies.map((company) => (
                       <MenuItem key={company.id} value={company.id}>
                         {company.nom} ({company.codeCIE})
                       </MenuItem>
                     ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Type de durée</InputLabel>
                  <Select
                    value={transformFormData.idTypeDuree}
                    onChange={(e) => setTransformFormData(prev => ({ ...prev, idTypeDuree: e.target.value }))}
                    label="Type de durée"
                  >
                    <MenuItem value="">
                      <em>Sélectionner un type de durée</em>
                    </MenuItem>
                                         {durationTypes.map((duration) => (
                       <MenuItem key={duration.id} value={duration.id}>
                         {duration.libelle} ({duration.nbMois} mois)
                       </MenuItem>
                     ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                                 <Button
                   variant="outlined"
                   component="label"
                   startIcon={<FileUploadIcon />}
                   fullWidth
                   sx={{ mb: 2 }}
                 >
                   Importer document
                   <input
                     type="file"
                     hidden
                     accept=".pdf"
                     onChange={handleTransformDocumentUpload}
                   />
                 </Button>
                 {selectedDocuments.length === 0 ? (
                   <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                     Aucun document sélectionné
                   </Typography>
                 ) : (
                   <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 2 }}>
                     {selectedDocuments.map((doc, index) => (
                       <Chip
                         key={index}
                         label={doc.name}
                         onClick={() => handleTransformDocumentClick(doc)}
                         onDelete={() => removeTransformDocument(index)}
                         icon={<DescriptionIcon />}
                         sx={{ mb: 1, cursor: 'pointer' }}
                       />
                     ))}
                   </Stack>
                 )}
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setTransformModalOpen(false)} color="secondary">
            Annuler
          </Button>
          <Button onClick={handleTransformSubmit} variant="contained" color="primary">
            Transformer
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <Dialog open={deleteModalOpen} onClose={() => setDeleteModalOpen(false)}>
        <DialogTitle>Confirmer la suppression</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Êtes-vous sûr de vouloir supprimer cette opportunité ? 
            Cette action est irréversible.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteModalOpen(false)}>
            Annuler
          </Button>
          <Button onClick={confirmDelete} color="error" variant="contained">
            Supprimer
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Snackbar */}
      <Snackbar
        open={showSuccess}
        autoHideDuration={6000}
        onClose={() => setShowSuccess(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setShowSuccess(false)} severity="success" sx={{ width: '100%' }}>
          {successMessage}
        </Alert>
      </Snackbar>

      {/* Error Snackbar */}
      <Snackbar
        open={showError}
        autoHideDuration={6000}
        onClose={() => setShowError(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setShowError(false)} severity="error" sx={{ width: '100%' }}>
          {errorMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default OpportunitiesPage;
