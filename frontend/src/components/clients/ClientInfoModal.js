import React, { useState, useRef, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  IconButton,
  Stack,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  InputAdornment,
  Snackbar
} from '@mui/material';
import {
  Close as CloseIcon,
  Upload as UploadIcon,
  Description as DescriptionIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import StarRating from '../common/StarRating';
import { clientService } from '../../services/clientService';
import { documentService } from '../../services/documentService';

const ClientInfoModal = ({ 
  open, 
  onClose, 
  clientType, 
  onSubmit, 
  onCancel,
  onError 
}) => {
  
  const [formData, setFormData] = useState({
    // Client fields
    codeClient: '',
    adresse: '',
    tel: '',
    email: '',
    importance: '0',
    budget: '',
    proba: '',
    
    // Particulier fields
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
    optoutEmail: false,
    
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

  const [documents, setDocuments] = useState([]);
  const [adherentsFile, setAdherentsFile] = useState(null);
  const [adherentsFileObject, setAdherentsFileObject] = useState(null);
  const [adherentsFileConfirmed, setAdherentsFileConfirmed] = useState(false);
  
  // CSV data state
  const [csvAdherentsData, setCsvAdherentsData] = useState([]);
  const [csvHeaders, setCsvHeaders] = useState([]);
  
  const [errors, setErrors] = useState({});
  const [errorMessage, setErrorMessage] = useState('');
  const [showError, setShowError] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Other SOCIETE clients for societeMere dropdown
  const [otherSocieteClients, setOtherSocieteClients] = useState([]);
  
  // Load other SOCIETE clients for societeMere dropdown
  useEffect(() => {
    const loadOtherSocieteClients = async () => {
      if (open && clientType === 'SOCIETE') {
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
            return isSociete;
          });
          
          setOtherSocieteClients(otherSocietes);
        } catch (error) {
          console.error('❌ Error loading other SOCIETE clients:', error);
          setOtherSocieteClients([]);
        }
      }
    };
    
    loadOtherSocieteClients();
  }, [open, clientType]);



  // Reset form when client type changes or modal opens
  useEffect(() => {
    if (open) {
      // Reset form data when modal opens
      setFormData({
        codeClient: '',
        adresse: '',
        tel: '',
        email: '',
        importance: '0',
        budget: '',
        proba: '',
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
        optoutEmail: false,
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
                     setDocuments([]);
        setAdherentsFile(null);
        setAdherentsFileConfirmed(false);
        setCsvAdherentsData([]);
        setCsvHeaders([]);
        setErrors({});
        setErrorMessage('');
        setShowError(false);
        setHasAttemptedSubmit(false);
       
    }
  }, [open, clientType]);
  

  
  const fileInputRef = useRef();
  const adherentsFileInputRef = useRef();

  const handleInputChange = (field, value) => {
    setFormData(prev => {
      // Handle nested fields (societe.*)
      if (field.startsWith('societe.')) {
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
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  // Clear all errors when form data changes significantly
  useEffect(() => {
    // Clear errors when client type changes
    if (Object.keys(errors).length > 0) {
      setErrors({});
      setHasAttemptedSubmit(false);
    }
  }, [clientType]);

  // Only show validation errors after user has attempted to submit
  const [hasAttemptedSubmit, setHasAttemptedSubmit] = useState(false);

  // Check if form is valid in real-time
  const isFormValid = () => {
    // If user hasn't attempted to submit yet, always return true
    if (!hasAttemptedSubmit) {
      return true;
    }
    
    // Check required fields for all clients
    if (!formData.codeClient || !formData.tel || !formData.email) {
      return false;
    }
    
    // Check type-specific required fields
    if (clientType === 'PARTICULIER') {
      if (!formData.nom || !formData.prenom) {
        return false;
      }
    } else if (clientType === 'SOCIETE') {
      if (!formData.societe.nom) {
        return false;
      }
    }
    
    return true;
  };

  const handleDocumentUpload = (event) => {
    const files = Array.from(event.target.files);
    const pdfFiles = files.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length !== files.length) {
      alert('Seuls les fichiers PDF sont accept&eacute;s');
      return;
    }
    
    setDocuments(prev => [...prev, ...pdfFiles]);
  };

  const handleAdherentsUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'text/csv') {
      setAdherentsFile(file.name);
      setAdherentsFileConfirmed(false); // Reset confirmation state
      
      // Store the actual file object for later upload
      setAdherentsFileObject(file);
      
      // Parse the CSV file immediately for preview
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const csvText = e.target.result;
          const parsedData = parseCSV(csvText);
          console.log('✅ CSV parsed successfully:', parsedData);
        } catch (error) {
          console.error('❌ Error parsing CSV:', error);
          alert(`Erreur lors du parsing du CSV: ${error.message}`);
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
    setAdherentsFileObject(null);
    setAdherentsFileConfirmed(false);
    setCsvAdherentsData([]);
    setCsvHeaders([]);
    // Reset the file input
    if (adherentsFileInputRef.current) {
      adherentsFileInputRef.current.value = '';
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



  const handleSubmit = async () => {
    // Set flag that user has attempted to submit
    setHasAttemptedSubmit(true);
    
    // Validate form and show errors if invalid
    const newErrors = {};
    
    // Check required fields for all clients
    if (!formData.codeClient) newErrors.codeClient = 'Code client requis';
    if (!formData.tel) newErrors.tel = 'Téléphone requis';
    if (!formData.email) newErrors.email = 'Email requis';
    
    // Check type-specific required fields
    if (clientType === 'PARTICULIER') {
      if (!formData.nom) newErrors.nom = 'Nom requis';
      if (!formData.prenom) newErrors.prenom = 'Prénom requis';
    } else if (clientType === 'SOCIETE') {
      if (!formData.societe.nom) newErrors.societe = { nom: 'Nom de la société requis' };
    }
    
    // Set errors and return if validation fails
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    setIsSubmitting(true);
    
    // Clean up the data before sending - convert empty strings to null for numeric fields
    const cleanedData = { ...formData };
    
    // Convert empty strings to null for numeric fields
    const numericFields = ['nombreEnfants', 'budget'];
    numericFields.forEach(field => {
      if (cleanedData[field] === '') {
        cleanedData[field] = null;
      } else if (field === 'budget' && cleanedData[field]) {
        // Convert budget to number if it's not empty
        cleanedData[field] = parseFloat(cleanedData[field]);
      }
    });
    
    // Convert empty strings to null for date fields
    const dateFields = ['dateNaissance', 'date_deces', 'datePermis'];
    dateFields.forEach(field => {
      if (cleanedData[field] === '') {
        cleanedData[field] = null;
      }
    });
    
    // Handle nested SOCIETE fields
    if (clientType === 'SOCIETE' && cleanedData.societe) {
      // Convert empty strings to null for numeric fields
      const societeNumericFields = ['societeMere', 'capital'];
      societeNumericFields.forEach(field => {
        if (cleanedData.societe[field] === '') {
          cleanedData.societe[field] = null;
        } else if (field === 'capital' && cleanedData.societe[field]) {
          // Convert capital to number if it's not empty
          cleanedData.societe[field] = parseFloat(cleanedData.societe[field]);
        }
      });
      
      // Convert empty strings to null for date fields
      const societeDateFields = ['dateCreationSociete'];
      societeDateFields.forEach(field => {
        if (cleanedData.societe[field] === '') {
          cleanedData.societe[field] = null;
        }
      });
    }
    
    const submitData = {
      ...cleanedData,
      typeClient: clientType,
      documents: documents.map(doc => doc.name), // Send only file names to backend
      adherentsFile: adherentsFileConfirmed ? adherentsFile : null
    };

    // Flatten nested structure for backend compatibility
    if (clientType === 'SOCIETE' && cleanedData.societe) {
      // Move all societe fields to the top level
      Object.keys(cleanedData.societe).forEach(key => {
        submitData[key] = cleanedData.societe[key];
      });
      // Remove the nested societe object
      delete submitData.societe;
    }

    console.log('Cleaned submit data:', submitData);
    console.log('SOCIETE fields check:', {
      nom: submitData.nom,
      formeJuridique: submitData.formeJuridique,
      capital: submitData.capital,
      registreCom: submitData.registreCom,
      taxePro: submitData.taxePro,
      idFiscal: submitData.idFiscal,
      CNSS: submitData.CNSS,
      ICE: submitData.ICE,
      siteWeb: submitData.siteWeb,
      societeMere: submitData.societeMere,
      raisonSociale: submitData.raisonSociale,
      sigle: submitData.sigle,
      tribunalCommerce: submitData.tribunalCommerce,
      secteurActivite: submitData.secteurActivite,
      dateCreationSociete: submitData.dateCreationSociete,
      nomContactPrincipal: submitData.nomContactPrincipal,
      fonctionContactPrincipal: submitData.fonctionContactPrincipal
    });
    
    try {
      // First, upload all documents to get their actual file paths
      const uploadedDocuments = [];
      if (documents.length > 0) {
        console.log('📤 Uploading', documents.length, 'documents...');
        for (let i = 0; i < documents.length; i++) {
          const doc = documents[i];
          try {
            console.log(`📤 Uploading document ${i + 1}/${documents.length}:`, doc.name);
            const uploadResult = await documentService.uploadDocument(doc);
            console.log('✅ Document uploaded successfully:', uploadResult);
            // Send both the original filename and the UUID filename
            uploadedDocuments.push({
              originalName: doc.name,
              filePath: uploadResult.file_path
            });
          } catch (uploadError) {
            console.error(`❌ Failed to upload document ${doc.name}:`, uploadError);
            throw new Error(`Échec du téléchargement du document ${doc.name}: ${uploadError.message}`);
          }
        }
        console.log('✅ All documents uploaded successfully:', uploadedDocuments);
      }
      
      // Upload CSV file if available
      let uploadedCSV = null;
      if (adherentsFileObject && adherentsFileConfirmed) {
        try {
          console.log('📤 Uploading CSV file:', adherentsFileObject.name);
          const csvUploadResult = await documentService.uploadDocument(adherentsFileObject);
          console.log('✅ CSV file uploaded successfully:', csvUploadResult);
          uploadedCSV = {
            originalName: adherentsFileObject.name,
            filePath: csvUploadResult.file_path
          };
        } catch (uploadError) {
          console.error(`❌ Failed to upload CSV file ${adherentsFileObject.name}:`, uploadError);
          throw new Error(`Échec du téléchargement du fichier CSV ${adherentsFileObject.name}: ${uploadError.message}`);
        }
      }
      
      // Update the submit data with the uploaded document information
      submitData.documents = uploadedDocuments;
      submitData.adherentsFile = uploadedCSV ? uploadedCSV.originalName : null;
      submitData.adherentsFilePath = uploadedCSV ? uploadedCSV.filePath : null;
      
      await onSubmit(submitData);
    } catch (error) {
      console.error('Error in form submission:', error);
      console.log('Error type:', typeof error);
      console.log('Error object:', error);
      console.log('Error response:', error.response);
      
      // Handle different types of errors
      let errorMessage = 'Erreur lors de la soumission';
      
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
        console.log('Using error.response.data.detail:', errorMessage);
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
        console.log('Using error.response.data.message:', errorMessage);
      } else if (error.message) {
        errorMessage = error.message;
        console.log('Using error.message:', errorMessage);
      }
      
      console.log('Final error message to display:', errorMessage);
      console.log('Setting error message and showing error popup');
      setErrorMessage(errorMessage);
      setShowError(true);
      
      // Don't call onError anymore - handle everything internally
      // if (onError) {
      //   onError(error);
      // }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDocumentClick = (docName) => {
    // Find the actual file object from the documents array
    const fileIndex = documents.findIndex(doc => doc.name === docName);
    if (fileIndex !== -1) {
      const file = documents[fileIndex];
      // Create a blob URL and open the PDF in a new window
      const blob = new Blob([file], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      window.open(url, '_blank');
      // Clean up the blob URL after a delay
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
  };

  const removeDocument = (index) => {
    setDocuments(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="lg"
      fullWidth
    >
      <DialogTitle>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
                                           <Typography variant="h5" component="div">
                                  Remplir les infos n&eacute;cessaires
            </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Stack>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ mt: 2 }}>
                                           <Typography variant="h6" gutterBottom>
                                  Informations g&eacute;n&eacute;rales
            </Typography>
          
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Code Client *"
                value={formData.codeClient}
                onChange={(e) => handleInputChange('codeClient', e.target.value)}
                                 error={hasAttemptedSubmit && !!errors.codeClient}
                 helperText={hasAttemptedSubmit ? errors.codeClient : ''}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                                                                                                                                                                   label="T&eacute;l&eacute;phone *"
                value={formData.tel}
                onChange={(e) => handleInputChange('tel', e.target.value)}
                                 error={hasAttemptedSubmit && !!errors.tel}
                 helperText={hasAttemptedSubmit ? errors.tel : ''}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Email *"
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                                 error={hasAttemptedSubmit && !!errors.email}
                 helperText={hasAttemptedSubmit ? errors.email : ''}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Adresse"
                value={formData.adresse}
                onChange={(e) => handleInputChange('adresse', e.target.value)}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Budget (DH)"
                value={formData.budget}
                onChange={(e) => handleInputChange('budget', e.target.value)}
                InputProps={{
                  endAdornment: <InputAdornment position="end">DH</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                                                                                                                                                                   label="Probabilit&eacute; (%)"
                value={formData.proba}
                onChange={(e) => handleInputChange('proba', e.target.value)}
                InputProps={{
                  endAdornment: <InputAdornment position="end">%</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Importance
                </Typography>
                <StarRating
                  value={parseFloat(formData.importance) || 0}
                  onChange={(value) => handleInputChange('importance', value.toString())}
                  readOnly={false}
                  size="large"
                  showHalfStars={true}
                />
                {formData.importance && parseFloat(formData.importance) > 0 && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                                                                                                                                                                                           {formData.importance} &eacute;toile{parseFloat(formData.importance) > 1 ? 's' : ''}
                    </Typography>
                    <IconButton 
                      size="small" 
                      onClick={() => handleInputChange('importance', '0')}
                      sx={{ p: 0.5 }}
                    >
                      <CloseIcon fontSize="small" />
                    </IconButton>
                  </Box>
                )}
              </Box>
            </Grid>
          </Grid>

          {clientType === 'PARTICULIER' && (
            <>
              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                Informations particulières
              </Typography>
              
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Titre"
                    value={formData.titre}
                    onChange={(e) => handleInputChange('titre', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                                     <TextField
                     fullWidth
                     label="Nom *"
                     value={formData.nom}
                     onChange={(e) => handleInputChange('nom', e.target.value)}
                     error={hasAttemptedSubmit && !!errors.nom}
                     helperText={hasAttemptedSubmit ? errors.nom : ''}
                     required
                   />
                </Grid>
                <Grid item xs={12} md={4}>
                                     <TextField
                     fullWidth
                                                                                                                                                                                       label="Pr&eacute;nom *"
                     value={formData.prenom}
                     onChange={(e) => handleInputChange('prenom', e.target.value)}
                     error={hasAttemptedSubmit && !!errors.prenom}
                     helperText={hasAttemptedSubmit ? errors.prenom : ''}
                     required
                   />
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>Sexe</InputLabel>
                    <Select
                      value={formData.sexe}
                      onChange={(e) => handleInputChange('sexe', e.target.value)}
                      label="Sexe"
                    >
                      <MenuItem value="M">Masculin</MenuItem>
                                                                                                                                                                                                           <MenuItem value="F">F&eacute;minin</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                                                                                                                                                                                   label="Nationalit&eacute;"
                    value={formData.nationalite}
                    onChange={(e) => handleInputChange('nationalite', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Lieu de naissance"
                    value={formData.lieuNaissance}
                    onChange={(e) => handleInputChange('lieuNaissance', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Date de naissance"
                    type="date"
                    value={formData.dateNaissance}
                    onChange={(e) => handleInputChange('dateNaissance', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="CIN"
                    value={formData.cin}
                    onChange={(e) => handleInputChange('cin', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Profession"
                    value={formData.profession}
                    onChange={(e) => handleInputChange('profession', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Type Document Identité"
                    value={formData.typeDocIdentite}
                    onChange={(e) => handleInputChange('typeDocIdentite', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Situation Familiale"
                    value={formData.situationFamiliale}
                    onChange={(e) => handleInputChange('situationFamiliale', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Nombre d&apos;Enfants"
                    type="number"
                    value={formData.nombreEnfants}
                    onChange={(e) => handleInputChange('nombreEnfants', e.target.value)}
                  />
                </Grid>

                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Moyen Contact Préféré"
                    value={formData.moyenContactPrefere}
                    onChange={(e) => handleInputChange('moyenContactPrefere', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Date de Décès"
                    type="date"
                    value={formData.date_deces}
                    onChange={(e) => handleInputChange('date_deces', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Date Permis"
                    type="date"
                    value={formData.datePermis}
                    onChange={(e) => handleInputChange('datePermis', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>Opt-out Téléphone</InputLabel>
                    <Select
                      value={formData.optoutTelephone}
                      onChange={(e) => handleInputChange('optoutTelephone', e.target.value)}
                      label="Opt-out Téléphone"
                    >
                      <MenuItem value={false}>Non</MenuItem>
                      <MenuItem value={true}>Oui</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>Opt-out Email</InputLabel>
                    <Select
                      value={formData.optoutEmail}
                      onChange={(e) => handleInputChange('optoutEmail', e.target.value)}
                      label="Opt-out Email"
                    >
                      <MenuItem value={false}>Non</MenuItem>
                      <MenuItem value={true}>Oui</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </>
          )}

          {clientType === 'SOCIETE' && (
            <>
              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                                                                                                                                                           Informations de la soci&eacute;t&eacute;
              </Typography>
              
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Nom de la société *"
                    value={formData.societe.nom}
                    onChange={(e) => handleInputChange('societe.nom', e.target.value)}
                    error={hasAttemptedSubmit && !!errors.societe?.nom}
                    helperText={hasAttemptedSubmit ? errors.societe?.nom : ''}
                    required
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Forme juridique"
                    value={formData.societe.formeJuridique}
                    onChange={(e) => handleInputChange('societe.formeJuridique', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Capital"
                    value={formData.societe.capital}
                    onChange={(e) => handleInputChange('societe.capital', e.target.value)}
                    type="number"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Registre de commerce"
                    value={formData.societe.registreCom}
                    onChange={(e) => handleInputChange('societe.registreCom', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Taxe professionnelle"
                    value={formData.societe.taxePro}
                    onChange={(e) => handleInputChange('societe.taxePro', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Identifiant fiscal"
                    value={formData.societe.idFiscal}
                    onChange={(e) => handleInputChange('societe.idFiscal', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="CNSS"
                    value={formData.societe.CNSS}
                    onChange={(e) => handleInputChange('societe.CNSS', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="ICE"
                    value={formData.societe.ICE}
                    onChange={(e) => handleInputChange('societe.ICE', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Site web"
                    value={formData.societe.siteWeb}
                    onChange={(e) => handleInputChange('societe.siteWeb', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Raison sociale"
                    value={formData.societe.raisonSociale}
                    onChange={(e) => handleInputChange('societe.raisonSociale', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Sigle"
                    value={formData.societe.sigle}
                    onChange={(e) => handleInputChange('societe.sigle', e.target.value)}
                  />
                </Grid>
                                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Tribunal de commerce"
                    value={formData.societe.tribunalCommerce}
                    onChange={(e) => handleInputChange('societe.tribunalCommerce', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Secteur d&apos;activité"
                    value={formData.societe.secteurActivite}
                    onChange={(e) => handleInputChange('societe.secteurActivite', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Date de création"
                    type="date"
                    value={formData.societe.dateCreationSociete}
                    onChange={(e) => handleInputChange('societe.dateCreationSociete', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Nom du contact principal"
                    value={formData.societe.nomContactPrincipal}
                    onChange={(e) => handleInputChange('societe.nomContactPrincipal', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Fonction du contact principal"
                    value={formData.societe.fonctionContactPrincipal}
                    onChange={(e) => handleInputChange('societe.fonctionContactPrincipal', e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Société mère</InputLabel>
                                         <Select
                       value={formData.societe.societeMere || ''}
                       onChange={(e) => handleInputChange('societe.societeMere', e.target.value)}
                       label="Société mère"
                     >
                       <MenuItem value="">
                         <em>Aucune société mère</em>
                       </MenuItem>
                       {otherSocieteClients.map((societe) => (
                         <MenuItem key={societe.id} value={societe.id}>
                           {societe.nom || societe.codeClient}
                         </MenuItem>
                       ))}
                     </Select>
                     {/* Show selected societe name if one is selected */}
                     {formData.societe.societeMere && (
                       <Typography variant="caption" color="text.secondary" display="block">
                         Société mère sélectionnée: {otherSocieteClients.find(s => s.id === formData.societe.societeMere)?.nom || 'ID: ' + formData.societe.societeMere}
                       </Typography>
                     )}
                    
                  </FormControl>
                </Grid>

              </Grid>
            </>
          )}

          {/* Documents Section */}
          <Box sx={{ mt: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Documents
            </Typography>
            
            <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
              <Button
                variant="outlined"
                startIcon={<UploadIcon />}
                onClick={() => fileInputRef.current.click()}
                sx={{ backgroundColor: '#ffeb3b', color: 'black' }}
              >
                Importer Document
              </Button>
              
              {clientType === 'SOCIETE' && (
                <Button
                  variant="outlined"
                  startIcon={<UploadIcon />}
                  onClick={() => adherentsFileInputRef.current.click()}
                  sx={{ backgroundColor: '#1976d2', color: 'white' }}
                >
                  Importer Adherents
                </Button>
              )}
            </Stack>

            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf"
              onChange={handleDocumentUpload}
              style={{ display: 'none' }}
            />
            
            <input
              ref={adherentsFileInputRef}
              type="file"
              accept=".csv"
              onChange={handleAdherentsUpload}
              style={{ display: 'none' }}
            />

            {/* Documents List */}
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Documents choisis:
              </Typography>
              {documents.length === 0 ? (
                                        <Typography variant="body2" color="text.secondary">
                                                                                                           Aucun document import&eacute;
                        </Typography>
              ) : (
                <Stack direction="row" spacing={1} flexWrap="wrap">
                                   {documents.map((doc, index) => (
                   <Chip
                     key={index}
                     label={doc.name}
                     onClick={() => handleDocumentClick(doc.name)}
                     onDelete={() => removeDocument(index)}
                     icon={<DescriptionIcon />}
                     sx={{ mb: 1 }}
                   />
                 ))}
                </Stack>
              )}
            </Box>

                         {/* Adherents File Validation */}
             {clientType === 'SOCIETE' && adherentsFile && (
               <Box sx={{ mt: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1, backgroundColor: '#f5f5f5' }}>
                 <Typography variant="subtitle2" gutterBottom>
                   Fichier adherents sélectionné: {adherentsFile}
                 </Typography>
                 
                                   {/* CSV File Info */}
                  <Box sx={{ mt: 2, mb: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      <strong>Fichier CSV sélectionné:</strong> {adherentsFile}
                    </Typography>
                  </Box>
                 
                 {!adherentsFileConfirmed ? (
                   <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
                     <Button
                       variant="contained"
                       color="success"
                       size="small"
                       onClick={confirmAdherentsFile}
                       startIcon={<CheckCircleIcon />}
                     >
                       Confirmer
                     </Button>
                     <Button
                       variant="outlined"
                       color="error"
                       size="small"
                       onClick={cancelAdherentsFile}
                     >
                       Annuler
                     </Button>
                   </Stack>
                 ) : (
                   <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                     <CheckCircleIcon color="success" />
                     <Typography variant="body2" color="success.main">
                       Fichier confirmé et prêt pour l&apos;import
                     </Typography>
                   </Box>
                 )}
               </Box>
             )}
          </Box>
        </Box>
      </DialogContent>
      
      <DialogActions sx={{ p: 3 }}>
        <Stack direction="row" spacing={2} sx={{ width: '100%', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="body2" color="text.secondary">
                             {documents.length === 0 ? 'Aucun document importé' : `${documents.length} document(s) importé(s)`}
            </Typography>
          </Box>
          
          <Stack direction="row" spacing={2}>
            <Button onClick={onCancel} variant="outlined">
              Annuler
            </Button>
            <Button 
              onClick={handleSubmit} 
              variant="contained" 
              color="primary"
              disabled={!isFormValid() || isSubmitting}
            >
                                                           {isSubmitting ? 'Création...' : 'Confirmer'}
            </Button>
          </Stack>
        </Stack>
             </DialogActions>
       
               {/* Error Message Snackbar */}
               <Snackbar
         open={showError}
         autoHideDuration={10000}
         onClose={() => setShowError(false)}
         message={errorMessage}
         anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
         sx={{
           zIndex: 9999, // Ensure it appears above the modal
           '& .MuiSnackbarContent-root': {
             backgroundColor: '#f44336',
             color: 'white',
             fontWeight: 'bold'
           }
         }}
       />
     </Dialog>
   );
 };

export default ClientInfoModal;
