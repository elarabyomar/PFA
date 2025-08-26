import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert,
  Pagination,
  Card,
  CardContent,
  CardHeader,
  IconButton,
  Tooltip,
  Badge,
  Tabs,
  Tab,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  OutlinedInput,
  FormHelperText,
  Checkbox,
  FormControlLabel
} from '@mui/material';
import {
  TableChart as TableIcon,
  Storage as DatabaseIcon,
  Info as InfoIcon,
  DataObject as DataIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { useApi } from '../../hooks/useApi';
import { databaseExplorerService } from '../../services/databaseExplorerService';

const DatabaseExplorerPage = () => {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [tableStructure, setTableStructure] = useState(null);
  const [tableData, setTableData] = useState(null);
  const [tableDisplayLabels, setTableDisplayLabels] = useState({}); // Pour stocker les libellés d'affichage
  const [tableDescriptions, setTableDescriptions] = useState({}); // Pour stocker les descriptions des colonnes
  const [tableForeignKeys, setTableForeignKeys] = useState({}); // Pour stocker les données des clés étrangères
  const [activeTab, setActiveTab] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(50);
  
  // États pour les opérations CRUD
  const [crudModalOpen, setCrudModalOpen] = useState(false);
  const [crudMode, setCrudMode] = useState('create'); // 'create' ou 'edit'
  const [selectedRow, setSelectedRow] = useState(null);
  const [formData, setFormData] = useState({});
  
  const { execute, loading, error } = useApi();

  // Charger la liste des tables au montage
  useEffect(() => {
    loadTables();
  }, []);

  // Charger la structure et les données quand une table est sélectionnée
  useEffect(() => {
    if (selectedTable) {
      loadTableStructure(selectedTable);
      loadTableData(selectedTable, 0);
      setCurrentPage(1);
    }
  }, [selectedTable]);

  const loadTables = async () => {
    try {
      const result = await execute(() => databaseExplorerService.getAllTables());
      setTables(result.tables || []);
    } catch (error) {
      console.error('Erreur lors du chargement des tables:', error);
    }
  };

  const loadTableStructure = async (tableName) => {
    try {
      const result = await execute(() => databaseExplorerService.getTableStructure(tableName));
      setTableStructure(result);
      
      // Récupérer les libellés d'affichage pour cette table
      try {
        const labelsResult = await execute(() => databaseExplorerService.getTableDisplayLabels(tableName));
        setTableDisplayLabels(prev => ({
          ...prev,
          [tableName]: labelsResult.labels || {}
        }));
      } catch (labelError) {
        console.warn('Impossible de récupérer les libellés d\'affichage:', labelError);
        // Utiliser les noms de colonnes par défaut si pas de libellés
        const defaultLabels = {};
        if (result?.columns) {
          result.columns.forEach(col => {
            defaultLabels[col.name] = col.name;
          });
        }
        setTableDisplayLabels(prev => ({
          ...prev,
          [tableName]: defaultLabels
        }));
      }
      
             // Récupérer les descriptions des colonnes depuis le CSV
       try {
         const descriptionsResult = await execute(() => databaseExplorerService.getTableColumnDescriptions(tableName));
         console.log(`DEBUG: Descriptions reçues pour ${tableName}:`, descriptionsResult);
         
         if (descriptionsResult.descriptions && Object.keys(descriptionsResult.descriptions).length > 0) {
           console.log(`✅ Descriptions trouvées pour ${tableName}:`, descriptionsResult.descriptions);
           setTableDescriptions(prev => ({
             ...prev,
             [tableName]: descriptionsResult.descriptions
           }));
         } else {
           console.warn(`⚠️  Aucune description reçue pour la table ${tableName}`);
           console.warn(`   Réponse complète:`, descriptionsResult);
           
           // Utiliser les noms de colonnes par défaut si pas de descriptions
           const defaultDescriptions = {};
           if (result?.columns) {
             result.columns.forEach(col => {
               defaultDescriptions[col.name] = `Colonne ${col.name}`;
             });
           }
           setTableDescriptions(prev => ({
             ...prev,
             [tableName]: defaultDescriptions
           }));
         }
       } catch (descError) {
         console.error('❌ Erreur lors de la récupération des descriptions des colonnes:', descError);
         console.error('   Détails de l\'erreur:', descError.message);
         
         // Utiliser les noms de colonnes par défaut si pas de descriptions
         const defaultDescriptions = {};
         if (result?.columns) {
           result.columns.forEach(col => {
             defaultDescriptions[col.name] = `Colonne ${col.name}`;
           });
         }
         setTableDescriptions(prev => ({
           ...prev,
           [tableName]: defaultDescriptions
         }));
       }

      // Récupérer les données des clés étrangères
      try {
        console.log(`🔍 Chargement des clés étrangères pour la table: ${tableName}`);
        const foreignKeysResult = await execute(() => databaseExplorerService.getTableForeignKeyData(tableName));
        console.log(`📊 Résultat des clés étrangères:`, foreignKeysResult);
        
        if (foreignKeysResult.foreign_keys_data) {
          console.log(`✅ Clés étrangères trouvées:`, Object.keys(foreignKeysResult.foreign_keys_data));
          for (const [columnName, fkData] of Object.entries(foreignKeysResult.foreign_keys_data)) {
            console.log(`   ${columnName} → ${fkData.referenced_table}: ${fkData.count || 0} valeurs`);
            console.log(`   🔍 Données de ${columnName}:`, fkData.data);
          }
          
          // CORRECTION: Vérifier que les données sont bien stockées
          const newForeignKeys = foreignKeysResult.foreign_keys_data || {};
          console.log(`💾 Stockage des clés étrangères:`, newForeignKeys);
          
          setTableForeignKeys(prev => {
            const updated = {
              ...prev,
              [tableName]: newForeignKeys
            };
            console.log(`🔄 État des clés étrangères mis à jour:`, updated);
            return updated;
          });
        } else {
          console.log(`⚠️  Aucune donnée de clé étrangère trouvée`);
          console.log(`   Réponse complète:`, foreignKeysResult);
        }
        
        // CORRECTION: Charger directement les données des tables référencées
        console.log(`🔍 Chargement direct des données des tables référencées pour: ${tableName}`);
        
        if (result?.foreign_keys && result.foreign_keys.length > 0) {
          console.log(`🔍 ${result.foreign_keys.length} clés étrangères trouvées dans la structure`);
          
          for (const fk of result.foreign_keys) {
            console.log(`🔍 Chargement des données de ${fk.referenced_table} pour ${fk.column}`);
            await loadReferencedTableData(tableName, fk.column, fk.referenced_table);
          }
        }
        
        // SUPPRIMER: L'ancien code qui ne fonctionne pas
        // try {
        //   console.log(`🔍 Chargement des données des tables master pour: ${tableName}`);
        //   const masterTablesResult = await execute(() => databaseExplorerService.getMasterTablesData(tableName));
        //   console.log(`📊 Résultat des tables master:`, masterTablesResult);
        //   
        //   if (masterTablesResult.master_tables_data) {
        //     console.log(`✅ Tables master trouvées:`, Object.keys(masterTablesResult.master_tables_data));
        //     
        //     // Fusionner avec les données des clés étrangères existantes
        //     setTableForeignKeys(prev => {
        //       const current = prev[tableName] || {};
        //       const masterData = masterTablesResult.master_tables_data || {};
        //       
        //       // Fusionner en priorisant les données des tables master
        //       const merged = { ...current };
        //       for (const [columnName, masterFkData] of Object.entries(masterData)) {
        //         if (masterFkData.data && masterFkData.data.length > 0) {
        //           console.log(`🔄 Fusion des données master pour ${columnName}: ${masterFkData.data.length} valeurs`);
        //           merged[columnName] = masterFkData;
        //         }
        //       }
        //       
        //       const updated = {
        //         ...prev,
        //         [tableName]: merged
        //       };
        //       console.log(`🔄 État final des clés étrangères:`, updated);
        //       return updated;
        //     });
        //   }
        // } catch (masterError) {
        //   console.warn('⚠️  Erreur lors du chargement des tables master:', masterError);
        //   
        //   // CORRECTION: Fallback - charger directement depuis la structure
        //   console.log(`🔄 Fallback: Chargement direct depuis la structure de la table`);
        //   if (result?.foreign_keys && result.foreign_keys.length > 0) {
        //     console.log(`🔍 ${result.foreign_keys.length} clés étrangères trouvées dans la structure`);
        //             
        //     for (const fk of result.foreign_keys) {
        //       console.log(`🔍 Chargement des données de ${fk.referenced_table} pour ${fk.column}`);
        //       await loadReferencedTableData(tableName, fk.column, fk.referenced_table);
        //     }
        //   }
        // }
      } catch (fkError) {
        console.error('❌ Erreur lors de la récupération des clés étrangères:', fkError);
        setTableForeignKeys(prev => ({
          ...prev,
          [tableName]: {}
        }));
      }
    } catch (error) {
      console.error('Erreur lors du chargement de la structure:', error);
    }
  };

  const loadTableData = async (tableName, offset = 0) => {
    try {
      const result = await execute(() => databaseExplorerService.getTableData(tableName, pageSize, offset));
      setTableData(result);
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
    }
  };

  // CORRECTION: Fonction pour charger directement les données des tables référencées
  const loadReferencedTableData = async (tableName, columnName, referencedTable) => {
    try {
      console.log(`🔍 Chargement direct des données de ${referencedTable} pour ${columnName}`);
      
      // Utiliser l'endpoint de données de table existant
      const dataResult = await execute(() => databaseExplorerService.getTableData(referencedTable, 100, 0));
      
      if (dataResult && dataResult.data && dataResult.data.length > 0) {
        console.log(`✅ ${dataResult.data.length} lignes chargées de ${referencedTable}`);
        
        // Mettre à jour les données des clés étrangères
        setTableForeignKeys(prev => {
          const current = prev[tableName] || {};
          const updated = {
            ...current,
            [columnName]: {
              referenced_table: referencedTable,
              referenced_column: 'id',
              data: dataResult.data,
              count: dataResult.data.length
            }
          };
          
          return {
            ...prev,
            [tableName]: updated
          };
        });
        
        return dataResult.data;
      } else {
        console.log(`⚠️  Aucune donnée trouvée dans ${referencedTable}`);
        return [];
      }
    } catch (error) {
      console.error(`❌ Erreur lors du chargement de ${referencedTable}:`, error);
      return [];
    }
  };

  const handleTableSelect = (tableName) => {
    setSelectedTable(tableName);
    setActiveTab(0);
  };

  const handlePageChange = (event, page) => {
    const offset = (page - 1) * pageSize;
    loadTableData(selectedTable, offset);
    setCurrentPage(page);
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const getTableTypeColor = (tableType) => {
    // Déterminer la couleur basée sur le type de table
    switch (tableType) {
      case 'MASTER':
        return 'primary';
      case 'REFERENCE':
        return 'secondary';
      case 'TRANSACTIONAL':
        return 'warning';
      default:
        return 'default';
    }
  };

  // Obtenir les données d'une clé étrangère
  const getForeignKeyData = (columnName) => {
    if (!selectedTable || !tableForeignKeys[selectedTable]) {
      return { data: [], count: 0 };
    }
    
    const fkDataFromApi = tableForeignKeys[selectedTable][columnName];
    
    if (fkDataFromApi && fkDataFromApi.data && fkDataFromApi.data.length > 0) {
      return fkDataFromApi;
    }
    
    // Fallback vers la structure
    const fkFromStructure = tableStructure?.foreign_keys?.find(fk => fk.column === columnName);
    
    if (fkFromStructure) {
      return { data: [], count: 0, error: 'Données non chargées' };
    }
    
    return { data: [], count: 0 };
  };

  // Obtenir le libellé d'affichage pour une valeur de clé étrangère
  const getForeignKeyDisplayLabel = (columnName, value) => {
    // Récupérer les données de la clé étrangère
    const fkData = tableForeignKeys[selectedTable]?.[columnName];
    
    console.log(`🔍 getForeignKeyDisplayLabel: ${columnName} = ${value}`);
    console.log(`🔍 fkData:`, fkData);
    
    if (!fkData || !fkData.data) {
      console.log(`⚠️  Pas de données FK pour ${columnName}`);
      return value || 'N/A';
    }
    
    // Trouver l'élément correspondant à la valeur
    const item = fkData.data.find(item => item.id == value);
    
    console.log(`🔍 Item trouvé:`, item);
    
    if (!item) {
      console.log(`⚠️  Aucun item trouvé pour la valeur ${value}`);
      return value || 'N/A';
    }
    
    // CORRECTION: Créer un libellé convivial basé sur le type de table
    const tableName = fkData.referenced_table;
    console.log(`🔍 Table référencée: ${tableName}`);
    
    let displayLabel = '';
    
    // CORRECTION: Logique générale pour toutes les tables
    if (tableName === 'compagnies') {
      displayLabel = `${item.nom || item.codeCIE || item.raisonSociale || 'Compagnie'} (${item.codeCIE || 'N/A'})`;
    } else if (tableName === 'users') {
      displayLabel = `${item.prenom || 'N/A'} ${item.nom || 'N/A'} (${item.email || 'N/A'})`;
    } else if (tableName === 'clients') {
      // CORRECTION: Afficher le code client et le type client
      console.log(`🔍 Données du client:`, item);
      
      // Récupérer les champs importants
      const codeClient = item.codeClient || item.code || item.id || 'ID';
      const typeClient = item.typeClient || item.type || '';
      const nomClient = item.nom || item.raisonSociale || item.prenom || '';
      
      // Construire le libellé d'affichage
      if (codeClient && codeClient !== 'ID' && typeClient) {
        // Priorité: Code Client + Type Client
        displayLabel = `${codeClient} - ${typeClient}`;
      } else if (codeClient && codeClient !== 'ID') {
        // Fallback: Seulement le code client
        displayLabel = `${codeClient}`;
      } else if (nomClient) {
        // Fallback: Nom + ID
        displayLabel = `${nomClient} (ID: ${item.id})`;
      } else {
        // Dernier fallback: Client + ID
        displayLabel = `Client ${item.id}`;
      }
      
      console.log(`🔍 Libellé client généré: ${displayLabel}`);
    } else if (tableName === 'particuliers') {
      const prenom = item.prenom || '';
      const nom = item.nom || '';
      const cin = item.cin || item.id || '';
      
      if (prenom || nom) {
        displayLabel = `${prenom} ${nom}`.trim() + (cin ? ` (${cin})` : '');
      } else {
        displayLabel = `Particulier ${cin}`;
      }
    } else if (tableName === 'societes') {
      const raisonSociale = item.raisonSociale || item.sigle || '';
      const registreCom = item.registreCom || item.id || '';
      
      if (raisonSociale) {
        displayLabel = `${raisonSociale} (${registreCom})`;
      } else {
        displayLabel = `Société ${registreCom}`;
      }
    } else if (tableName === 'flotte_auto') {
      displayLabel = `${item.marque || 'N/A'} ${item.modele || 'N/A'} (${item.matricule || 'N/A'})`;
    } else if (tableName === 'assure_sante') {
      displayLabel = `${item.prenom || 'N/A'} ${item.nom || 'N/A'} (${item.cin || 'N/A'})`;
    } else if (tableName === 'type_relation') {
      displayLabel = item.libelle || item.codeTypeRelation || 'N/A';
    } else {
      // CORRECTION: Fallback général intelligent pour toutes les autres tables
      console.log(`🔍 Table ${tableName} non spécifiquement gérée, utilisation du fallback général`);
      
      // Essayer de trouver les meilleurs champs pour l'affichage
      const displayFields = ['nom', 'prenom', 'libelle', 'description', 'code', 'raisonSociale', 'sigle', 'marque', 'modele'];
      let foundField = null;
      
      for (const field of displayFields) {
        if (item[field] && item[field] !== 'N/A' && item[field] !== '') {
          foundField = field;
          break;
        }
      }
      
      if (foundField) {
        displayLabel = `${item[foundField]} (ID: ${item.id})`;
      } else {
        // Dernier recours: afficher l'ID avec le nom de la table
        displayLabel = `${tableName.charAt(0).toUpperCase() + tableName.slice(1)} ${item.id}`;
      }
      
      console.log(`🔍 Fallback général utilisé: ${displayLabel}`);
    }
    
    console.log(`✅ Libellé généré: ${displayLabel}`);
    return displayLabel;
  };

  // Vérifier si une colonne est de type boolean
  const isBooleanColumn = (column) => {
    if (!column || !column.type) return false;
    const type = column.type.toLowerCase();
    return type === 'boolean' || type.includes('boolean') || type === 'bool';
  };

  // Obtenir les informations détaillées sur le type d'une colonne
  const getTypeInfo = (column) => {
    if (!column || !column.type) return {};
    
    const type = column.type.toLowerCase();
    const info = {};
    
    if (type.includes('varchar') || type.includes('character varying')) {
      info.examples = 'Texte libre';
      info.placeholder = 'Entrez du texte...';
      if (column.max_length) {
        info.format = `Max ${column.max_length} caractères`;
      }
    } else if (type.includes('integer') || type.includes('int')) {
      info.examples = 'Nombre entier (ex: 123)';
      info.placeholder = 'Entrez un nombre entier...';
    } else if (type.includes('numeric') || type.includes('decimal')) {
      info.examples = 'Nombre décimal (ex: 123.45)';
      info.placeholder = 'Entrez un nombre décimal...';
    } else if (type.includes('date')) {
      info.examples = 'Date (YYYY-MM-DD)';
      info.format = 'Format: AAAA-MM-JJ';
    } else if (type.includes('timestamp')) {
      info.examples = 'Date et heure';
      info.format = 'Format: AAAA-MM-JJ HH:MM:SS';
    } else if (type === 'boolean' || type.includes('boolean')) {
      info.examples = 'OUI (cochée) / NON (non cochée)';
    } else if (type.includes('text')) {
      info.examples = 'Texte long';
      info.placeholder = 'Entrez du texte...';
    }
    
    return info;
  };

  const formatDataType = (column) => {
    let type = column.type;
    
    if (column.max_length) {
      type += `(${column.max_length})`;
    } else if (column.precision && column.scale) {
      type += `(${column.precision},${column.scale})`;
    } else if (column.precision) {
      type += `(${column.precision})`;
    }
    
    return type;
  };

  const isPrimaryKey = (columnName) => {
    return tableStructure?.primary_keys?.includes(columnName);
  };

  const isForeignKey = (columnName) => {
    // Vérifier d'abord dans les données des clés étrangères du CSV
    const isFkInCsv = tableForeignKeys[selectedTable]?.[columnName] !== undefined;
    
    // Vérifier aussi dans la structure de la table (contraintes de base de données)
    const isFkInStructure = tableStructure?.foreign_keys?.some(fk => fk.column === columnName);
    
    return isFkInCsv || isFkInStructure;
  };

  const getForeignKeyInfo = (columnName) => {
    // Vérifier d'abord dans la structure de la table (contraintes de base de données)
    const fkFromStructure = tableStructure?.foreign_keys?.find(fk => fk.column === columnName);
    
    if (fkFromStructure) {
      return fkFromStructure;
    }
    
    // Si pas trouvé dans la structure, vérifier dans les données CSV
    const fkFromCsv = tableForeignKeys[selectedTable]?.[columnName];
    if (fkFromCsv) {
      return {
        column: columnName,
        referenced_table: fkFromCsv.referenced_table,
        referenced_column: 'id'
      };
    }
    
    return null;
  };

  // Fonctions CRUD
  const handleCreateRow = () => {
    setCrudMode('create');
    setSelectedRow(null);
    setFormData({});
    setCrudModalOpen(true);
  };

  const handleCreateRowSubmit = async () => {
    try {
      console.log('🔍 Données à insérer:', formData);
      
      // CORRECTION: Valider et formater les données avant envoi
      const validatedData = {};
      for (const [key, value] of Object.entries(formData)) {
        if (value === '') {
          // Ignorer les champs vides
          continue;
        }
        
        // Détecter et valider les dates
        if (key.toLowerCase().includes('date') && typeof value === 'string') {
          try {
            // Vérifier si c'est une date valide
            const date = new Date(value);
            if (!isNaN(date.getTime())) {
              // Formater la date au format YYYY-MM-DD
              validatedData[key] = date.toISOString().split('T')[0];
              console.log(`✅ Date validée: ${key} = ${value} → ${validatedData[key]}`);
            } else {
              validatedData[key] = value;
              console.log(`⚠️  Date invalide: ${key} = ${value}`);
            }
          } catch (e) {
            validatedData[key] = value;
            console.log(`❌ Erreur validation date ${key}: ${e}`);
          }
        } else {
          validatedData[key] = value;
        }
      }
      
      console.log('🔍 Données validées:', validatedData);
      
      const result = await execute(() => 
        databaseExplorerService.createTableRow(selectedTable, validatedData)
      );
      
      console.log('✅ Ligne créée:', result);
      
      // Actualiser les données
      loadTableData(selectedTable, 0);
      
      // Fermer le modal
      handleCloseCrudModal();
      
      // Réinitialiser le formulaire
      setFormData({});
      
    } catch (error) {
      console.error('❌ Erreur lors de la création:', error);
      // L'erreur sera affichée par le composant useApi
    }
  };

  const handleEditRow = (row) => {
    setCrudMode('edit');
    setSelectedRow(row);
    setFormData({ ...row });
    setCrudModalOpen(true);
  };

  const handleDeleteRow = async (row) => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer cette ligne ?`)) {
      try {
        await execute(() => 
          databaseExplorerService.deleteTableRow(selectedTable, row.id)
        );
        // Recharger les données
        loadTableData(selectedTable, (currentPage - 1) * pageSize);
      } catch (error) {
        console.error('Erreur lors de la suppression:', error);
      }
    }
  };

  const handleSubmitCrud = async () => {
    try {
      // Préparer les données avec conversion de types
      const processedData = { ...formData };
      
      // Convertir les types selon la structure de la table
      if (tableStructure?.columns) {
        tableStructure.columns.forEach(column => {
          if (column.name in processedData) {
            const value = processedData[column.name];
            
            // Conversion des types
            if (isBooleanColumn(column)) {
              // Convertir 'OUI'/'NON' en true/false
              if (value === 'OUI' || value === 'YES' || value === 'true' || value === true) {
                processedData[column.name] = true;
              } else if (value === 'NON' || value === 'NO' || value === 'false' || value === false) {
                processedData[column.name] = false;
              } else if (value === '') {
                processedData[column.name] = null; // Pour les champs nullable
              }
            } else if (column.type.includes('date') || column.type.includes('timestamp')) {
              // CORRECTION: Gestion spéciale des dates
              if (value && value !== '') {
                try {
                  // Si c'est déjà une date valide, la formater
                  if (value instanceof Date) {
                    processedData[column.name] = value.toISOString().split('T')[0];
                  } else if (typeof value === 'string') {
                    // Vérifier si c'est une date valide
                    const date = new Date(value);
                    if (!isNaN(date.getTime())) {
                      processedData[column.name] = date.toISOString().split('T')[0];
                      console.log(`✅ Date formatée: ${column.name} = ${value} → ${processedData[column.name]}`);
                    } else {
                      console.log(`⚠️  Date invalide: ${column.name} = ${value}`);
                    }
                  }
                } catch (e) {
                  console.log(`❌ Erreur formatage date ${column.name}: ${e}`);
                }
              }
            } else if (column.type.includes('int') || column.type.includes('numeric')) {
              // Convertir en nombre si possible
              if (value !== '' && value !== null && value !== undefined) {
                const numValue = parseFloat(value);
                if (!isNaN(numValue)) {
                  processedData[column.name] = numValue;
                }
              }
            }
          }
        });
      }
      
      console.log('🔍 Données traitées avant envoi:', processedData);
      
      if (crudMode === 'create') {
        const result = await execute(() => 
          databaseExplorerService.createTableRow(selectedTable, processedData)
        );
        console.log('✅ Ligne créée:', result);
      } else {
        const result = await execute(() => 
          databaseExplorerService.updateTableRow(selectedTable, selectedRow.id, processedData)
        );
        console.log('✅ Ligne modifiée:', result);
      }
      
      // Actualiser les données
      loadTableData(selectedTable, (currentPage - 1) * pageSize);
      
      // Fermer le modal
      handleCloseCrudModal();
      
      // Réinitialiser le formulaire
      setFormData({});
      setSelectedRow(null);
      
    } catch (error) {
      console.error('❌ Erreur lors de la soumission:', error);
    }
  };

  const handleCloseCrudModal = () => {
    setCrudModalOpen(false);
    setFormData({});
    setSelectedRow(null);
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Explorateur de Base de Données
        </Typography>
        <Tooltip title="Actualiser">
          <IconButton onClick={loadTables} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Typography variant="body1" color="text.secondary" paragraph>
        Explorez la structure et les données de tous les tableaux créés lors du premier lancement d&apos;Insurforce.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Liste des tables à gauche */}
        <Grid item xs={12} md={3}>
          <Paper elevation={2}>
            <CardHeader
              title="Tables"
              avatar={<DatabaseIcon />}
              action={
                <Badge badgeContent={tables.length} color="primary">
                  <TableIcon />
                </Badge>
              }
            />
            <Divider />
            <List sx={{ maxHeight: '70vh', overflow: 'auto' }}>
              {loading ? (
                <Box display="flex" justifyContent="center" p={2}>
                  <CircularProgress size={24} />
                </Box>
              ) : (
                tables.map((table) => (
                  <ListItem key={table.name} disablePadding>
                    <ListItemButton
                      selected={selectedTable === table.name}
                      onClick={() => handleTableSelect(table.name)}
                    >
                      <ListItemText
                        primary={table.name}
                        secondary={
                          <Chip
                            label={table.type}
                            size="small"
                            color={getTableTypeColor(table.type)}
                            variant="outlined"
                          />
                        }
                      />
                    </ListItemButton>
                  </ListItem>
                ))
              )}
            </List>
          </Paper>
        </Grid>

        {/* Détails de la table sélectionnée à droite */}
        <Grid item xs={12} md={9}>
          {selectedTable ? (
            <Paper elevation={2}>
              <CardHeader
                title={`Table: ${selectedTable}`}
                avatar={<TableIcon />}
                action={
                  <Chip
                    label={`${tableData?.pagination?.total_rows || 0} lignes`}
                    color="info"
                    variant="outlined"
                  />
                }
              />
              <Divider />
              
              <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={activeTab} onChange={handleTabChange}>
                  <Tab label="Structure" icon={<InfoIcon />} />
                  <Tab label="Données" icon={<DataIcon />} />
                </Tabs>
              </Box>

              {/* Onglet Structure */}
              {activeTab === 0 && (
                <Box p={3}>
                  {tableStructure ? (
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <Typography variant="h6" gutterBottom>
                          Colonnes ({tableStructure.column_count})
                        </Typography>
                        <TableContainer>
                          <Table size="small">
                                                         <TableHead>
                               <TableRow>
                                 <TableCell>Nom</TableCell>
                                 <TableCell>Description</TableCell>
                                 <TableCell>Type</TableCell>
                                 <TableCell>Nullable</TableCell>
                                 <TableCell>Clés</TableCell>
                               </TableRow>
                             </TableHead>
                            <TableBody>
                              {tableStructure.columns.map((column) => {
                                return (
                                <TableRow key={column.name}>
                                  <TableCell>
                                    <Typography variant="body2" fontWeight="bold">
                                      {column.name}
                                    </Typography>
                                  </TableCell>
                                    <TableCell>
                                      <Typography variant="body2" color="text.secondary">
                                        {(() => {
                                          const description = tableDescriptions[selectedTable]?.[column.name];
                                          console.log(`DEBUG: Affichage description pour ${column.name}:`, description);
                                          return description || '-';
                                        })()}
                                      </Typography>
                                    </TableCell>
                                  <TableCell>
                                    <Chip
                                      label={formatDataType(column)}
                                      size="small"
                                      variant="outlined"
                                    />
                                  </TableCell>
                                   <TableCell>
                                     <Chip
                                       label={column.nullable ? 'OUI' : 'NON'}
                                       size="small"
                                       color={column.nullable ? 'default' : 'error'}
                                     />
                                   </TableCell>
                                   <TableCell>
                                    <Box display="flex" gap={1}>
                                      {isPrimaryKey(column.name) && (
                                        <Chip
                                          label="PK"
                                          size="small"
                                          color="primary"
                                        />
                                      )}
                                      {isForeignKey(column.name) && (
                                        <Tooltip title={`Référence: ${getForeignKeyInfo(column.name)?.referenced_table}.${getForeignKeyInfo(column.name)?.referenced_column}`}>
                                          <Chip
                                            label="FK"
                                            size="small"
                                            color="secondary"
                                          />
                                        </Tooltip>
                                      )}
                                    </Box>
                                  </TableCell>
                                </TableRow>
                                );
                              })}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </Grid>

                      {/* Clés primaires */}
                      {tableStructure.primary_keys.length > 0 && (
                        <Grid item xs={12} md={6}>
                          <Card variant="outlined">
                            <CardContent>
                              <Typography variant="h6" gutterBottom>
                                Clés Primaires
                              </Typography>
                              <Box display="flex" gap={1} flexWrap="wrap">
                                {tableStructure.primary_keys.map((pk) => (
                                  <Chip key={pk} label={pk} color="primary" />
                                ))}
                              </Box>
                            </CardContent>
                          </Card>
                        </Grid>
                      )}

                      {/* Clés étrangères */}
                      {tableStructure.foreign_keys.length > 0 && (
                        <Grid item xs={12} md={6}>
                          <Card variant="outlined">
                            <CardContent>
                              <Typography variant="h6" gutterBottom>
                                Clés Étrangères
                              </Typography>
                              <Box display="flex" gap={1} flexWrap="wrap">
                                {tableStructure.foreign_keys.map((fk) => (
                                  <Tooltip key={fk.column} title={`${fk.column} → ${fk.referenced_table}.${fk.referenced_column}`}>
                                    <Chip
                                      label={fk.column}
                                      color="secondary"
                                      variant="outlined"
                                    />
                                  </Tooltip>
                                ))}
                              </Box>
                            </CardContent>
                          </Card>
                        </Grid>
                      )}
                    </Grid>
                  ) : (
                    <Box display="flex" justifyContent="center" p={4}>
                      <CircularProgress />
                    </Box>
                  )}
                </Box>
              )}

              {/* Onglet Données */}
              {activeTab === 1 && (
                <Box p={3}>
                  {tableData ? (
                    <Box>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                        <Typography variant="h6">
                          Données ({tableData.pagination.total_rows} lignes)
                        </Typography>
                        <Button
                          variant="contained"
                          startIcon={<AddIcon />}
                          onClick={handleCreateRow}
                          color="primary"
                        >
                          + Ajouter une ligne
                        </Button>
                      </Box>
                      
                      <TableContainer sx={{ maxHeight: '60vh' }}>
                        <Table size="small" stickyHeader>
                                                  <TableHead>
                          <TableRow>
                              {tableData.columns.map((column) => {
                                const displayLabel = tableDisplayLabels[selectedTable]?.[column] || column;
                                return (
                              <TableCell key={column} sx={{ fontWeight: 'bold' }}>
                                    {displayLabel}
                              </TableCell>
                                );
                               })}
                            <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {tableData.data.map((row, index) => (
                            <TableRow key={index} hover>
                              {tableData.columns.map((column) => (
                                <TableCell key={column}>
                                  {row[column] !== null && row[column] !== undefined ? (
                                      isForeignKey(column) ? (
                                        <Tooltip title={`ID: ${row[column]}`}>
                                          <Typography variant="body2">
                                            {getForeignKeyDisplayLabel(column, row[column])}
                                          </Typography>
                                        </Tooltip>
                                      ) : (
                                        // Gestion spéciale pour les types de données
                                        (() => {
                                          const columnInfo = tableStructure?.columns?.find(col => col.name === column);
                                          if (isBooleanColumn(columnInfo)) {
                                            return (
                                              <Chip
                                                label={row[column] ? 'OUI' : 'NON'}
                                                size="small"
                                                color={row[column] ? 'success' : 'default'}
                                                variant="outlined"
                                              />
                                            );
                                          }
                                          return String(row[column]);
                                        })()
                                      )
                                  ) : (
                                    <Typography variant="body2" color="text.secondary" fontStyle="italic">
                                      NULL
                                    </Typography>
                                  )}
                                </TableCell>
                              ))}
                              <TableCell>
                                <Box display="flex" gap={1}>
                                  <Tooltip title="Modifier">
                                    <IconButton
                                      size="small"
                                      onClick={() => handleEditRow(row)}
                                      color="primary"
                                    >
                                      <EditIcon />
                                    </IconButton>
                                  </Tooltip>
                                  <Tooltip title="Supprimer">
                                    <IconButton
                                      size="small"
                                      onClick={() => handleDeleteRow(row)}
                                      color="error"
                                    >
                                      <DeleteIcon />
                                    </IconButton>
                                  </Tooltip>
                                </Box>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                        </Table>
                      </TableContainer>

                      {/* Pagination */}
                      {tableData.pagination.total_pages > 1 && (
                        <Box display="flex" justifyContent="center" mt={2}>
                          <Pagination
                            count={tableData.pagination.total_pages}
                            page={currentPage}
                            onChange={handlePageChange}
                            color="primary"
                            showFirstButton
                            showLastButton
                          />
                        </Box>
                      )}
                    </Box>
                  ) : (
                    <Box display="flex" justifyContent="center" p={4}>
                      <CircularProgress />
                    </Box>
                  )}
                </Box>
              )}
            </Paper>
          ) : (
            <Paper elevation={2} sx={{ p: 4, textAlign: 'center' }}>
              <TableIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                Sélectionnez une table pour voir sa structure et ses données
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>

      {/* Modale CRUD */}
      <Dialog 
        open={crudModalOpen} 
        onClose={handleCloseCrudModal} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          {crudMode === 'create' ? 'Ajouter une ligne' : 'Modifier la ligne'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
             {tableStructure?.columns?.map((column) => {
               const displayLabel = tableDisplayLabels[selectedTable]?.[column.name] || column.name;
               const typeInfo = getTypeInfo(column);
               
               return (
              <Box key={column.name} sx={{ mb: 2 }}>
                {column.name === 'id' && crudMode === 'create' ? (
                  // Ignorer l'ID pour la création (auto-incrémenté)
                  null
                   ) : isForeignKey(column.name) ? (
                     // Sélecteur pour les clés étrangères
                     <FormControl fullWidth>
                       <InputLabel>{displayLabel}</InputLabel>
                       <Select
                         value={formData[column.name] || ''}
                         onChange={(e) => setFormData({
                           ...formData,
                           [column.name]: e.target.value
                         })}
                         label={displayLabel}
                       >
                         <MenuItem value="">
                           <em>Sélectionner...</em>
                         </MenuItem>
                         {getForeignKeyData(column.name)?.data?.map((item) => (
                           <MenuItem key={item.id} value={item.id}>
                             {getForeignKeyDisplayLabel(column.name, item.id)}
                           </MenuItem>
                         ))}
                       </Select>
                       <FormHelperText>
                         <strong>Type:</strong> {column.type} (Clé étrangère vers {getForeignKeyData(column.name)?.referenced_table || 'table inconnue'})
                         {column.nullable ? ' • Nullable' : ' • Obligatoire'}
                         {typeInfo.examples && ` • Exemples: ${typeInfo.examples}`}
                         {getForeignKeyData(column.name)?.data && ` • ${getForeignKeyData(column.name).data.length} valeurs disponibles`}
                       </FormHelperText>
                       
                       {/* CORRECTION: Ajouter du débogage pour les clés étrangères */}
                       {console.log(`🔍 Modal - Colonne ${column.name}:`, {
                         isForeignKey: isForeignKey(column.name),
                         fkData: getForeignKeyData(column.name),
                         dataLength: getForeignKeyData(column.name)?.data?.length || 0,
                         tableForeignKeys: tableForeignKeys[selectedTable]
                       })}
                     </FormControl>
                   ) : isBooleanColumn(column) ? (
                     // Case à cocher pour les colonnes boolean
                     <FormControl component="fieldset">
                       <FormControlLabel
                         control={
                           <Checkbox
                             checked={formData[column.name] === true || formData[column.name] === 'true'}
                             onChange={(e) => setFormData({
                               ...formData,
                               [column.name]: e.target.checked
                             })}
                           />
                         }
                         label={displayLabel}
                       />
                       <FormHelperText>
                         <strong>Type:</strong> {column.type} (Boolean)
                         {column.nullable ? ' • Nullable' : ' • Obligatoire'}
                         • <strong>Valeurs:</strong> OUI (cochée) / NON (non cochée)
                       </FormHelperText>
                     </FormControl>
                   ) : (
                     // Champ texte normal pour les autres colonnes
                  <TextField
                    fullWidth
                       label={displayLabel}
                    value={formData[column.name] || ''}
                    onChange={(e) => setFormData({
                      ...formData,
                      [column.name]: e.target.value
                    })}
                    type={column.type.includes('date') ? 'date' : 'text'}
                    InputLabelProps={column.type.includes('date') ? { shrink: true } : {}}
                       placeholder={typeInfo.placeholder}
                       helperText={
                         <Box>
                           <strong>Type:</strong> {column.type}
                           {column.nullable ? ' • Nullable' : ' • Obligatoire'}
                           {typeInfo.examples && ` • Exemples: ${typeInfo.examples}`}
                           {typeInfo.format && ` • Format: ${typeInfo.format}`}
                         </Box>
                       }
                  />
                )}
              </Box>
               );
             })}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseCrudModal}>Annuler</Button>
          <Button 
            onClick={handleSubmitCrud} 
            variant="contained"
            disabled={loading}
          >
            {loading ? 'En cours...' : (crudMode === 'create' ? 'Créer' : 'Modifier')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DatabaseExplorerPage; 