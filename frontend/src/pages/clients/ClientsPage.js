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
  Stack
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { clientService } from '../../services/clientService';
import StarRating from '../../components/common/StarRating';

const ClientsPage = () => {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const [skip, setSkip] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  
  // Search and filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    typeClient: '',
    statut: '',
    importance: ''
  });
  
  // Filter options
  const [filterOptions, setFilterOptions] = useState({
    types: [],
    statuts: [],
    importanceLevels: []
  });

  const limit = 50;

  // Load filter options
  useEffect(() => {
    const loadFilterOptions = async () => {
      try {
        const [types, statuts, importanceLevels] = await Promise.all([
          clientService.getClientTypes(),
          clientService.getClientStatuts(),
          clientService.getClientImportanceLevels()
        ]);
        
        setFilterOptions({
          types,
          statuts,
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
      setLoading(true);
      setError(null);
      
      const currentSkip = reset ? 0 : skip;
      const params = {
        skip: currentSkip,
        limit,
        search: searchTerm,
        ...filters
      };
      
      const response = await clientService.getClients(params);
      
      if (reset) {
        setClients(response.clients);
        setSkip(limit);
      } else {
        setClients(prev => [...prev, ...response.clients]);
        setSkip(prev => prev + limit);
      }
      
      setTotalCount(response.total_count);
      setHasMore(response.has_more);
    } catch (error) {
      setError('Erreur lors du chargement des clients');
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

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Statut</InputLabel>
            <Select
              value={filters.statut}
              onChange={(e) => handleFilterChange('statut', e.target.value)}
              label="Statut"
            >
              <MenuItem value="">Tous</MenuItem>
              {filterOptions.statuts.map((statut) => (
                <MenuItem key={statut} value={statut}>{statut}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Importance</InputLabel>
            <Select
              value={filters.importance}
              onChange={(e) => handleFilterChange('importance', e.target.value)}
              label="Importance"
            >
              <MenuItem value="">Toutes</MenuItem>
              {filterOptions.importanceLevels.map((level) => (
                <MenuItem key={level} value={level}>{level}</MenuItem>
              ))}
            </Select>
          </FormControl>

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
            color="success"
            startIcon={<AddIcon />}
            sx={{ minWidth: 150 }}
          >
            Ajouter Client
          </Button>
        </Stack>
      </Paper>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Clients Table */}
      <Paper>
        <TableContainer 
          sx={{ maxHeight: 'calc(100vh - 300px)' }}
          onScroll={handleScroll}
        >
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>NOM</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>TYPE</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>TEL</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>EMAIL</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>BUDGET</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>PROBA</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>IMPORTANCE</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {clients.map((client) => (
                <TableRow key={client.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {client.nom}
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
                    />
                  </TableCell>
                </TableRow>
              ))}
              
              {/* Loading row */}
              {loading && (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <CircularProgress size={24} />
                  </TableCell>
                </TableRow>
              )}
              
              {/* No more data row */}
              {!hasMore && clients.length > 0 && (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography variant="body2" color="text.secondary">
                      Aucun autre client à charger
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
              
              {/* Empty state */}
              {!loading && clients.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} align="center">
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
    </Box>
  );
};

export default ClientsPage;
