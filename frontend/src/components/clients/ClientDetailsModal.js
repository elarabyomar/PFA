import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  IconButton,
  Stack,
  Button,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert,
  Snackbar,
  CircularProgress,
  InputAdornment,
  Card,
  CardContent,
  CardActions
} from '@mui/material';
import {
  Close as CloseIcon,
  Edit as EditIcon,
  Check as CheckIcon,
  Add as AddIcon,
  Transform as TransformIcon,
  PersonAdd as PersonAddIcon,
  Remove as RemoveIcon,
  Upload as UploadIcon,
  Description as DescriptionIcon,
  Visibility as VisibilityIcon,
  Delete as DeleteIcon,
  FileUpload as FileUploadIcon
} from '@mui/icons-material';
import { clientService } from '../../services/clientService';
import { opportunityService } from '../../services/opportunityService';
import { contractService } from '../../services/contractService';
import { clientRelationService } from '../../services/clientRelationService';
import { adherentService } from '../../services/adherentService';


import { documentService } from '../../services/documentService';
import StarRating from '../common/StarRating';
import AddOpportunityModal from './AddOpportunityModal';
import AddAssociateModal from './AddAssociateModal';
import AddAdherentModal from './AddAdherentModal';
import EditOpportunityModal from './EditOpportunityModal';

