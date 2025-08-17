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
  OutlinedInput
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
    return tableStructure?.foreign_keys?.some(fk => fk.column === columnName);
  };

  const getForeignKeyInfo = (columnName) => {
    return tableStructure?.foreign_keys?.find(fk => fk.column === columnName);
  };

  // Fonctions CRUD
  const handleCreateRow = () => {
    setCrudMode('create');
    setSelectedRow(null);
    setFormData({});
    setCrudModalOpen(true);
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
      if (crudMode === 'create') {
        await execute(() => 
          databaseExplorerService.createTableRow(selectedTable, formData)
        );
      } else {
        await execute(() => 
          databaseExplorerService.updateTableRow(selectedTable, selectedRow.id, formData)
        );
      }
      
      setCrudModalOpen(false);
      // Recharger les données
      loadTableData(selectedTable, (currentPage - 1) * pageSize);
    } catch (error) {
      console.error('Erreur lors de l\'opération CRUD:', error);
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
        <br />
        <strong>Note :</strong> Les tables sensibles (users, roles, refprofiles, infos) ne sont pas affichées ici pour des raisons de sécurité.
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
                                <TableCell>Type</TableCell>
                                <TableCell>Nullable</TableCell>
                                <TableCell>Défaut</TableCell>
                                <TableCell>Clés</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {tableStructure.columns.map((column) => (
                                <TableRow key={column.name}>
                                  <TableCell>
                                    <Typography variant="body2" fontWeight="bold">
                                      {column.name}
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
                                    {column.default ? (
                                      <Chip
                                        label={column.default}
                                        size="small"
                                        variant="outlined"
                                      />
                                    ) : (
                                      '-'
                                    )}
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
                              ))}
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
                          Ajouter une ligne
                        </Button>
                      </Box>
                      
                      <TableContainer sx={{ maxHeight: '60vh' }}>
                        <Table size="small" stickyHeader>
                                                  <TableHead>
                          <TableRow>
                            {tableData.columns.map((column) => (
                              <TableCell key={column} sx={{ fontWeight: 'bold' }}>
                                {column}
                              </TableCell>
                            ))}
                            <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {tableData.data.map((row, index) => (
                            <TableRow key={index} hover>
                              {tableData.columns.map((column) => (
                                <TableCell key={column}>
                                  {row[column] !== null && row[column] !== undefined ? (
                                    String(row[column])
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
            {tableStructure?.columns?.map((column) => (
              <Box key={column.name} sx={{ mb: 2 }}>
                {column.name === 'id' && crudMode === 'create' ? (
                  // Ignorer l'ID pour la création (auto-incrémenté)
                  null
                ) : (
                  <TextField
                    fullWidth
                    label={column.name}
                    value={formData[column.name] || ''}
                    onChange={(e) => setFormData({
                      ...formData,
                      [column.name]: e.target.value
                    })}
                    type={column.type.includes('date') ? 'date' : 'text'}
                    InputLabelProps={column.type.includes('date') ? { shrink: true } : {}}
                    helperText={`Type: ${column.type}${column.nullable ? ' (nullable)' : ''}`}
                  />
                )}
              </Box>
            ))}
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