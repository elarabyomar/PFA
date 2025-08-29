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
  DialogContentText
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { clientService } from '../../services/clientService';
import { documentService } from '../../services/documentService';
import StarRating from '../../components/common/StarRating';
import ClientTypeModal from '../../components/clients/ClientTypeModal';
import ClientInfoModal from '../../components/clients/ClientInfoModal';
import ClientDetailsModal from '../../components/clients/ClientDetailsModal';

const ClientsPage = () => {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [skip, setSkip] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  
  // Search and filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    typeClient: '',
    importance: ''
  });
  
  // Filter options
  const [filterOptions, setFilterOptions] = useState({
    types: [],
    importanceLevels: []
  });

  // Modal states
  const [typeModalOpen, setTypeModalOpen] = useState(false);
  const [infoModalOpen, setInfoModalOpen] = useState(false);
  const [selectedClientType, setSelectedClientType] = useState(null);
  const [detailsModalOpen, setDetailsModalOpen] = useState(false);
  const [selectedClientId, setSelectedClientId] = useState(null);
  
  // Delete confirmation modal state
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [clientToDelete, setClientToDelete] = useState(null);
  
  // Success message state
  const [successMessage, setSuccessMessage] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [showError, setShowError] = useState(false);

  const limit = 50;

  // Load filter options
  useEffect(() => {
    const loadFilterOptions = async () => {
      try {
        const [types, importanceLevels] = await Promise.all([
          clientService.getClientTypes(),
          clientService.getClientImportanceLevels()
        ]);
        
        setFilterOptions({
          types,
          importanceLevels
        });
      } catch (error) {
        console.error('Error loading filter options:', error);
      }
    };
    
    loadFilterOptions();
  }, []);

  // Load clients
  const loadClients = useCallback(async (reset = false) => {
    try {
      console.log(`🔄 loadClients called with reset=${reset}, skip=${skip}, searchTerm="${searchTerm}"`);
      setLoading(true);
      
      const currentSkip = reset ? 0 : skip;
      const params = {
        skip: currentSkip,
        limit,
        search: searchTerm,
        ...filters
      };
      
      const response = await clientService.getClients(params);
      console.log('API Response:', response);
      console.log('Clients data:', response.clients);
      
      // Filter out associated clients (clients that are linked to other clients)
      const filteredClients = response.clients.filter(client => !client.isAssociated);
      console.log('Filtered clients (excluding associated):', filteredClients);
      
      if (reset) {
        setClients(filteredClients);
        setSkip(limit);
      } else {
        setClients(prev => [...prev, ...filteredClients]);
        setSkip(prev => prev + limit);
      }
      
      // Adjust total count to reflect filtered results
      const adjustedTotalCount = Math.max(0, response.total_count - (response.clients.length - filteredClients.length));
      setTotalCount(adjustedTotalCount);
      setHasMore(response.has_more && filteredClients.length > 0);
      console.log(`✅ loadClients completed: ${filteredClients.length} clients loaded, adjusted_total_count=${adjustedTotalCount}`);
    } catch (error) {
      console.error('Error loading clients:', error);
    } finally {
      setLoading(false);
    }
  }, [skip, searchTerm, filters]);

  // Initial load
  useEffect(() => {
    loadClients(true);
  }, [searchTerm, filters]);

  // Handle search
  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
    setSkip(0);
  };

  // Handle filter change
  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
    setSkip(0);
  };

  // Handle refresh
  const handleRefresh = () => {
    setSkip(0);
    loadClients(true);
  };

  // Handle add client button click
  const handleAddClient = () => {
    setTypeModalOpen(true);
  };

  // Handle client type selection
  const handleClientTypeSelect = (type) => {
    setSelectedClientType(type);
    setInfoModalOpen(true);
  };

    // Handle client info submission
  const handleClientSubmit = async (clientData) => {
    try {
      console.log('Client data to submit:', clientData);
      console.log('Client data type:', typeof clientData);
      console.log('Client data keys:', Object.keys(clientData));
      
      // Log specific problematic fields
      if (clientData.dateNaissance) console.log('dateNaissance:', clientData.dateNaissance, typeof clientData.dateNaissance);
      if (clientData.date_deces) console.log('date_deces:', clientData.date_deces, typeof clientData.date_deces);
      if (clientData.datePermis) console.log('datePermis:', clientData.datePermis, typeof clientData.datePermis);
      if (clientData.dateCreationSociete) console.log('dateCreationSociete:', clientData.dateCreationSociete, typeof clientData.dateCreationSociete);
      
      // Call the API to create the client
      const result = await documentService.createClientWithDocuments(clientData);
      console.log('Client created successfully:', result);
      
      // Close the modal
      setInfoModalOpen(false);
      setSelectedClientType(null);
      
      // Show success message
      setSuccessMessage('Client créé avec succès!');
      setShowSuccess(true);
      
      // Refresh the clients list without resetting filters
      loadClients(true);
      
    } catch (error) {
      console.error('Error creating client:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        stack: error.stack
      });
      // Re-throw the error so the modal can catch and display it
      throw error;
    }
  };

  // Handle modal close
  const handleInfoModalClose = () => {
    setInfoModalOpen(false);
    setSelectedClientType(null);
  };

  // Handle client row click
  const handleClientRowClick = (clientId) => {
    console.log('🖱️ Client row clicked, ID:', clientId);
    setSelectedClientId(clientId);
    setDetailsModalOpen(true);
    console.log('✅ Modal state updated:', { selectedClientId: clientId, detailsModalOpen: true });
  };

  // Handle details modal close
  const handleDetailsModalClose = () => {
    setDetailsModalOpen(false);
    setSelectedClientId(null);
  };

  // Handle delete client
  const handleDeleteClient = async (clientId, event) => {
    event.stopPropagation(); // Prevent row click
    setClientToDelete(clientId);
    setDeleteModalOpen(true);
  };

  // Handle delete confirmation
  const handleConfirmDelete = async () => {
    if (!clientToDelete) return;
    console.log(`🗑️ handleConfirmDelete called for client ${clientToDelete}`);
    try {
      console.log(`🔄 Calling clientService.deleteClient(${clientToDelete})`);
      const result = await clientService.deleteClient(clientToDelete);
      console.log(`✅ Delete result:`, result);
      
      setSuccessMessage('Client supprimé avec succès');
      setShowSuccess(true);
      
      console.log(`🔄 Refreshing client list...`);
      await loadClients(true); // Refresh the list
      console.log(`✅ Client list refreshed`);
    } catch (error) {
      console.error(`❌ Error deleting client ${clientToDelete}:`, error);
      console.error(`❌ Error details:`, error.response?.data);
      console.error(`❌ Error status:`, error.response?.status);
      setErrorMessage('Erreur lors de la suppression du client');
      setShowError(true);
    } finally {
      console.log(`🔄 Closing delete modal and resetting state`);
      setDeleteModalOpen(false);
      setClientToDelete(null);
    }
  };

  // Handle delete cancellation
  const handleCancelDelete = () => {
    setDeleteModalOpen(false);
    setClientToDelete(null);
  };

  // Handle infinite scroll
  const handleScroll = useCallback((event) => {
    const { scrollTop, scrollHeight, clientHeight } = event.target;
    if (scrollTop + clientHeight >= scrollHeight - 100 && !loading && hasMore) {
      loadClients();
    }
  }, [loading, hasMore, loadClients]);

  // Format budget
  const formatBudget = (budget) => {
    if (!budget) return '0 DH';
    try {
      const num = parseFloat(budget);
      return isNaN(num) ? budget : `${num.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} DH`;
    } catch {
      return budget;
    }
  };

  // Format probability
  const formatProba = (proba) => {
    if (!proba) return '0%';
    try {
      const num = parseFloat(proba);
      return isNaN(num) ? proba : `${num.toFixed(1)}%`;
    } catch {
      return proba;
    }
  };

  // Parse importance to number for star rating
  const parseImportance = (importance) => {
    if (!importance) return 0;
    try {
      return parseFloat(importance);
    } catch {
      return 0;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Gestion des Clients
      </Typography>

      {/* Search and Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
          <TextField
            label="Rechercher par nom"
            value={searchTerm}
            onChange={handleSearch}
            placeholder="Rechercher..."
            size="small"
            sx={{ minWidth: 300 }}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
            }}
          />
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Type Client</InputLabel>
            <Select
              value={filters.typeClient}
              onChange={(e) => handleFilterChange('typeClient', e.target.value)}
              label="Type Client"
            >
              <MenuItem value="">Tous</MenuItem>
              {filterOptions.types.map((type) => (
                <MenuItem key={type} value={type}>{type}</MenuItem>
              ))}
            </Select>
          </FormControl>



          <Box sx={{ minWidth: 150 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Importance
            </Typography>
            <StarRating
              value={parseFloat(filters.importance) || 0}
              onChange={(value) => handleFilterChange('importance', value.toString())}
              readOnly={false}
              size="small"
              showHalfStars={true}
            />
            {filters.importance && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  {filters.importance} étoile{parseFloat(filters.importance) > 1 ? 's' : ''}
                </Typography>
                <IconButton 
                  size="small" 
                  onClick={() => handleFilterChange('importance', '')}
                  sx={{ p: 0.5 }}
                >
                  <CloseIcon fontSize="small" />
                </IconButton>
              </Box>
            )}
          </Box>

          <IconButton onClick={handleRefresh} color="primary">
            <RefreshIcon />
          </IconButton>
        </Stack>

        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="body2" color="text.secondary">
            {totalCount} client(s) trouvé(s)
          </Typography>
          
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddClient}
            sx={{ 
              minWidth: 150,
              backgroundColor: 'green',
              color: 'white',
              '&:hover': {
                backgroundColor: '#005000',
                color: 'white'
              }
            }}
          >
            Ajouter Client
          </Button>
        </Stack>
      </Paper>

             {/* Error Alert - Removed since errors are now handled in the modal */}

      {/* Clients Table */}
      <Paper>
        <TableContainer 
          sx={{ maxHeight: 'calc(100vh - 300px)' }}
          onScroll={handleScroll}
        >
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Nom</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Type</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Téléphone</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Email</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Budget</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Réalisation</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Importance</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {clients.map((client) => (
                <TableRow 
                  key={client.id} 
                  hover 
                  onClick={() => handleClientRowClick(client.id)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {client.nom || 'N/A'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={client.typeClient} 
                      size="small"
                      color={client.typeClient === 'PARTICULIER' ? 'primary' : 'secondary'}
                    />
                  </TableCell>
                  <TableCell>{client.tel || '-'}</TableCell>
                  <TableCell>{client.email || '-'}</TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {formatBudget(client.budget)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {formatProba(client.proba)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <StarRating 
                      value={parseImportance(client.importance)} 
                      readOnly={true}
                      size="small"
                      showHalfStars={true}
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={(e) => handleDeleteClient(client.id, e)}
                      color="error"
                      title="Supprimer le client"
                      sx={{ 
                        color: 'red',
                        '&:hover': {
                          backgroundColor: 'rgba(244, 67, 54, 0.1)',
                          color: '#d32f2f'
                        }
                      }}
                    >
                      ✕
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              
              {/* Loading row */}
              {loading && (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <CircularProgress size={24} />
                  </TableCell>
                </TableRow>
              )}
              
              {/* No more data row */}
              {!hasMore && clients.length > 0 && (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography variant="body2" color="text.secondary">
                      Aucun autre client à charger
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
              
              {/* Empty state */}
              {!loading && clients.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography variant="body2" color="text.secondary">
                      Aucun client trouvé
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Client Type Selection Modal */}
      <ClientTypeModal
        open={typeModalOpen}
        onClose={() => setTypeModalOpen(false)}
        onTypeSelect={handleClientTypeSelect}
      />

             {/* Client Info Form Modal */}
               <ClientInfoModal
          open={infoModalOpen}
          onClose={handleInfoModalClose}
          clientType={selectedClientType}
          onSubmit={handleClientSubmit}
          onCancel={handleInfoModalClose}
        />

        {/* Client Details Modal */}
        <ClientDetailsModal
          open={detailsModalOpen}
          onClose={handleDetailsModalClose}
          clientId={selectedClientId}
          onClientUpdated={() => {
            console.log('🔄 onClientUpdated callback triggered - refreshing clients table...');
            setSkip(0); // Reset pagination to start
            loadClients(true); // Load from beginning with reset=true
          }}
          onRefreshMainTable={() => {
            console.log('🔄 onRefreshMainTable callback triggered - refreshing clients table...');
            setSkip(0); // Reset pagination to start
            loadClients(true); // Load from beginning with reset=true
          }}
        />
       
               {/* Success Message Snackbar */}
        <Snackbar
          open={showSuccess}
          autoHideDuration={3000}
          onClose={() => setShowSuccess(false)}
          message={successMessage}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          sx={{
            zIndex: 9999, // Ensure it appears above everything
            '& .MuiSnackbarContent-root': {
              backgroundColor: '#4caf50',
              color: 'white',
              fontWeight: 'bold'
            }
          }}
        />

        {/* Error Message Snackbar */}
        <Snackbar
          open={showError}
          autoHideDuration={3000}
          onClose={() => setShowError(false)}
          message={errorMessage}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          sx={{
            zIndex: 9999,
            '& .MuiSnackbarContent-root': {
              backgroundColor: '#f44336',
              color: 'white',
              fontWeight: 'bold'
            }
          }}
        />

        {/* Delete Confirmation Dialog */}
        <Dialog
          open={deleteModalOpen}
          onClose={handleCancelDelete}
          aria-labelledby="delete-dialog-title"
          aria-describedby="delete-dialog-description"
        >
          <DialogTitle id="delete-dialog-title">Confirmation de suppression</DialogTitle>
          <DialogContent>
            <DialogContentText id="delete-dialog-description">
              Êtes-vous sûr de vouloir supprimer ce client ? Cette action est irréversible.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCancelDelete} color="primary">
              Annuler
            </Button>
            <Button onClick={handleConfirmDelete} color="error" variant="contained">
              Supprimer
            </Button>
          </DialogActions>
        </Dialog>
     </Box>
   );
 };

export default ClientsPage;