const ClientDetailsModal = ({ 
  open, 
  onClose, 
  clientId,
  onClientUpdated,
  onRefreshMainTable 
}) => {
  const [clientDetails, setClientDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [opportunities, setOpportunities] = useState([]);
  const [contracts, setContracts] = useState([]);
  const [relations, setRelations] = useState([]);
  const [typeRelations, setTypeRelations] = useState([]);
  const [successMessage, setSuccessMessage] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [showError, setShowError] = useState(false);

  // Form data for editing - restructured to match ClientInfoModal
  const [formData, setFormData] = useState({
    // Client fields
    codeClient: '',
    adresse: '',
    tel: '',
    email: '',
    importance: '0',
    budget: '',
    proba: '',
    typeClient: '',
    
    // Particulier fields
    particulier: {
      titre: '',
      nom: '',
      prenom: '',
      sexe: '',
      nationalite: '',
      lieuNaissance: '',
      dateNaissance: '',
      date_deces: '',
      datePermis: '',
      cin: '',
      profession: '',
      typeDocIdentite: '',
      situationFamiliale: '',
      nombreEnfants: '',
      moyenContactPrefere: '',
      optoutTelephone: false,
      optoutEmail: false
    },
    
    // Societe fields
    societe: {
      nom: '',
      formeJuridique: '',
      capital: '',
      registreCom: '',
      taxePro: '',
      idFiscal: '',
      CNSS: '',
      ICE: '',
      siteWeb: '',
      societeMere: '',
      raisonSociale: '',
      sigle: '',
      tribunalCommerce: '',
      secteurActivite: '',
      dateCreationSociete: '',
      nomContactPrincipal: '',
      fonctionContactPrincipal: ''
    }
  });

  // Modal states
  const [opportunityModalOpen, setOpportunityModalOpen] = useState(false);
  const [associateModalOpen, setAssociateModalOpen] = useState(false);
  const [adherentModalOpen, setAdherentModalOpen] = useState(false);
  const [adherentType, setAdherentType] = useState('');
  
  // Opportunity CRUD states
  const [editOpportunityModalOpen, setEditOpportunityModalOpen] = useState(false);
  const [selectedOpportunityForEdit, setSelectedOpportunityForEdit] = useState(null);
  const [opportunityToEdit, setOpportunityToEdit] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [opportunityToDelete, setOpportunityToDelete] = useState(null);

  // Adherents data - now includes CSV parsing
  const [flotteAutoData, setFlotteAutoData] = useState([]);
  const [assureSanteData, setAssureSanteData] = useState([]);
  const [otherSocieteClients, setOtherSocieteClients] = useState([]);
  
  // CSV data for adherents
  const [csvAdherentsData, setCsvAdherentsData] = useState([]);
  const [csvHeaders, setCsvHeaders] = useState([]);
  const [csvFileName, setCsvFileName] = useState('');

  // Documents data
  const [documents, setDocuments] = useState([]);
  const [newDocuments, setNewDocuments] = useState([]);
  const [deletedDocuments, setDeletedDocuments] = useState([]);
  const [uploadingDocuments, setUploadingDocuments] = useState(false);

  // CSV file upload for adherents
  const [adherentsFile, setAdherentsFile] = useState(null);
  const [adherentsFileConfirmed, setAdherentsFileConfirmed] = useState(false);
  const adherentsFileInputRef = React.useRef();

  // Contract editing states
  const [editContractModalOpen, setEditContractModalOpen] = useState(false);
  const [selectedContractForEdit, setSelectedContractForEdit] = useState(null);
  const [viewDocumentsModalOpen, setViewDocumentsModalOpen] = useState(false);
  const [selectedContractForDocuments, setSelectedContractForDocuments] = useState(null);
  const [contractDocuments, setContractDocuments] = useState([]);
  const [newContractDocuments, setNewContractDocuments] = useState([]);
  const [deletedContractDocuments, setDeletedContractDocuments] = useState([]);

  // Load client data when modal opens
  useEffect(() => {
    if (open && clientId) {
      loadClientData();
      // Force refresh opportunities to ensure we have the latest data
      setTimeout(() => {
        forceRefreshOpportunities();
      }, 1000); // Small delay to ensure loadClientData completes first
    }
  }, [open, clientId]);

  // Load other SOCIETE clients when needed
  useEffect(() => {
    if (open && editMode && formData.typeClient === 'SOCIETE') {
      loadOtherSocieteClients();
    }
  }, [open, editMode, formData.typeClient, clientId]);

  // Set initial adherent type when component loads
  useEffect(() => {
    if (open && formData.typeClient === 'SOCIETE') {
      setAdherentType('flotte_auto'); // Default to first tab
    }
  }, [open, formData.typeClient]);

  // Detect CSV files when documents state changes
  useEffect(() => {
    if (open && clientId && documents.length > 0 && formData.typeClient === 'SOCIETE') {
      console.log('🔍 Detecting CSV files in documents:', documents.length, 'documents');
      
      try {
        // Find CSV documents among the loaded documents
        const csvDocuments = documents.filter(doc => 
          doc.fichierNom && doc.fichierNom.toLowerCase().endsWith('.csv')
        );
        
        console.log('📊 CSV documents found:', csvDocuments.length, csvDocuments);
        
        if (csvDocuments.length > 0) {
          console.log('📊 Found CSV documents:', csvDocuments);
          
          // For now, we'll use the first CSV document
          // In the future, we could add a way to select which CSV to display
          const csvDoc = csvDocuments[0];
          console.log('📁 Setting CSV file name to:', csvDoc.fichierNom);
          setCsvFileName(csvDoc.fichierNom);
          
          // Note: We'll parse the CSV content when the user views the adherents tab
          // This avoids loading large CSV data unnecessarily
          console.log('📁 CSV file ready for parsing:', csvDoc.fichierNom);
        } else {
          console.log('ℹ️ No CSV documents found for this client');
          setCsvFileName(''); // Clear any previous CSV file name
        }
      } catch (csvError) {
        console.error('❌ Error processing CSV documents:', csvError);
        // Don't fail the entire operation, just log the error
      }
    }
  }, [open, clientId, documents, formData.typeClient]);

  // Clear contract edit states when modal is closed
  useEffect(() => {
    if (!editContractModalOpen) {
      // Clear all contract-related states when modal is closed
      setNewContractDocuments([]);
      setDeletedContractDocuments([]);
      setContractDocuments([]);
      setSelectedContractForEdit(null);
    }
  }, [editContractModalOpen]);

  const loadOtherSocieteClients = async () => {
    try {
      const allClientsResponse = await clientService.getClients({ limit: 1000 });
      
      // Handle both possible response structures
      let allClients = [];
      if (Array.isArray(allClientsResponse)) {
        allClients = allClientsResponse;
      } else if (allClientsResponse && allClientsResponse.clients) {
        allClients = allClientsResponse.clients;
      } else {
        console.warn('⚠️ Unexpected response structure:', allClientsResponse);
        allClients = [];
      }
      
      const otherSocietes = allClients.filter(client => {
        const isSociete = client.typeClient === 'SOCIETE';
        const isNotCurrent = client.id !== clientId;
        return isSociete && isNotCurrent;
      });
      
      setOtherSocieteClients(otherSocietes);
    } catch (error) {
      console.error('❌ Error loading other SOCIETE clients:', error);
      setOtherSocieteClients([]);
    }
  };

  // CSV parsing function
  const parseCSV = (csvText) => {
    try {
      const lines = csvText.split('\n');
      if (lines.length < 2) {
        throw new Error('CSV file must have at least headers and one data row');
      }
      
      // Parse headers (first line)
      const headers = lines[0].split(',').map(header => header.trim().replace(/"/g, ''));
      if (headers.length === 0 || headers.every(h => !h)) {
        throw new Error('CSV headers cannot be empty');
      }
      setCsvHeaders(headers);
      
      // Parse data rows (skip first line which is headers)
      const data = [];
      for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim()) { // Skip empty lines
          const values = lines[i].split(',').map(value => value.trim().replace(/"/g, ''));
          const row = {};
          headers.forEach((header, index) => {
            row[header] = values[index] || '';
          });
          data.push(row);
        }
      }
      
      if (data.length === 0) {
        throw new Error('CSV file must contain at least one data row');
      }
      
      setCsvAdherentsData(data);
      console.log('✅ CSV parsed successfully:', { headers, data: data.length });
      return { headers, data };
    } catch (error) {
      console.error('❌ Error parsing CSV:', error);
      throw error;
    }
  };

  // Handle CSV file upload for adherents
  const handleAdherentsUpload = (event, type = null) => {
    const file = event.target.files[0];
    if (file && file.type === 'text/csv') {
      setAdherentsFile(file);
      setAdherentsFileConfirmed(false);
      
      // Set the adherent type if provided
      if (type) {
        setAdherentType(type);
      }
      
      // Parse the CSV file immediately
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const csvText = e.target.result;
          parseCSV(csvText);
          setCsvFileName(file.name);
        } catch (error) {
          setErrorMessage(`Erreur lors du parsing du CSV: ${error.message}`);
          setShowError(true);
        }
      };
      reader.readAsText(file);
    } else {
      alert('Veuillez sélectionner un fichier CSV');
    }
  };

  const confirmAdherentsFile = () => {
    setAdherentsFileConfirmed(true);
  };

  const cancelAdherentsFile = () => {
    setAdherentsFile(null);
    setAdherentsFileConfirmed(false);
    setCsvAdherentsData([]);
    setCsvHeaders([]);
    setCsvFileName('');
    // Reset the file input
    if (adherentsFileInputRef.current) {
      adherentsFileInputRef.current.value = '';
    }
  };

  // Load CSV content from stored CSV document
  const loadCSVContent = async () => {
    console.log('🔄 loadCSVContent called with:', { csvFileName, clientId, documentsCount: documents.length });
    
    if (!csvFileName || !clientId) {
      const errorMsg = `Impossible de charger le contenu CSV: csvFileName=${csvFileName}, clientId=${clientId}`;
      console.error('❌', errorMsg);
      setErrorMessage(errorMsg);
      setShowError(true);
      return;
    }

    try {
      console.log('🔄 Loading CSV content for file:', csvFileName);
      console.log('📁 Available documents:', documents.map(doc => ({ nom: doc.fichierNom, chemin: doc.fichierChemin })));
      
      // Find the CSV document among the loaded documents
      const csvDocument = documents.find(doc => 
        doc.fichierNom === csvFileName
      );

      if (!csvDocument) {
        const errorMsg = `Document CSV non trouvé: ${csvFileName}`;
        console.error('❌', errorMsg);
        setErrorMessage(errorMsg);
        setShowError(true);
        return;
      }

      console.log('✅ Found CSV document:', csvDocument);

      // Fetch the CSV file from the backend
      const apiUrl = `/api/documents/csv/${clientId}/${encodeURIComponent(csvFileName)}`;
      console.log('🌐 Fetching from:', apiUrl);
      
      const response = await fetch(apiUrl);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const csvText = await response.text();
      console.log('📄 CSV content received:', csvText.substring(0, 200) + '...');
      
      // Parse the CSV content
      const lines = csvText.split('\n').filter(line => line.trim());
      if (lines.length === 0) {
        setErrorMessage('Le fichier CSV est vide');
        setShowError(true);
        return;
      }
      
      // Parse headers (first line)
      const headers = lines[0].split(',').map(header => header.trim().replace(/"/g, ''));
      console.log('📋 CSV headers:', headers);
      
      // Parse data rows (skip header line)
      const data = lines.slice(1).map(line => {
        const values = line.split(',').map(value => value.trim().replace(/"/g, ''));
        const row = {};
        headers.forEach((header, index) => {
          row[header] = values[index] || '';
        });
        return row;
      }).filter(row => Object.values(row).some(value => value.trim() !== ''));
      
      console.log('📊 CSV data rows:', data.length);
      
      // Update state with parsed CSV data
      setCsvHeaders(headers);
      setCsvAdherentsData(data);
      setAdherentType('general');
      
      setSuccessMessage(`Contenu CSV chargé avec succès: ${data.length} adhérents trouvés`);
      setShowSuccess(true);
      
    } catch (error) {
      console.error('❌ Error loading CSV content:', error);
      setErrorMessage(`Erreur lors du chargement du CSV: ${error.message}`);
      setShowError(true);
    }
  };

  // Load client data when modal opens
  const loadClientData = async () => {
    console.log('🔄 loadClientData called with clientId:', clientId);
    if (!clientId) {
      console.log('❌ No clientId provided');
      return;
    }
    
    try {
      console.log('📡 Calling clientService.getClientDetails with ID:', clientId);
      const clientDetails = await clientService.getClientDetails(clientId);
      console.log('✅ Client details received:', clientDetails);

      if (!clientDetails) {
        console.error('❌ No client details received');
        return;
      }

      // Extract client and type-specific data from the nested structure
      const client = clientDetails.client || clientDetails;
      const particulier = clientDetails.particulier || {};
      const societe = clientDetails.societe || {};
      
      // Restructure data to match form structure
      const restructuredData = {
        // Client fields
        codeClient: client.codeClient || '',
        adresse: client.adresse || '',
        tel: client.tel || '',
        email: client.email || '',
        importance: client.importance || '0',
        budget: client.budget || '',
        proba: client.proba || '',
        typeClient: client.typeClient || '',
        
        // Particulier fields (nested structure to match form state)
        particulier: {
          titre: particulier.titre || '',
          nom: particulier.nom || '',
          prenom: particulier.prenom || '',
          sexe: particulier.sexe || '',
          nationalite: particulier.nationalite || '',
          lieuNaissance: particulier.lieuNaissance || '',
          dateNaissance: particulier.dateNaissance || '',
          date_deces: particulier.date_deces || '',
          datePermis: particulier.datePermis || '',
          cin: particulier.cin || '',
          profession: particulier.profession || '',
          typeDocIdentite: particulier.typeDocIdentite || '',
          situationFamiliale: particulier.situationFamiliale || '',
          nombreEnfants: particulier.nombreEnfants !== undefined && particulier.nombreEnfants !== null ? particulier.nombreEnfants : '',
          moyenContactPrefere: particulier.moyenContactPrefere || '',
          optoutTelephone: particulier.optoutTelephone || false,
          optoutEmail: particulier.optoutEmail || false
        },
        
        // Societe fields (nested structure)
        societe: {
          nom: societe.nom || '',
          formeJuridique: societe.formeJuridique || '',
          capital: societe.capital !== undefined && societe.capital !== null ? societe.capital : '',
          registreCom: societe.registreCom || '',
          taxePro: societe.taxePro || '',
          idFiscal: societe.idFiscal || '',
          CNSS: societe.CNSS || '',
          ICE: societe.ICE || '',
          siteWeb: societe.siteWeb || '',
          societeMere: societe.societeMere !== undefined && societe.societeMere !== null ? parseInt(societe.societeMere) : '',
          raisonSociale: societe.raisonSociale || '',
          sigle: societe.sigle || '',
          tribunalCommerce: societe.tribunalCommerce || '',
          secteurActivite: societe.secteurActivite || '',
          dateCreationSociete: societe.dateCreationSociete || '',
          nomContactPrincipal: societe.nomContactPrincipal || '',
          fonctionContactPrincipal: societe.fonctionContactPrincipal || ''
        }
      };
      
      setClientDetails(clientDetails);
      setFormData(restructuredData);
      
             // Load documents for this client
       try {
         const documentsResponse = await documentService.getClientDocuments(clientId);
         if (documentsResponse && documentsResponse.length > 0) {
           // Filter out documents without valid file paths (for backward compatibility)
           const validDocuments = documentsResponse.filter(doc => 
             doc.fichierChemin && doc.fichierChemin.trim() !== '' && doc.fichierChemin !== 'null'
           );
           
           setDocuments(validDocuments);
         } else {
           setDocuments([]);
         }
       } catch (docError) {
         console.error('❌ Error loading documents:', docError);
         setDocuments([]);
       }
       
       // Note: CSV detection will be handled in a separate useEffect when documents state changes
      
      // Load opportunities for this client
      try {
        const opportunitiesResponse = await opportunityService.getOpportunitiesByClient(clientId);
        setOpportunities(opportunitiesResponse || []);
        console.log('✅ Opportunities loaded:', opportunitiesResponse);
      } catch (oppError) {
        console.error('❌ Error loading opportunities:', oppError);
        setOpportunities([]);
      }
      
      // Load other SOCIETE clients for societeMere dropdown
      if (client.typeClient === 'SOCIETE') {
        try {
          const allClientsResponse = await clientService.getClients({ limit: 1000 });
          
          // Handle both possible response structures
          let allClients = [];
          if (Array.isArray(allClientsResponse)) {
            allClients = allClientsResponse;
          } else if (allClientsResponse && allClientsResponse.clients) {
            allClients = allClientsResponse.clients;
          } else {
            console.warn('⚠️ Unexpected response structure:', allClientsResponse);
            allClients = [];
          }
          
          const otherSocietes = allClients.filter(client => {
            const isSociete = client.typeClient === 'SOCIETE';
            const isNotCurrent = client.id !== clientId;
            return isSociete && isNotCurrent;
          });
          
          setOtherSocieteClients(otherSocietes);
        } catch (error) {
          console.error('❌ Error loading other SOCIETE clients:', error);
          setOtherSocieteClients([]);
        }
      }
      
      // Load contracts for this client
      try {
        const contractsResponse = await contractService.getContractsByClient(clientId);
        setContracts(contractsResponse || []);
        console.log('✅ Contracts loaded:', contractsResponse);
      } catch (contractError) {
        console.error('❌ Error loading contracts:', contractError);
        setContracts([]);
      }
      
      // Load client relations for this client
      try {
        console.log('🔄 Loading client relations for client ID:', clientId);
        const relationsResponse = await clientRelationService.getClientRelations(clientId);
        console.log('📦 Relations response received:', relationsResponse);
        setRelations(relationsResponse || []);
        console.log('✅ Relations loaded and set:', relationsResponse);
      } catch (relationError) {
        console.error('❌ Error loading relations:', relationError);
        setRelations([]);
      }
     
     // Load type relations for the dropdown
     try {
       const typeRelationsResponse = await clientRelationService.getTypeRelations();
       setTypeRelations(typeRelationsResponse || []);
       console.log('✅ Type relations loaded:', typeRelationsResponse);
     } catch (typeError) {
       console.error('❌ Error loading type relations:', typeError);
       setTypeRelations([]);
     }
      
    } catch (error) {
      console.error('❌ Error loading client data:', error);
    }
  };

  const handleEdit = () => {
    setEditMode(true);
  };

  const handleConfirm = async () => {
    try {

      
      // Update client data - we need to extract just the client fields
      const clientUpdateData = {
        codeClient: formData.codeClient,
        adresse: formData.adresse,
        tel: formData.tel,
        email: formData.email,
        importance: formData.importance,
        budget: formData.budget ? parseFloat(formData.budget) : null,
        proba: formData.proba
      };
      
      // Add particulier fields if this is a PARTICULIER client
      if (formData.typeClient === 'PARTICULIER') {

        Object.assign(clientUpdateData, {
          nom: formData.particulier.nom,
          prenom: formData.particulier.prenom,
          titre: formData.particulier.titre,
          sexe: formData.particulier.sexe,
          nationalite: formData.particulier.nationalite,
          lieuNaissance: formData.particulier.lieuNaissance,
          dateNaissance: formData.particulier.dateNaissance,
          date_deces: formData.particulier.date_deces,
          datePermis: formData.particulier.datePermis,
          cin: formData.particulier.cin,
          profession: formData.particulier.profession,
          typeDocIdentite: formData.particulier.typeDocIdentite,
          situationFamiliale: formData.particulier.situationFamiliale,
          nombreEnfants: formData.particulier.nombreEnfants ? parseInt(formData.particulier.nombreEnfants) : null,
          moyenContactPrefere: formData.particulier.moyenContactPrefere,
          optoutTelephone: formData.particulier.optoutTelephone,
          optoutEmail: formData.particulier.optoutEmail
        });
      }
      
      // Add societe fields if this is a SOCIETE client
      if (formData.typeClient === 'SOCIETE') {

        Object.assign(clientUpdateData, {
          nom: formData.societe.nom,
          formeJuridique: formData.societe.formeJuridique,
          capital: formData.societe.capital ? parseFloat(formData.societe.capital) : null,
          registreCom: formData.societe.registreCom,
          taxePro: formData.societe.taxePro,
          idFiscal: formData.societe.idFiscal,
          CNSS: formData.societe.CNSS,
          ICE: formData.societe.ICE,
          siteWeb: formData.societe.siteWeb,
          societeMere: formData.societe.societeMere ? parseInt(formData.societe.societeMere) : null,
          raisonSociale: formData.societe.raisonSociale,
          sigle: formData.societe.sigle,
          tribunalCommerce: formData.societe.tribunalCommerce,
          secteurActivite: formData.societe.secteurActivite,
          dateCreationSociete: formData.societe.dateCreationSociete,
          nomContactPrincipal: formData.societe.nomContactPrincipal,
          fonctionContactPrincipal: formData.societe.fonctionContactPrincipal
        });
      }
      

      
      await clientService.updateClient(clientId, clientUpdateData);

      
      // Handle document updates
      if (newDocuments.length > 0 || deletedDocuments.length > 0) {
        await handleDocumentUpdates();
      }
      
      // Handle CSV adherents data if confirmed
      if (adherentsFileConfirmed && csvAdherentsData.length > 0) {
        console.log('📊 Processing CSV adherents data...');
        await handleCSVAdherentsUpdate();
      }
      
      setEditMode(false);
      setSuccessMessage('Client mis à jour avec succès');
      setShowSuccess(true);
      
      // Clear document changes
      setNewDocuments([]);
      setDeletedDocuments([]);
      
      // Clear CSV changes
      setAdherentsFile(null);
      setAdherentsFileConfirmed(false);
      setCsvAdherentsData([]);
      setCsvHeaders([]);
      setCsvFileName('');
      
      // Reload ALL client data to show updated information
      console.log('🔄 Reloading client data after update...');
      await loadClientData();
      
      // Notify parent component about the update
      if (onClientUpdated) {
        console.log('🔄 Notifying parent component about client update...');
        onClientUpdated();
      }
    } catch (error) {
      console.error('❌ Error updating client:', error);
      console.error('❌ Error details:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        stack: error.stack
      });
      setErrorMessage(`Erreur lors de la mise à jour du client: ${error.message}`);
      setShowError(true);
    }
  };

  const handleDocumentUpdates = async () => {
    try {
      setUploadingDocuments(true);
      
      // Delete removed documents
      for (const docId of deletedDocuments) {
        try {
          await documentService.deleteDocument(docId);
          console.log(`✅ Document ${docId} deleted successfully`);
        } catch (error) {
          console.error(`❌ Failed to delete document ${docId}:`, error);
        }
      }
      
      // Upload new documents
      for (const file of newDocuments) {
        try {
          const formData = new FormData();
          formData.append('file', file);
          formData.append('client_id', clientId);
          formData.append('entity_type', 'CLIENT');
          formData.append('entity_id', clientId);
          
          await documentService.uploadDocument(formData);
          console.log(`✅ Document ${file.name} uploaded successfully`);
        } catch (error) {
          console.error(`❌ Failed to upload document ${file.name}:`, error);
        }
      }
      
      setUploadingDocuments(false);
    } catch (error) {
      console.error('❌ Error handling document updates:', error);
      setUploadingDocuments(false);
      throw error;
    }
  };

  const handleCSVAdherentsUpdate = async () => {
    try {
      console.log('📊 Starting CSV adherents update...');
      console.log('📊 CSV data:', csvAdherentsData);
      console.log('📊 Adherent type:', adherentType);
      
      // Here you would typically send the CSV data to the backend
      // For now, we'll just log it and could implement backend integration later
      
      if (adherentType === 'flotte_auto') {
        console.log('🚗 Processing flotte auto CSV data...');
        // TODO: Send to backend API for flotte auto processing
        // await csvService.processFlotteAutoCSV(clientId, csvAdherentsData);
      } else if (adherentType === 'assure_sante') {
        console.log('🏥 Processing assure sante CSV data...');
        // TODO: Send to backend API for assure sante processing
        // await csvService.processAssureSanteCSV(clientId, csvAdherentsData);
      } else {
        console.log('📋 Processing general adherents CSV data...');
        // TODO: Send to backend API for general adherents processing
        // await csvService.processAdherentsCSV(clientId, csvAdherentsData);
      }
      
      console.log('✅ CSV adherents update completed');
    } catch (error) {
      console.error('❌ Error handling CSV adherents update:', error);
      throw error;
    }
  };

    const handleCancel = () => {
    setEditMode(false);
    // Reset document changes
    setNewDocuments([]);
    setDeletedDocuments([]);
    // Reset CSV changes
    setAdherentsFile(null);
    setAdherentsFileConfirmed(false);
    setCsvAdherentsData([]);
    setCsvHeaders([]);
    setCsvFileName('');
    setAdherentType('');
    // Reset form data to original values
    if (clientDetails) {
      const restructuredData = {
        // Client fields
        codeClient: clientDetails.client?.codeClient || '',
        adresse: clientDetails.client?.adresse || '',
        tel: clientDetails.client?.tel || '',
        email: clientDetails.client?.email || '',
        importance: clientDetails.client?.importance || '0',
        budget: clientDetails.client?.budget || '',
        proba: clientDetails.client?.proba || '',
        typeClient: clientDetails.client?.typeClient || '',
        
        // Particulier fields
        particulier: {
          titre: clientDetails.particulier?.titre || '',
          nom: clientDetails.particulier?.nom || '',
          prenom: clientDetails.particulier?.prenom || '',
          sexe: clientDetails.particulier?.sexe || '',
          nationalite: clientDetails.particulier?.nationalite || '',
          lieuNaissance: clientDetails.particulier?.lieuNaissance || '',
          dateNaissance: clientDetails.particulier?.dateNaissance || '',
          date_deces: clientDetails.particulier?.date_deces || '',
          datePermis: clientDetails.particulier?.datePermis || '',
          cin: clientDetails.particulier?.cin || '',
          profession: clientDetails.particulier?.profession || '',
          typeDocIdentite: clientDetails.particulier?.typeDocIdentite || '',
          situationFamiliale: clientDetails.particulier?.situationFamiliale || '',
          nombreEnfants: clientDetails.particulier?.nombreEnfants !== undefined && clientDetails.particulier?.nombreEnfants !== null ? clientDetails.particulier.nombreEnfants : '',
          moyenContactPrefere: clientDetails.particulier?.moyenContactPrefere || '',
          optoutTelephone: clientDetails.particulier?.optoutTelephone || false,
          optoutEmail: clientDetails.particulier?.optoutEmail || false
        },
        
                 // Societe fields
         societe: {
           nom: clientDetails.societe?.nom || '',
           formeJuridique: clientDetails.societe?.formeJuridique || '',
           capital: clientDetails.societe?.capital !== undefined && clientDetails.societe?.capital !== null ? clientDetails.societe.capital : '',
           registreCom: clientDetails.societe?.registreCom || '',
           taxePro: clientDetails.societe?.taxePro || '',
           idFiscal: clientDetails.societe?.idFiscal || '',
           CNSS: clientDetails.societe?.CNSS || '',
           ICE: clientDetails.societe?.ICE || '',
           siteWeb: clientDetails.societe?.siteWeb || '',
           societeMere: clientDetails.societe?.societeMere !== undefined && clientDetails.societe?.societeMere !== null ? parseInt(clientDetails.societe.societeMere) : '',
           raisonSociale: clientDetails.societe?.raisonSociale || '',
           sigle: clientDetails.societe?.sigle || '',
           tribunalCommerce: clientDetails.societe?.tribunalCommerce || '',
           secteurActivite: clientDetails.societe?.secteurActivite || '',
           dateCreationSociete: clientDetails.societe?.dateCreationSociete || '',
           nomContactPrincipal: clientDetails.societe?.nomContactPrincipal || '',
           fonctionContactPrincipal: clientDetails.societe?.fonctionContactPrincipal || ''
         }
      };
      setFormData(restructuredData);
    }
  };

  const handleClose = () => {
    // Only notify parent component if there were actual changes
    // The onClientUpdated will be called by individual update functions when needed
    onClose();
  };

  const [transformModalOpen, setTransformModalOpen] = useState(false);
  const [selectedOpportunity, setSelectedOpportunity] = useState(null);
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
      await loadClientData(); // Reload data
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

  const handleAddOpportunity = async () => {
    setOpportunityModalOpen(true);
  };

  const handleOpportunitySuccess = async () => {
    await loadClientData(); // Reload data
    setSuccessMessage('Opportunité créée avec succès');
    setShowSuccess(true);
  };

  const handleEditOpportunity = (opportunity) => {
    setSelectedOpportunityForEdit(opportunity);
    setEditOpportunityModalOpen(true);
  };

  const handleEditOpportunitySuccess = async () => {
    await loadClientData(); // Reload data
    setSuccessMessage('Opportunité modifiée avec succès');
    setShowSuccess(true);
    setEditOpportunityModalOpen(false);
    setSelectedOpportunityForEdit(null);
  };

  const handleDeleteOpportunity = (opportunityId) => {
    console.log('🗑️ handleDeleteOpportunity called with ID:', opportunityId);
    setOpportunityToDelete(opportunityId);
    setDeleteDialogOpen(true);
    console.log('✅ Delete dialog opened, opportunityToDelete set to:', opportunityId);
  };

  const handleCloseDeleteDialog = () => {
    console.log('❌ handleCloseDeleteDialog called');
    setDeleteDialogOpen(false);
    setOpportunityToDelete(null);
    console.log('✅ Delete dialog closed, opportunityToDelete cleared');
  };

  // Function to reload only opportunities data (more efficient than loadClientData)
  const reloadOpportunities = async () => {
    try {
      console.log('🔄 Reloading only opportunities data...');
      const opportunitiesResponse = await opportunityService.getOpportunitiesByClient(clientId);
      setOpportunities(opportunitiesResponse || []);
      console.log('✅ Opportunities reloaded:', opportunitiesResponse);
    } catch (error) {
      console.error('❌ Error reloading opportunities:', error);
      // Don't show error to user for this, just log it
    }
  };

  // Function to force refresh opportunities data (used when data might be stale)
  const forceRefreshOpportunities = async () => {
    try {
      console.log('🔄 Force refreshing opportunities data...');
      // Clear current state first
      setOpportunities([]);
      // Then reload fresh data
      await reloadOpportunities();
      console.log('✅ Opportunities force refreshed');
    } catch (error) {
      console.error('❌ Error force refreshing opportunities:', error);
    }
  };

  const handleConfirmDelete = async () => {
    console.log('🔄 handleConfirmDelete called');
    console.log('📋 opportunityToDelete:', opportunityToDelete);
    
    if (!opportunityToDelete) {
      console.error('❌ No opportunity to delete!');
      return;
    }
    
    try {
      console.log('📡 Calling opportunityService.deleteOpportunity with ID:', opportunityToDelete);
      const result = await opportunityService.deleteOpportunity(opportunityToDelete);
      console.log('✅ Delete API call successful, result:', result);
      
      // Force clear the opportunities state first to ensure fresh data
      console.log('🗑️ Clearing opportunities state...');
      setOpportunities([]);
      
      // Only reload opportunities data, not all client data
      console.log('🔄 Reloading opportunities data...');
      await reloadOpportunities();
      console.log('✅ Opportunities data reloaded');
      
      setDeleteDialogOpen(false);
      setOpportunityToDelete(null);
      setSuccessMessage('Opportunité supprimée avec succès');
      setShowSuccess(true);
      console.log('✅ Delete flow completed successfully');
    } catch (error) {
      console.error('❌ Error deleting opportunity:', error);
      console.error('❌ Error details:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      });
      // Handle specific error cases
      if (error.response?.status === 404) {
        setErrorMessage('Cette opportunité n\'existe plus. Actualisation de la liste...');
        setShowError(true);
        
        // Force refresh opportunities data since the current state is stale
        console.log('🔄 Opportunity not found, forcing refresh of opportunities...');
        await reloadOpportunities();
      } else {
        setErrorMessage('Erreur lors de la suppression de l\'opportunité');
        setShowError(true);
      }
    }
  };

  const handleAddRelation = async () => {
    setAssociateModalOpen(true);
  };

  const handleAddAdherent = (type) => {
    setAdherentType(type);
    setAdherentModalOpen(true);
  };

  const handleAssociateSuccess = async () => {
    console.log('🔄 handleAssociateSuccess called');
    console.log('🔄 Loading client data...');
    await loadClientData();
    console.log('✅ Client data loaded');
    
    // Refresh the main table to show updated client associations
    if (onRefreshMainTable) {
      console.log('🔄 Calling onRefreshMainTable...');
      onRefreshMainTable();
      console.log('✅ onRefreshMainTable called');
    } else {
      console.log('⚠️ onRefreshMainTable not available');
    }
    
    setSuccessMessage('Associés ajoutés avec succès');
    setShowSuccess(true);
    console.log('✅ handleAssociateSuccess completed');
  };

  const handleAdherentSuccess = async () => {
    await loadClientData();
    setSuccessMessage('Adhérent ajouté avec succès');
    setShowSuccess(true);
  };

  const handleRemoveRelation = async (relationId) => {
    try {
      console.log('🔄 handleRemoveRelation called for relation ID:', relationId);
      
      console.log('🔄 Deleting client relation...');
      await clientRelationService.deleteClientRelation(relationId);
      console.log('✅ Client relation deleted');
      
      setSuccessMessage('Relation supprimée avec succès');
      setShowSuccess(true);
      
      console.log('🔄 Reloading client data...');
      await loadClientData(); // Reload data
      console.log('✅ Client data reloaded');
      
      // Debug: Check if relations were actually removed
      console.log('🔍 Current relations state after reload:', relations);
      
      // Force refresh the relations state by calling the API again
      try {
        console.log('🔄 Force refreshing relations...');
        const freshRelations = await clientRelationService.getClientRelations(clientId);
        console.log('📦 Fresh relations received:', freshRelations);
        setRelations(freshRelations || []);
        console.log('✅ Relations state updated with fresh data');
      } catch (refreshError) {
        console.error('❌ Error refreshing relations:', refreshError);
      }
      
      // Refresh the main table to show updated client associations
      if (onRefreshMainTable) {
        console.log('🔄 Calling onRefreshMainTable...');
        onRefreshMainTable();
        console.log('✅ onRefreshMainTable called');
      } else {
        console.log('⚠️ onRefreshMainTable not available');
      }
      
      console.log('✅ handleRemoveRelation completed');
    } catch (error) {
      console.error('❌ Error removing relation:', error);
      setErrorMessage('Erreur lors de la suppression de la relation');
      setShowError(true);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => {
      // Handle nested fields (particulier.* and societe.*)
      if (field.startsWith('particulier.')) {
        const subField = field.replace('particulier.', '');
        return {
          ...prev,
          particulier: {
            ...prev.particulier,
            [subField]: value
          }
        };
      } else if (field.startsWith('societe.')) {
        const subField = field.replace('societe.', '');
        return {
          ...prev,
          societe: {
            ...prev.societe,
            [subField]: value
          }
        };
      } else {
        // Handle top-level fields
        return {
          ...prev,
          [field]: value
        };
      }
    });
  };

  const handleDocumentUpload = (event) => {
    const files = Array.from(event.target.files);
    const pdfFiles = files.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length !== files.length) {
      alert('Seuls les fichiers PDF sont acceptés');
      return;
    }
    
    setNewDocuments(prev => [...prev, ...pdfFiles]);
  };

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

  // Contract handlers
  const handleEditContract = async (contract) => {
    console.log('🔍 Opening edit modal for contract:', contract);
    
    // Clear all previous contract-related states first
    setNewContractDocuments([]);
    setDeletedContractDocuments([]);
    
    setSelectedContractForEdit(contract);
    setEditContractModalOpen(true);
    
    // Load companies and duration types when opening the edit contract modal
    await loadCompanies();
    await loadDurationTypes();
    
    // Load existing documents for this contract
    try {
      console.log(`📄 Loading documents for contract ${contract.id}...`);
      const docs = await documentService.getDocumentsByEntity('contrat', contract.id);
      console.log(`✅ Loaded ${docs.length} documents for contract:`, docs);
      setContractDocuments(docs);
    } catch (error) {
      console.error('Error loading contract documents:', error);
      setContractDocuments([]);
    }
  };

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

  const handleContractEditSuccess = async () => {
    try {
      if (!selectedContractForEdit) return;
      
      // Prepare contract data for update
      const updateData = {
        numPolice: selectedContractForEdit.numPolice,
        typeContrat: selectedContractForEdit.typeContrat,
        dateDebut: selectedContractForEdit.dateDebut,
        dateFin: selectedContractForEdit.dateFin,
        prime: selectedContractForEdit.prime ? parseFloat(selectedContractForEdit.prime) : null,
        idCompagnie: selectedContractForEdit.idCompagnie ? parseInt(selectedContractForEdit.idCompagnie) : null,
        idTypeDuree: selectedContractForEdit.idTypeDuree ? parseInt(selectedContractForEdit.idTypeDuree) : null
      };
      
      // Update contract via API
      await contractService.updateContract(selectedContractForEdit.id, updateData);
      
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
          formData.append('client_id', selectedContractForEdit.idClient);
          formData.append('entity_type', 'contrat');
          formData.append('entity_id', selectedContractForEdit.id);
          
          // Upload document directly linked to contract
          const uploadedDoc = await documentService.uploadDocument(formData);
          
          console.log(`✅ Document ${file.name} uploaded and linked successfully to contract ${selectedContractForEdit.id}`);
        } catch (error) {
          console.error(`Error uploading document ${file.name}:`, error);
          setErrorMessage(`Erreur lors de l'upload du document ${file.name}: ${error.message}`);
          setShowError(true);
        }
      }
      
      // Reload data
      await loadClientData();
      
      // Reset document states
      setContractDocuments([]);
      setNewContractDocuments([]);
      setDeletedContractDocuments([]);
      
      setSuccessMessage('Contrat modifié avec succès');
      setShowSuccess(true);
      setEditContractModalOpen(false);
      setSelectedContractForEdit(null);
    } catch (error) {
      console.error('Error updating contract:', error);
      setErrorMessage(`Erreur lors de la modification: ${error.message}`);
      setShowError(true);
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
      }
      
      // Clean up the URL after a delay
      setTimeout(() => URL.revokeObjectURL(fileUrl), 1000);
    } else {
      alert('Document non disponible');
    }
  };

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

  const removeDocument = (index, isNew = false) => {
    if (isNew) {
      setNewDocuments(prev => prev.filter((_, i) => i !== index));
    } else {
      const doc = documents[index];
      setDeletedDocuments(prev => [...prev, doc.id]);
      setDocuments(prev => prev.filter((_, i) => i !== index));
    }
  };

  const renderClientInfo = () => {
    if (!clientDetails) return null;

    return (
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Informations du client
        </Typography>
        
        {/* Basic Client Information */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Code Client *"
              value={formData.codeClient}
              onChange={(e) => handleInputChange('codeClient', e.target.value)}
              size="small"
              disabled={!editMode}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Type Client"
              value={formData.typeClient}
              onChange={(e) => handleInputChange('typeClient', e.target.value)}
              size="small"
              disabled
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Téléphone *"
              value={formData.tel}
              onChange={(e) => handleInputChange('tel', e.target.value)}
              size="small"
              disabled={!editMode}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Email *"
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              size="small"
              disabled={!editMode}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Adresse"
              value={formData.adresse}
              onChange={(e) => handleInputChange('adresse', e.target.value)}
              size="small"
              disabled={!editMode}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Budget (DH)"
              value={formData.budget}
              onChange={(e) => handleInputChange('budget', e.target.value)}
              size="small"
              disabled={!editMode}
              InputProps={{
                endAdornment: <InputAdornment position="end">DH</InputAdornment>,
              }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Probabilité (%)"
              value={formData.proba}
              onChange={(e) => handleInputChange('proba', e.target.value)}
              size="small"
              disabled={!editMode}
              InputProps={{
                endAdornment: <InputAdornment position="end">%</InputAdornment>,
              }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Importance
              </Typography>
              <StarRating
                value={parseFloat(formData.importance) || 0}
                onChange={(value) => handleInputChange('importance', value.toString())}
                readOnly={!editMode}
                size="large"
                showHalfStars={true}
              />
            </Box>
          </Grid>
        </Grid>

        {/* Particulier Fields - Same order as ClientInfoModal */}
        {formData.typeClient === 'PARTICULIER' && (
          <>
            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              Informations particulières
            </Typography>
            
            <Grid container spacing={2} sx={{ mb: 3 }}>
                             <Grid item xs={12} md={4}>
                               <TextField
                 fullWidth
                 label="Titre"
                 value={formData.particulier.titre || ''}
                 onChange={(e) => handleInputChange('particulier.titre', e.target.value)}
                 size="small"
                 disabled={!editMode}
               />
               </Grid>
               <Grid item xs={12} md={4}>
                 <TextField
                   fullWidth
                   label="Nom *"
                   value={formData.particulier.nom || ''}
                   onChange={(e) => handleInputChange('particulier.nom', e.target.value)}
                   size="small"
                   disabled={!editMode}
                 />
               </Grid>
               <Grid item xs={12} md={4}>
                 <TextField
                   fullWidth
                   label="Prénom *"
                   value={formData.particulier.prenom || ''}
                   onChange={(e) => handleInputChange('particulier.prenom', e.target.value)}
                   size="small"
                   disabled={!editMode}
                 />
               </Grid>
                             <Grid item xs={12} md={4}>
                 <FormControl fullWidth size="small">
                   <InputLabel>Sexe</InputLabel>
                   <Select
                     value={formData.particulier.sexe || ''}
                     onChange={(e) => handleInputChange('particulier.sexe', e.target.value)}
                     label="Sexe"
                     disabled={!editMode}
                   >
                     <MenuItem value="M">Masculin</MenuItem>
                     <MenuItem value="F">Féminin</MenuItem>
                   </Select>
                 </FormControl>
               </Grid>
               <Grid item xs={12} md={4}>
                 <TextField
                   fullWidth
                   label="Nationalité"
                   value={formData.particulier.nationalite || ''}
                   onChange={(e) => handleInputChange('particulier.nationalite', e.target.value)}
                   size="small"
                   disabled={!editMode}
                 />
               </Grid>
               <Grid item xs={12} md={4}>
                 <TextField
                   fullWidth
                   label="Lieu de naissance"
                   value={formData.particulier.lieuNaissance || ''}
                   onChange={(e) => handleInputChange('particulier.lieuNaissance', e.target.value)}
                   size="small"
                   disabled={!editMode}
                 />
               </Grid>
                             <Grid item xs={12} md={4}>
                 <TextField
                   fullWidth
                   label="Date de naissance"
                   type="date"
                   value={formData.particulier.dateNaissance || ''}
                   onChange={(e) => handleInputChange('particulier.dateNaissance', e.target.value)}
                   size="small"
                   disabled={!editMode}
                   InputLabelProps={{ shrink: true }}
                 />
               </Grid>
               <Grid item xs={12} md={4}>
                 <TextField
                   fullWidth
                   label="CIN"
                   value={formData.particulier.cin || ''}
                   onChange={(e) => handleInputChange('particulier.cin', e.target.value)}
                   size="small"
                   disabled={!editMode}
                 />
               </Grid>
               <Grid item xs={12} md={4}>
                 <TextField
                   fullWidth
                   label="Profession"
                   value={formData.particulier.profession || ''}
                   onChange={(e) => handleInputChange('particulier.profession', e.target.value)}
                   size="small"
                   disabled={!editMode}
                 />
               </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Type Document Identité"
                  value={formData.particulier.typeDocIdentite || ''}
                  onChange={(e) => handleInputChange('particulier.typeDocIdentite', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Situation Familiale"
                  value={formData.particulier.situationFamiliale || ''}
                  onChange={(e) => handleInputChange('particulier.situationFamiliale', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Nombre d&apos;Enfants"
                  type="number"
                  value={formData.particulier.nombreEnfants !== undefined && formData.particulier.nombreEnfants !== null ? formData.particulier.nombreEnfants : ''}
                  onChange={(e) => handleInputChange('particulier.nombreEnfants', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Moyen Contact Préféré"
                  value={formData.particulier.moyenContactPrefere || ''}
                  onChange={(e) => handleInputChange('particulier.moyenContactPrefere', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Date de Décès"
                  type="date"
                  value={formData.particulier.date_deces || ''}
                  onChange={(e) => handleInputChange('particulier.date_deces', e.target.value)}
                  size="small"
                  disabled={!editMode}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Date Permis"
                  type="date"
                  value={formData.particulier.datePermis || ''}
                  onChange={(e) => handleInputChange('particulier.datePermis', e.target.value)}
                  size="small"
                  disabled={!editMode}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Opt-out Téléphone</InputLabel>
                  <Select
                    value={formData.particulier.optoutTelephone || false}
                    onChange={(e) => handleInputChange('particulier.optoutTelephone', e.target.value)}
                    label="Opt-out Téléphone"
                    disabled={!editMode}
                  >
                    <MenuItem value={false}>Non</MenuItem>
                    <MenuItem value={true}>Oui</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Opt-out Email</InputLabel>
                  <Select
                    value={formData.particulier.optoutEmail || false}
                    onChange={(e) => handleInputChange('particulier.optoutEmail', e.target.value)}
                    label="Opt-out Email"
                    disabled={!editMode}
                  >
                    <MenuItem value={false}>Non</MenuItem>
                    <MenuItem value={true}>Oui</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </>
        )}

        {/* Societe Fields - Same order as ClientInfoModal */}
        {formData.typeClient === 'SOCIETE' && (
          <>
            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              Informations de la société
            </Typography>
            
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Nom de la société *"
                  value={formData.societe.nom || ''}
                  onChange={(e) => handleInputChange('societe.nom', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Forme juridique"
                  value={formData.societe.formeJuridique || ''}
                  onChange={(e) => handleInputChange('societe.formeJuridique', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Capital"
                  type="number"
                  value={formData.societe.capital !== undefined && formData.societe.capital !== null ? formData.societe.capital : ''}
                  onChange={(e) => handleInputChange('societe.capital', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Registre de commerce"
                  value={formData.societe.registreCom || ''}
                  onChange={(e) => handleInputChange('societe.registreCom', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Taxe professionnelle"
                  value={formData.societe.taxePro || ''}
                  onChange={(e) => handleInputChange('societe.taxePro', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Identifiant fiscal"
                  value={formData.societe.idFiscal || ''}
                  onChange={(e) => handleInputChange('societe.idFiscal', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="CNSS"
                  value={formData.societe.CNSS || ''}
                  onChange={(e) => handleInputChange('societe.CNSS', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="ICE"
                  value={formData.societe.ICE || ''}
                  onChange={(e) => handleInputChange('societe.ICE', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Site web"
                  value={formData.societe.siteWeb || ''}
                  onChange={(e) => handleInputChange('societe.siteWeb', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Raison sociale"
                  value={formData.societe.raisonSociale || ''}
                  onChange={(e) => handleInputChange('societe.raisonSociale', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Sigle"
                  value={formData.societe.sigle || ''}
                  onChange={(e) => handleInputChange('societe.sigle', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Tribunal de commerce"
                  value={formData.societe.tribunalCommerce || ''}
                  onChange={(e) => handleInputChange('societe.tribunalCommerce', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Secteur d&apos;activité"
                  value={formData.societe.secteurActivite || ''}
                  onChange={(e) => handleInputChange('societe.secteurActivite', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Date de création"
                  type="date"
                  value={formData.societe.dateCreationSociete || ''}
                  onChange={(e) => handleInputChange('societe.dateCreationSociete', e.target.value)}
                  size="small"
                  disabled={!editMode}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Nom du contact principal"
                  value={formData.societe.nomContactPrincipal || ''}
                  onChange={(e) => handleInputChange('societe.nomContactPrincipal', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Fonction du contact principal"
                  value={formData.societe.fonctionContactPrincipal || ''}
                  onChange={(e) => handleInputChange('societe.fonctionContactPrincipal', e.target.value)}
                  size="small"
                  disabled={!editMode}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth size="small">
                  <InputLabel>Société mère</InputLabel>
                                     <Select
                     value={formData.societe.societeMere !== undefined && formData.societe.societeMere !== null ? formData.societe.societeMere : ''}
                     onChange={(e) => handleInputChange('societe.societeMere', e.target.value)}
                     label="Société mère"
                     disabled={!editMode}
                   >
                     <MenuItem value="">
                       <em>Aucune société mère</em>
                     </MenuItem>
                     {otherSocieteClients.map((societe) => (
                       <MenuItem key={societe.id} value={societe.id}>
                         {societe.nom || societe.codeClient} {societe.raisonSociale ? `(${societe.raisonSociale})` : ''}
                       </MenuItem>
                     ))}
                   </Select>
                   {/* Show selected societe name if one is selected */}
                   {formData.societe.societeMere && (
                     <Typography variant="caption" color="text.secondary" display="block">
                       Société mère sélectionnée: {otherSocieteClients.find(s => s.id === formData.societe.societeMere)?.nom || 'ID: ' + formData.societe.societeMere}
                     </Typography>
                   )}
                  {/* Debug info */}
                  {editMode && (
                    <Typography variant="caption" color="text.secondary">
                      {otherSocieteClients.length} sociétés disponibles
                    </Typography>
                  )}
                </FormControl>
              </Grid>
            </Grid>
          </>
        )}
        </Box>
      );
  };

  const renderOpportunitiesTab = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Opportunités</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddOpportunity}
          size="small"
        >
          Ajouter Opportunité
        </Button>
      </Box>
      
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Produit</TableCell>
              <TableCell>Origine</TableCell>
              <TableCell>Étape</TableCell>
              <TableCell>Date de Création</TableCell>
              <TableCell>Date d&apos;Échéance</TableCell>
              <TableCell>Budget</TableCell>
                      <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {opportunities
              .sort((a, b) => {
                // Sort by ID (newest first) to ensure new opportunities appear at the top
                return b.id - a.id;
              })
              .map((opp) => (
                <TableRow key={opp.id}>
                  <TableCell>
                    {opp.produit ? opp.produit.libelle : opp.idProduit || 'N/A'}
                  </TableCell>
                  <TableCell>{opp.origine || 'N/A'}</TableCell>
                  <TableCell>{opp.etape || 'N/A'}</TableCell>
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
              ))}
            {opportunities.length === 0 && (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  Aucune opportunité trouvée
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderContractsTab = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Contrats</Typography>
      </Box>
      
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Numéro Police</TableCell>
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
            {contracts.map((contract) => (
                <TableRow key={contract.id}>
                  <TableCell>{contract.numPolice}</TableCell>
                  <TableCell>{contract.typeContrat}</TableCell>
                  <TableCell>{contract.duree ? contract.duree.libelle : 'N/A'}</TableCell>
                  <TableCell>{contract.dateDebut}</TableCell>
                  <TableCell>{contract.dateFin || 'N/A'}</TableCell>
                  <TableCell>{contract.prime ? `${contract.prime} DH` : 'N/A'}</TableCell>
                  <TableCell>{contract.compagnie ? contract.compagnie.nom : 'N/A'}</TableCell>
                  <TableCell>{contract.produit ? contract.produit.libelle : contract.idProduit || 'N/A'}</TableCell>
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
              ))}
            {contracts.length === 0 && (
              <TableRow>
                <TableCell colSpan={9} align="center">
                  Aucun contrat trouvé
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderRelationsTab = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Associés</Typography>
        <Button
          variant="contained"
          startIcon={<PersonAddIcon />}
          onClick={handleAddRelation}
          size="small"
        >
          Ajouter Associé
        </Button>
      </Box>
      
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Code Client</TableCell>
              <TableCell>Nom</TableCell>
              <TableCell>Type Relation</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {relations.map((relation) => {
              const relationType = typeRelations.find(type => type.id === relation.idTypeRelation);
              return (
                <TableRow key={relation.id}>
                  <TableCell>{relation.client_lie?.codeClient || relation.idClientLie}</TableCell>
                  <TableCell>{relation.client_lie?.nom || 'N/A'}</TableCell>
                  <TableCell>{relationType?.libelle || 'N/A'}</TableCell>
                  <TableCell>{relation.description || 'N/A'}</TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleRemoveRelation(relation.id)}
                      color="error"
                      title="Dissocier"
                    >
                      <RemoveIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              );
            })}
            {relations.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  Aucun associé trouvé
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderAdherentsTab = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Adhérents</Typography>
        {editMode && (
          <Button
            variant="contained"
            component="label"
            startIcon={<FileUploadIcon />}
            size="small"
            disabled={adherentsFileConfirmed}
          >
            {adherentsFileConfirmed ? 'CSV Confirmé' : 'Importer CSV Adhérents'}
            <input
              type="file"
              hidden
              accept=".csv"
              onChange={handleAdherentsUpload}
              ref={adherentsFileInputRef}
            />
          </Button>
        )}
      </Box>

      {/* CSV File Status and Load Button */}
      {csvFileName && !csvAdherentsData.length && (
        <Box sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1, backgroundColor: '#f5f5f5' }}>
          <Typography variant="body2" gutterBottom>
            <strong>Fichier CSV disponible:</strong> {csvFileName}
          </Typography>
          <Button
            variant="outlined"
            size="small"
            onClick={loadCSVContent}
            startIcon={<TransformIcon />}
            sx={{ mt: 1 }}
          >
            Charger le contenu CSV
          </Button>
        </Box>
      )}

      {/* CSV Data Status */}
      {csvAdherentsData.length > 0 && csvHeaders.length > 0 && (
        <Box sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1, backgroundColor: '#f5f5f5' }}>
          <Typography variant="body2" gutterBottom>
            <strong>Contenu CSV chargé:</strong> {csvFileName}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            <strong>Colonnes:</strong> {csvHeaders.length} | <strong>Lignes:</strong> {csvAdherentsData.length}
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
            <strong>Colonnes:</strong> {csvHeaders.join(', ')}
          </Typography>
        </Box>
      )}

      {/* Dynamic CSV Data Table */}
      {csvAdherentsData.length > 0 && csvHeaders.length > 0 ? (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                {csvHeaders.map((header, index) => (
                  <TableCell key={index} sx={{ fontWeight: 'bold' }}>
                    {header}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {csvAdherentsData.map((row, rowIndex) => (
                <TableRow 
                  key={rowIndex}
                  sx={{ 
                    backgroundColor: rowIndex % 2 === 0 ? '#ffffff' : '#fafafa',
                    '&:hover': { backgroundColor: '#f0f0f0' }
                  }}
                >
                  {csvHeaders.map((header, colIndex) => (
                    <TableCell key={colIndex}>
                      {row[header] || 'N/A'}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : csvFileName ? (
        /* Show message when CSV file is available but not loaded yet */
        <Box sx={{ mt: 2, p: 3, textAlign: 'center', border: '1px solid #e0e0e0', borderRadius: 1, backgroundColor: '#f9f9f9' }}>
          <Typography variant="body1" color="text.secondary">
            Fichier CSV disponible. Cliquez sur &quot;Charger le contenu CSV&quot; pour afficher les données.
          </Typography>
        </Box>
      ) : (
        /* Show message when no CSV file is available */
        <Box sx={{ mt: 2, p: 3, textAlign: 'center', border: '1px solid #e0e0e0', borderRadius: 1, backgroundColor: '#f9f9f9' }}>
          <Typography variant="body1" color="text.secondary">
            Aucun fichier CSV d&apos;adhérents disponible pour ce client.
          </Typography>
        </Box>
      )}
    </Box>
  );



  const renderDocumentsTab = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Documents</Typography>
        {editMode && (
          <Button
            variant="contained"
            component="label"
            startIcon={uploadingDocuments ? <CircularProgress size={16} /> : <UploadIcon />}
            size="small"
            disabled={uploadingDocuments}
          >
            {uploadingDocuments ? 'Traitement...' : 'Importer Document'}
            <input
              type="file"
              hidden
              multiple
              accept=".pdf"
              onChange={handleDocumentUpload}
            />
          </Button>
        )}
      </Box>
      
      {/* Documents Grid */}
      <Grid container spacing={2}>
        {/* Existing Documents */}
        {documents.map((doc, index) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={`existing-${index}`}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Box
                sx={{
                  height: 200,
                  backgroundColor: '#f5f5f5',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  border: '1px solid #e0e0e0',
                  '&:hover': {
                    backgroundColor: '#eeeeee'
                  }
                }}
                onClick={() => handleDocumentClick(doc)}
              >
                <Box sx={{ textAlign: 'center' }}>
                  <DescriptionIcon sx={{ fontSize: 48, color: '#d32f2f', mb: 1 }} />
                  <Typography variant="caption" color="text.secondary">
                    PDF
                  </Typography>
                </Box>
              </Box>
                              <CardContent sx={{ flexGrow: 1, p: 1 }}>
                  <Typography variant="body2" noWrap>
                    {doc.fichierNom}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {doc.instantTele ? new Date(doc.instantTele).toLocaleDateString() : 'N/A'}
                  </Typography>
                </CardContent>
              <CardActions sx={{ p: 1, justifyContent: 'space-between' }}>
                <Button
                  size="small"
                  startIcon={<VisibilityIcon />}
                  onClick={() => handleDocumentClick(doc)}
                >
                  Voir
                </Button>
                {editMode && (
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => removeDocument(index, false)}
                  >
                    <DeleteIcon />
                  </IconButton>
                )}
              </CardActions>
            </Card>
          </Grid>
        ))}
        
        {/* New Documents */}
        {newDocuments.map((doc, index) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={`new-${index}`}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', border: '2px dashed #1976d2' }}>
              <Box
                sx={{
                  height: 200,
                  backgroundColor: '#e3f2fd',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '1px solid #1976d2'
                }}
              >
                <Box sx={{ textAlign: 'center' }}>
                  <UploadIcon sx={{ fontSize: 48, color: '#1976d2', mb: 1 }} />
                  <Typography variant="caption" color="primary">
                    Nouveau PDF
                  </Typography>
                </Box>
              </Box>
              <CardContent sx={{ flexGrow: 1, p: 1 }}>
                <Typography variant="body2" noWrap color="primary">
                  {doc.name} (Nouveau)
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  À télécharger
                </Typography>
              </CardContent>
              <CardActions sx={{ p: 1, justifyContent: 'center' }}>
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => removeDocument(index, true)}
                >
                  <DeleteIcon />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
        
        {/* Empty State */}
        {documents.length === 0 && newDocuments.length === 0 && (
          <Grid item xs={12}>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <DescriptionIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Aucun document
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {editMode ? 'Ajoutez des documents en utilisant le bouton "Importer Document"' : 'Aucun document disponible pour ce client'}
              </Typography>
            </Box>
          </Grid>
        )}
      </Grid>
    </Box>
  );

  if (loading) {
    return (
      <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
        <DialogContent>
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        </DialogContent>
      </Dialog>
    );
  }

  if (!clientDetails) {
    return null;
  }

  const isSociete = formData.typeClient === 'SOCIETE';
  const tabLabels = isSociete 
    ? ['Opportunités', 'Contrats', 'Adhérents', 'Documents']
    : ['Opportunités', 'Contrats', 'Associés', 'Documents'];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h5">
            Détails du Client - {formData.codeClient}
          </Typography>
          <Box>
            {!editMode ? (
              <Button
                variant="contained"
                startIcon={<EditIcon />}
                onClick={handleEdit}
                color="primary"
              >
                Modifier
              </Button>
            ) : (
              <Stack direction="row" spacing={1}>
                <Button
                  variant="contained"
                  startIcon={<CheckIcon />}
                  onClick={handleConfirm}
                  color="success"
                >
                  Confirmer
                </Button>
                <Button
                  variant="outlined"
                  onClick={handleCancel}
                  color="secondary"
                >
                  Annuler
                </Button>
              </Stack>
            )}
                         <IconButton onClick={handleClose} sx={{ ml: 1 }}>
               <CloseIcon />
             </IconButton>
          </Box>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {/* Client Information Section */}
        <Box sx={{ maxHeight: '300px', overflow: 'auto', mb: 3 }}>
          {renderClientInfo()}
        </Box>
        
        {/* Tabs Section */}
        <Box sx={{ borderTop: 1, borderColor: 'divider', pt: 2 }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            {tabLabels.map((label, index) => (
              <Tab key={index} label={label} />
            ))}
          </Tabs>
          
                     <Box sx={{ mt: 2 }}>
             {activeTab === 0 && renderOpportunitiesTab()}
             {activeTab === 1 && renderContractsTab()}
             {activeTab === 2 && (isSociete ? renderAdherentsTab() : renderRelationsTab())}
             {activeTab === 3 && renderDocumentsTab()}
           </Box>
        </Box>
      </DialogContent>
      
              {/* Success/Error Messages */}
        <Snackbar
          open={showSuccess}
          autoHideDuration={3000}
          onClose={() => setShowSuccess(false)}
          message={successMessage}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          sx={{
            '& .MuiSnackbarContent-root': {
              backgroundColor: '#4caf50',
              color: 'white',
              fontWeight: 'bold'
            }
          }}
        />
        
        <Snackbar
          open={showError}
          autoHideDuration={3000}
          onClose={() => setShowError(false)}
          message={errorMessage}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          sx={{
            '& .MuiSnackbarContent-root': {
              backgroundColor: '#f44336',
              color: 'white',
              fontWeight: 'bold'
            }
          }}
        />

        {/* Add Opportunity Modal */}
        <AddOpportunityModal
          open={opportunityModalOpen}
          onClose={() => setOpportunityModalOpen(false)}
          clientId={clientId}
          onSuccess={handleOpportunitySuccess}
          clientType={formData.typeClient}
        />

        {/* Add Associate Modal */}
        <AddAssociateModal
          open={associateModalOpen}
          onClose={() => setAssociateModalOpen(false)}
          onSuccess={handleAssociateSuccess}
          clientId={clientId}
        />

        {/* Add Adherent Modal */}
        <AddAdherentModal
          open={adherentModalOpen}
          onClose={() => setAdherentModalOpen(false)}
          onSuccess={handleAdherentSuccess}
          clientId={clientId}
          adherentType={adherentType}
        />

        {/* Edit Opportunity Modal */}
        <EditOpportunityModal
          open={editOpportunityModalOpen}
          onClose={() => {
            setEditOpportunityModalOpen(false);
            setSelectedOpportunityForEdit(null);
          }}
          opportunityData={selectedOpportunityForEdit}
          onSuccess={handleEditOpportunitySuccess}
        />

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
                      accept=".pdf,.doc,.docx"
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

        {/* Delete Confirmation Dialog */}
        <Dialog open={deleteDialogOpen} onClose={handleCloseDeleteDialog}>
          <DialogTitle>Confirmer la suppression</DialogTitle>
          <DialogContent>
            <Typography variant="body1">
              Êtes-vous sûr de vouloir supprimer cette opportunité ?
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDeleteDialog} color="primary">
              Annuler
            </Button>
            <Button onClick={handleConfirmDelete} color="error">
              Confirmer
            </Button>
          </DialogActions>
        </Dialog>

        {/* Edit Contract Modal */}
        <Dialog 
          open={editContractModalOpen} 
          onClose={() => {
            setEditContractModalOpen(false);
            setSelectedContractForEdit(null);
            setContractDocuments([]);
            setNewContractDocuments([]);
            setDeletedContractDocuments([]);
          }}
          onBackdropClick={() => {
            setEditContractModalOpen(false);
            setSelectedContractForEdit(null);
            setContractDocuments([]);
            setNewContractDocuments([]);
            setDeletedContractDocuments([]);
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
                    value={selectedContractForEdit?.numPolice || ''}
                    onChange={(e) => setSelectedContractForEdit(prev => ({ ...prev, numPolice: e.target.value }))}
                    size="small"
                    sx={{ mb: 2 }}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                    <InputLabel>Type Contrat</InputLabel>
                    <Select
                      value={selectedContractForEdit?.typeContrat || ''}
                      onChange={(e) => setSelectedContractForEdit(prev => ({ ...prev, typeContrat: e.target.value }))}
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
                    value={selectedContractForEdit?.dateDebut || ''}
                    onChange={(e) => setSelectedContractForEdit(prev => ({ ...prev, dateDebut: e.target.value }))}
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
                    value={selectedContractForEdit?.dateFin || ''}
                    onChange={(e) => setSelectedContractForEdit(prev => ({ ...prev, dateFin: e.target.value }))}
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
                    value={selectedContractForEdit?.prime || ''}
                    onChange={(e) => setSelectedContractForEdit(prev => ({ ...prev, prime: e.target.value }))}
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
                      value={selectedContractForEdit?.idCompagnie || ''}
                      onChange={(e) => setSelectedContractForEdit(prev => ({ ...prev, idCompagnie: e.target.value }))}
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
                      value={selectedContractForEdit?.idTypeDuree || ''}
                      onChange={(e) => setSelectedContractForEdit(prev => ({ ...prev, idTypeDuree: e.target.value }))}
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
                  <Typography variant="h6" sx={{ mb: 2 }}>Documents du contrat</Typography>
                  <Button
                    variant="outlined"
                    component="label"
                    startIcon={<FileUploadIcon />}
                    sx={{ mb: 2 }}
                  >
                    Ajouter document
                    <input
                      type="file"
                      hidden
                      accept=".pdf,.doc,.docx"
                      onChange={handleContractDocumentUpload}
                    />
                  </Button>
                  
                  {/* Existing Documents */}
                  {contractDocuments.length > 0 && (
                    <>
                      <Typography variant="subtitle2" sx={{ mb: 1, mt: 2 }}>Documents existants:</Typography>
                      <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 2 }}>
                        {contractDocuments.map((doc, index) => (
                          <Chip
                            key={`existing-${doc.id || index}`}
                            label={doc.fichierNom || doc.fichierChemin || `Document ${index + 1}`}
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
            <Button onClick={() => {
              setEditContractModalOpen(false);
              // Clear all contract-related states when canceling
              setSelectedContractForEdit(null);
              setContractDocuments([]);
              setNewContractDocuments([]);
              setDeletedContractDocuments([]);
            }} color="secondary">
              Annuler
            </Button>
            <Button onClick={handleContractEditSuccess} variant="contained" color="primary">
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
      </Dialog>
    );
  };

export default ClientDetailsModal;
