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
  IconButton,
  CircularProgress,
  Alert,
  Stack,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  InputAdornment,
  Card,
  CardContent,
  Chip
} from '@mui/material';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  Description as DescriptionIcon,
  FileUpload as FileUploadIcon
} from '@mui/icons-material';
import { contractService } from '../../services/contractService';
import { produitService } from '../../services/produitService';
import { clientService } from '../../services/clientService';
import { documentService } from '../../services/documentService';


const ContractsPage = () => {
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [skip, setSkip] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  
  // Search and filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    typeContrat: '',
    idTypeDuree: ''
  });
  
  // Filter options
  const [filterOptions, setFilterOptions] = useState({
    typeContrats: ['Duree ferme', 'Duree campagne'],
    durees: [] // Will be loaded from service
  });

  // Modal states
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedContract, setSelectedContract] = useState(null);
  const [viewDocumentsModalOpen, setViewDocumentsModalOpen] = useState(false);
  const [selectedContractForDocuments, setSelectedContractForDocuments] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [durationTypes, setDurationTypes] = useState([]);
  const [contractDocuments, setContractDocuments] = useState([]);
  const [newContractDocuments, setNewContractDocuments] = useState([]);
  const [deletedContractDocuments, setDeletedContractDocuments] = useState([]);
  
  // Success message state
  const [successMessage, setSuccessMessage] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [showError, setShowError] = useState(false);

  const limit = 50;

  // Load contracts
  const loadContracts = useCallback(async (reset = false) => {
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
      
      const response = await contractService.getContracts(params);
      
      if (reset) {
        setContracts(response.contracts || response);
        setSkip(limit);
      } else {
        setContracts(prev => [...prev, ...(response.contracts || response)]);
        setSkip(prev => prev + limit);
      }
      
      setTotalCount(response.total_count || (response.contracts || response).length);
      setHasMore(response.has_more || (response.contracts || response).length >= limit);
    } catch (error) {
      console.error('Error loading contracts:', error);
      setErrorMessage('Erreur lors du chargement des contrats');
      setShowError(true);
    } finally {
      setLoading(false);
    }
  }, [skip, limit, searchTerm, filters]);

  useEffect(() => {
    loadContracts(true);
  }, [searchTerm, filters]);

  // Filter contracts based on search and filters
  const filteredContracts = contracts.filter(contract => {
    const matchesSearch = !searchTerm || 
      (contract.numPolice && contract.numPolice.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (contract.client?.nom && contract.client.nom.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (contract.client?.codeClient && contract.client.codeClient.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (contract.typeContrat && contract.typeContrat.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesTypeContrat = !filters.typeContrat || contract.typeContrat === filters.typeContrat;
    const matchesDuree = !filters.idTypeDuree || contract.idTypeDuree === filters.idTypeDuree;

    return matchesSearch && matchesTypeContrat && matchesDuree;
  });

  // Handle edit contract
  const handleEditContract = async (contract) => {
    setSelectedContract(contract);
    setEditModalOpen(true);
    
    // Load companies and duration types when opening the modal
    await loadCompanies();
    await loadDurationTypes();
    
    // Load existing documents for this contract
    try {
      const docs = await documentService.getDocumentsByEntity('contrat', contract.id);
      setContractDocuments(docs);
    } catch (error) {
      console.error('Error loading contract documents:', error);
      setContractDocuments([]);
    }
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

  // Document handling functions
  const handleDocumentClick = (document) => {
    try {
      console.log('📄 Document clicked:', document);
      console.log('📄 Document type:', typeof document);
      console.log('📄 Document keys:', Object.keys(document));
      
      // Check if this is a File object (new document) or a document record (existing document)
      if (document instanceof File) {
        // NEW DOCUMENT: This is a File object from file input
        console.log('📄 New document File object detected:', document.name);
        
        // Create a temporary URL for the file
        const fileUrl = URL.createObjectURL(document);
        console.log('📄 Created blob URL for new document:', fileUrl);
        
        // Open the file in a new window/tab
        const newWindow = window.open(fileUrl, '_blank');
        if (!newWindow) {
          console.error('❌ Failed to open document window');
          alert('Impossible d\'ouvrir le document dans une nouvelle fenêtre. Vérifiez les bloqueurs de popup.');
        } else {
          console.log('✅ New document window opened successfully');
        }
        
        // Clean up the URL after a delay
        setTimeout(() => URL.revokeObjectURL(fileUrl), 1000);
        return;
      }
      
      // EXISTING DOCUMENT: This is a document record from the database
      console.log('📄 Existing document record detected');
      console.log('📄 Document.fichierChemin:', document.fichierChemin);
      console.log('📄 Document.fichierNom:', document.fichierNom);
      
      // Check if this is a document with an actual file or just a reference
      if (document.fichierChemin && document.fichierChemin.trim() !== '') {
        // Check if this looks like a file path (has file extension)
        const hasFileExtension = /\.(pdf|doc|docx|xls|xlsx|txt|csv|jpg|jpeg|png|gif)$/i.test(document.fichierChemin);
        
        if (!hasFileExtension) {
          // This is likely a reference document (like CSV import) without an actual file
          console.log('📄 Document appears to be a reference without an actual file:', document.fichierChemin);
          alert(`Ce document est une référence (${document.fichierNom || 'N/A'}) et ne contient pas de fichier téléchargeable.\n\nType: Référence\nChemin: ${document.fichierChemin || 'N/A'}`);
          return;
        }
        
        // Check if this is an old format document and handle it properly
        let fileUrl;
        if (document.fichierChemin.startsWith('uploads/')) {
          // OLD FORMAT: extract the filename and try to find a matching UUID file
          const filename = document.fichierChemin.replace('uploads/', '');
          console.log('📄 Document has old format, extracted filename:', filename);
          
          // For now, show an error asking user to re-upload
          alert(`Ce document utilise un ancien format de stockage qui n'est plus supporté.\n\nNom: ${document.fichierNom}\nChemin: ${document.fichierChemin}\n\nVeuillez supprimer ce document et le télécharger à nouveau pour le corriger.`);
          return;
        } else {
          // NEW FORMAT: use UUID filename directly
          fileUrl = `${window.location.origin}/api/documents/files/${encodeURIComponent(document.fichierChemin)}`;
          console.log('📄 Opening document with UUID filename:', fileUrl);
          console.log('📄 Document path:', document.fichierChemin);
        }
        
        // Try to open the document in a new tab
        console.log('📄 Attempting to open document URL:', fileUrl);
        const newWindow = window.open(fileUrl, '_blank');
        if (!newWindow) {
          console.error('❌ Failed to open document window');
          alert('Impossible d\'ouvrir le document dans une nouvelle fenêtre. Vérifiez les bloqueurs de popup.');
        } else {
          console.log('✅ Document window opened successfully');
        }
      } else {
        console.error('❌ Document has no fichierChemin or empty path:', document);
        console.error('❌ Document data:', JSON.stringify(document, null, 2));
        alert(`Document non disponible - chemin manquant\nNom: ${document.fichierNom || 'N/A'}\nChemin: ${document.fichierChemin || 'N/A'}\nID: ${document.id || 'N/A'}\n\nCe document n&apos;a pas de fichier associé.`);
      }
    } catch (error) {
      console.error('❌ Error opening document:', error);
      alert(`Erreur lors de l'ouverture du document:\n${error.message}\n\nVérifiez que le fichier existe sur le serveur.`);
    }
  };

  const handleContractDocumentUpload = (event) => {
    const files = Array.from(event.target.files);
    const pdfFiles = files.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length !== files.length) {
      alert('Seuls les fichiers PDF sont acceptés');
      return;
    }
    
    // Add new files to newContractDocuments (not to contractDocuments)
    setNewContractDocuments(prev => [...prev, ...pdfFiles]);
    setSuccessMessage('Documents ajoutés (seront sauvegardés lors de la confirmation)');
    setShowSuccess(true);
  };

  const removeContractDocument = (index, isNew = false) => {
    if (isNew) {
      // Remove from new documents
      setNewContractDocuments(prev => prev.filter((_, i) => i !== index));
    } else {
      // Mark existing document for deletion
      const doc = contractDocuments[index];
      if (doc && doc.id) {
        setDeletedContractDocuments(prev => [...prev, doc.id]);
      }
      // Remove from display
      setContractDocuments(prev => prev.filter((_, i) => i !== index));
    }
    setSuccessMessage('Document supprimé');
    setShowSuccess(true);
  };

  // Handle view contract documents
  const handleViewContractDocuments = async (contract) => {
    setSelectedContractForDocuments(contract);
    try {
      // Load documents for this contract
      const docs = await documentService.getDocumentsByEntity('contrat', contract.id);
      setContractDocuments(docs);
      setViewDocumentsModalOpen(true);
    } catch (error) {
      console.error('Error loading contract documents:', error);
      setErrorMessage('Erreur lors du chargement des documents');
      setShowError(true);
    }
  };

  // Handle modal close
  const handleModalClose = () => {
    setEditModalOpen(false);
    setSelectedContract(null);
    setViewDocumentsModalOpen(false);
    setSelectedContractForDocuments(null);
    // Clear all contract-related states when canceling
    setContractDocuments([]);
    setNewContractDocuments([]);
    setDeletedContractDocuments([]);
  };

  // Handle success
  const handleSuccess = async () => {
    try {
      if (!selectedContract) return;
      
      // Prepare contract data for update
      const updateData = {
        numPolice: selectedContract.numPolice,
        typeContrat: selectedContract.typeContrat,
        dateDebut: selectedContract.dateDebut,
        dateFin: selectedContract.dateFin,
        prime: selectedContract.prime ? parseFloat(selectedContract.prime) : null,
        idCompagnie: selectedContract.idCompagnie ? parseInt(selectedContract.idCompagnie) : null,
        idTypeDuree: selectedContract.idTypeDuree ? parseInt(selectedContract.idTypeDuree) : null
      };
      
      // Update contract via API
      await contractService.updateContract(selectedContract.id, updateData);
      
      // Handle document deletions
      for (const docId of deletedContractDocuments) {
        try {
          await documentService.deleteDocument(docId);
        } catch (error) {
          console.error(`Error deleting document ${docId}:`, error);
        }
      }
      
      // Handle new document uploads
      for (const file of newContractDocuments) {
        try {
          const formData = new FormData();
          formData.append('file', file);
          formData.append('client_id', selectedContract.idClient);
          formData.append('entity_type', 'contrat');
          formData.append('entity_id', selectedContract.id);
          
          // Upload document directly linked to contract
          const uploadedDoc = await documentService.uploadDocument(formData);
          
          console.log(`✅ Document ${file.name} uploaded and linked successfully to contract ${selectedContract.id}`);
        } catch (error) {
          console.error(`Error uploading document ${file.name}:`, error);
          setErrorMessage(`Erreur lors de l'upload du document ${file.name}: ${error.message}`);
          setShowError(true);
        }
      }
      
      setSuccessMessage('Contrat modifié avec succès');
      setShowSuccess(true);
      await loadContracts(true); // Reset the list when updating contract
      handleModalClose();
      
      // Reset document states
      setContractDocuments([]);
      setNewContractDocuments([]);
      setDeletedContractDocuments([]);
    } catch (error) {
      console.error('Error updating contract:', error);
      setErrorMessage('Erreur lors de la modification du contrat');
      setShowError(true);
    }
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
    loadContracts(true);
  };

  // Clear filters
  const clearFilters = () => {
    setFilters({
      typeContrat: '',
      idTypeDuree: ''
    });
    setSearchTerm('');
    setSkip(0);
    loadContracts(true);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Tous les Contrats
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
            <InputLabel>Type Contrat</InputLabel>
            <Select
              value={filters.typeContrat}
              onChange={(e) => handleFilterChange('typeContrat', e.target.value)}
              label="Type Contrat"
            >
              <MenuItem value="">Tous</MenuItem>
              {filterOptions.typeContrats.map((type) => (
                <MenuItem key={type} value={type}>{type}</MenuItem>
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
          {filteredContracts.length} contrat(s) trouvé(s) sur {totalCount} total
        </Typography>
      </Paper>



      {/* Contracts Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Numéro Police</TableCell>
              <TableCell>Client</TableCell>
              <TableCell>Type Contrat</TableCell>
              <TableCell>Type Durée</TableCell>
              <TableCell>Date Début</TableCell>
              <TableCell>Date Fin</TableCell>
              <TableCell>Prime Annuel</TableCell>
              <TableCell>Compagnie</TableCell>
              <TableCell>Produit</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={10} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : filteredContracts.length > 0 ? (
              filteredContracts.map((contract) => (
                <TableRow key={contract.id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {contract.numPolice || 'N/A'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {contract.client ? (
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {contract.client.nom || 'N/A'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {contract.client.typeClient}
                        </Typography>
                      </Box>
                    ) : 'N/A'}
                  </TableCell>
                  <TableCell>{contract.typeContrat || 'N/A'}</TableCell>
                  <TableCell>
                    {contract.duree ? contract.duree.libelle : 'N/A'}
                  </TableCell>
                  <TableCell>{contract.dateDebut || 'N/A'}</TableCell>
                  <TableCell>{contract.dateFin || 'N/A'}</TableCell>
                  <TableCell>
                    {contract.prime ? `${contract.prime} DH` : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {contract.compagnie ? contract.compagnie.nom : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {contract.produit ? contract.produit.libelle : contract.idProduit || 'N/A'}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleEditContract(contract)}
                      color="primary"
                      title="Modifier"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleViewContractDocuments(contract)}
                      color="info"
                      title="Voir les documents"
                    >
                      <VisibilityIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={10} align="center">
                  Aucun contrat trouvé
                </TableCell>
              </TableRow>
                         )}
             
                           {/* Loading row */}
              {loading && hasMore && (
                <TableRow>
                  <TableCell colSpan={10} align="center">
                    <CircularProgress size={24} />
                  </TableCell>
                </TableRow>
              )}
              
              {/* No more data row */}
              {!hasMore && contracts.length > 0 && (
                <TableRow>
                  <TableCell colSpan={10} align="center">
                    <Typography variant="body2" color="text.secondary">
                      Fin de la liste
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
           </TableBody>
         </Table>
       </TableContainer>



      {/* Edit Contract Modal */}
      <Dialog 
        open={editModalOpen} 
        onClose={() => {
          setEditModalOpen(false);
          setSelectedContract(null);
        }}
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>Modifier le contrat</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Numéro Police"
                  value={selectedContract?.numPolice || ''}
                  onChange={(e) => setSelectedContract(prev => ({ ...prev, numPolice: e.target.value }))}
                  size="small"
                  sx={{ mb: 2 }}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                  <InputLabel>Type Contrat</InputLabel>
                  <Select
                    value={selectedContract?.typeContrat || ''}
                    onChange={(e) => setSelectedContract(prev => ({ ...prev, typeContrat: e.target.value }))}
                    label="Type Contrat"
                  >
                    <MenuItem value="Duree ferme">Durée ferme</MenuItem>
                    <MenuItem value="Duree campagne">Durée campagne</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Date de début"
                  type="date"
                  value={selectedContract?.dateDebut || ''}
                  onChange={(e) => setSelectedContract(prev => ({ ...prev, dateDebut: e.target.value }))}
                  InputLabelProps={{ shrink: true }}
                  size="small"
                  sx={{ mb: 2 }}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Date de fin"
                  type="date"
                  value={selectedContract?.dateFin || ''}
                  onChange={(e) => setSelectedContract(prev => ({ ...prev, dateFin: e.target.value }))}
                  InputLabelProps={{ shrink: true }}
                  size="small"
                  sx={{ mb: 2 }}
                />
              </Grid>
              
                             <Grid item xs={12} md={6}>
                 <TextField
                   fullWidth
                   label="Prime annuel (DH)"
                   type="number"
                   value={selectedContract?.prime || ''}
                   onChange={(e) => setSelectedContract(prev => ({ ...prev, prime: e.target.value }))}
                   size="small"
                   InputProps={{
                     endAdornment: <InputAdornment position="end">DH</InputAdornment>,
                   }}
                   sx={{ mb: 2 }}
                 />
               </Grid>
               
               <Grid item xs={12} md={6}>
                 <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                   <InputLabel>Compagnie</InputLabel>
                   <Select
                     value={selectedContract?.idCompagnie || ''}
                     onChange={(e) => setSelectedContract(prev => ({ ...prev, idCompagnie: e.target.value }))}
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
                 <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                   <InputLabel>Type de durée</InputLabel>
                   <Select
                     value={selectedContract?.idTypeDuree || ''}
                     onChange={(e) => setSelectedContract(prev => ({ ...prev, idTypeDuree: e.target.value }))}
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
               
               {/* Document Management Section */}
               <Grid item xs={12}>
                 <Typography variant="h6" sx={{ mb: 2, mt: 2 }}>Documents</Typography>
                 
                 {/* Existing Documents */}
                 {contractDocuments.length > 0 && (
                   <>
                     <Typography variant="subtitle2" sx={{ mb: 1 }}>Documents existants:</Typography>
                     <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 2 }}>
                       {contractDocuments.map((doc, index) => (
                         <Chip
                           key={index}
                           label={doc.fichierNom || doc.name || `Document ${index + 1}`}
                           onClick={() => handleDocumentClick(doc)}
                           onDelete={() => removeContractDocument(index, false)}
                           icon={<DescriptionIcon />}
                           sx={{ mb: 1, cursor: 'pointer' }}
                         />
                       ))}
                     </Stack>
                   </>
                 )}
                 
                 {/* New Documents */}
                 {newContractDocuments.length > 0 && (
                   <>
                     <Typography variant="subtitle2" sx={{ mb: 1, mt: 2 }}>Nouveaux documents:</Typography>
                     <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 2 }}>
                       {newContractDocuments.map((doc, index) => (
                         <Chip
                           key={`new-${index}`}
                           label={doc.name}
                           onClick={() => handleDocumentClick(doc)}
                           onDelete={() => removeContractDocument(index, true)}
                           icon={<DescriptionIcon />}
                           sx={{ mb: 1, cursor: 'pointer' }}
                         />
                       ))}
                     </Stack>
                   </>
                 )}
                 
                 {/* Document Upload */}
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
                     onChange={handleContractDocumentUpload}
                   />
                 </Button>
                 
                 {/* No Documents Message */}
                 {contractDocuments.length === 0 && newContractDocuments.length === 0 && (
                   <Typography variant="body2" color="text.secondary">
                     Aucun document
                   </Typography>
                 )}
               </Grid>
             </Grid>
           </Box>
         </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setEditModalOpen(false)} color="secondary">
            Annuler
          </Button>
          <Button onClick={handleSuccess} variant="contained" color="primary">
            Confirmer
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Contract Documents Modal */}
      <Dialog open={viewDocumentsModalOpen} onClose={() => {
        setViewDocumentsModalOpen(false);
        setSelectedContractForDocuments(null);
        setContractDocuments([]);
      }} maxWidth="md" fullWidth>
        <DialogTitle>Documents du contrat</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            {contractDocuments.length === 0 ? (
              <Typography variant="body2" color="text.secondary" align="center">
                Aucun document trouvé pour ce contrat
              </Typography>
            ) : (
              <Grid container spacing={2}>
                {contractDocuments.map((doc, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card 
                      sx={{ 
                        cursor: 'pointer',
                        '&:hover': { boxShadow: 3 }
                      }}
                                             onClick={() => handleDocumentClick(doc)}
                    >
                      <CardContent sx={{ textAlign: 'center', p: 2 }}>
                        <DescriptionIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
                        <Typography variant="body2" noWrap>
                          {doc.fichierNom || doc.name || `Document ${index + 1}`}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Cliquez pour voir
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setViewDocumentsModalOpen(false)} color="primary">
            Fermer
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

export default ContractsPage;
