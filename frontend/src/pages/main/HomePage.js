import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Avatar,
  Chip,
  Divider,
  Alert,
  Button,
  LinearProgress,
  Paper,
  Stack,
  IconButton,
  Tooltip,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Badge,
  Fade,
  Grow
} from '@mui/material';
import {
  Person as PersonIcon,
  Email as EmailIcon,
  CalendarToday as CalendarIcon,
  Security as SecurityIcon,
  Lock as LockIcon,
  Business as BusinessIcon,
  People as PeopleIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Assignment as AssignmentIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Pending as PendingIcon,
  MonetizationOn as MonetizationOnIcon,
  Description as DescriptionIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  Transform as TransformIcon,
  AttachMoney as AttachMoneyIcon,
  Schedule as ScheduleIcon,
  Star as StarIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';
import { formatDate } from '../../utils/validation';
import { useNavigate } from 'react-router-dom';
import { clientService } from '../../services/clientService';
import { opportunityService } from '../../services/opportunityService';
import { contractService } from '../../services/contractService';

const HomePage = () => {
  const { user, requiresPasswordChange } = useAuth();
  const navigate = useNavigate();
  
  // Dashboard data states
  const [dashboardData, setDashboardData] = useState({
    clients: { loading: true, data: null },
    opportunities: { loading: true, data: null },
    contracts: { loading: true, data: null }
  });

  // Load dashboard data
  const loadDashboardData = async () => {
    try {
      // Load clients data
      const clientsData = await clientService.getAllClients();
      
      // Load opportunities data
      const opportunitiesData = await opportunityService.getAllOpportunities();
      
      // Load contracts data
      const contractsData = await contractService.getAllContracts();

      setDashboardData({
        clients: { loading: false, data: clientsData },
        opportunities: { loading: false, data: opportunitiesData },
        contracts: { loading: false, data: contractsData }
      });
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setDashboardData({
        clients: { loading: false, data: [] },
        opportunities: { loading: false, data: [] },
        contracts: { loading: false, data: [] }
      });
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  // Calculate client statistics
  const getClientStats = (clients) => {
    if (!clients || clients.length === 0) return {};
    
    const total = clients.length;
    const particuliers = clients.filter(c => c.typeClient === 'PARTICULIER').length;
    const societes = clients.filter(c => c.typeClient === 'SOCIETE').length;
    const highImportance = clients.filter(c => c.importance >= 8).length;
    const mediumImportance = clients.filter(c => c.importance >= 5 && c.importance < 8).length;
    const lowImportance = clients.filter(c => c.importance < 5).length;
    
    // Calculate average budget - properly handle string/Decimal conversion
    const totalBudget = clients.reduce((sum, c) => {
      const budgetValue = c.budget;
      
      if (budgetValue === null || budgetValue === undefined || budgetValue === '') {
        return sum;
      }
      // Convert to number, handling both string and number types
      const numericBudget = typeof budgetValue === 'string' ? parseFloat(budgetValue) : Number(budgetValue);
      
      return sum + (isNaN(numericBudget) ? 0 : numericBudget);
    }, 0);
    const avgBudget = total > 0 ? totalBudget / total : 0;
    
    return {
      total,
      particuliers,
      societes,
      highImportance,
      mediumImportance,
      lowImportance,
      avgBudget: Math.round(avgBudget)
    };
  };

  // Calculate opportunity statistics
  const getOpportunityStats = (opportunities) => {
    if (!opportunities || opportunities.length === 0) return {};
    
    const total = opportunities.length;
    const transformed = opportunities.filter(o => o.transformed).length;
    const nonTransformed = total - transformed;
    const gagnees = opportunities.filter(o => o.etape === 'Gagnée').length;
    const perdues = opportunities.filter(o => o.etape === 'Perdue').length;
    const enCours = total - gagnees - perdues;
    
    // Calculate success rate
    const successRate = total > 0 ? Math.round((gagnees / total) * 100) : 0;
    
    // Calculate transformation rate
    const transformationRate = total > 0 ? Math.round((transformed / total) * 100) : 0;
    
    return {
      total,
      transformed,
      nonTransformed,
      gagnees,
      perdues,
      enCours,
      successRate,
      transformationRate
    };
  };

  // Calculate contract statistics
  const getContractStats = (contracts) => {
    if (!contracts || contracts.length === 0) return {};
    
    const total = contracts.length;
    const dureeFerme = contracts.filter(c => c.typeContrat === 'Duree ferme').length;
    const dureeCampagne = contracts.filter(c => c.typeContrat === 'Duree campagne').length;
    
    // Calculate total and average prime - properly handle string/Decimal conversion
    const totalPrime = contracts.reduce((sum, c) => {
      const primeValue = c.prime;
      
      if (primeValue === null || primeValue === undefined || primeValue === '') {
        return sum;
      }
      // Convert to number, handling both string and number types
      const numericPrime = typeof primeValue === 'string' ? parseFloat(primeValue) : Number(primeValue);
      
      return sum + (isNaN(numericPrime) ? 0 : numericPrime);
    }, 0);
    const avgPrime = total > 0 ? totalPrime / total : 0;
    
    // Calculate contracts by month (last 6 months)
    const now = new Date();
    const sixMonthsAgo = new Date(now.getFullYear(), now.getMonth() - 6, 1);
    const recentContracts = contracts.filter(c => {
      const contractDate = new Date(c.dateDebut);
      return contractDate >= sixMonthsAgo;
    }).length;
    
    return {
      total,
      dureeFerme,
      dureeCampagne,
      totalPrime: Math.round(totalPrime),
      avgPrime: Math.round(avgPrime),
      recentContracts
    };
  };

  const clientStats = getClientStats(dashboardData.clients.data);
  const opportunityStats = getOpportunityStats(dashboardData.opportunities.data);
  const contractStats = getContractStats(dashboardData.contracts.data);

  // Custom progress bar component
  const CustomProgressBar = ({ value, maxValue, color, label, showPercentage = true }) => (
    <Box sx={{ mb: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
        {showPercentage && (
          <Typography variant="body2" fontWeight="medium">
            {maxValue > 0 ? Math.round((value / maxValue) * 100) : 0}%
          </Typography>
        )}
      </Box>
      <LinearProgress
        variant="determinate"
        value={maxValue > 0 ? (value / maxValue) * 100 : 0}
        sx={{
          height: 8,
          borderRadius: 4,
          backgroundColor: 'grey.200',
          '& .MuiLinearProgress-bar': {
            backgroundColor: color,
            borderRadius: 4,
          }
        }}
      />
    </Box>
  );

  // Stat card component
  const StatCard = ({ title, value, subtitle, icon, color, trend, trendValue }) => (
    <Card sx={{ height: '100%', position: 'relative', overflow: 'visible' }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography variant="h4" component="div" fontWeight="bold" color={color}>
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              {title}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Avatar
            sx={{
              bgcolor: `${color}.light`,
              color: color,
              width: 48,
              height: 48,
              position: 'absolute',
              top: -20,
              right: 16,
            }}
          >
            {icon}
          </Avatar>
        </Box>
        {trend && (
          <Box display="flex" alignItems="center" mt={2}>
            {trend === 'up' ? (
              <TrendingUpIcon color="success" fontSize="small" />
            ) : (
              <TrendingDownIcon color="error" fontSize="small" />
            )}
            <Typography
              variant="caption"
              color={trend === 'up' ? 'success.main' : 'error.main'}
              sx={{ ml: 0.5 }}
            >
              {trendValue}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box>
      {requiresPasswordChange && (
        <Alert 
          severity="warning" 
          sx={{ mb: 3 }}
          action={
            <Button 
              color="inherit" 
              size="small"
              startIcon={<LockIcon />}
              onClick={() => navigate('/change-password')}
            >
              Changer maintenant
            </Button>
          }
        >
          <Typography variant="body2" fontWeight="medium">
            Attention : Votre mot de passe par défaut doit être changé pour des raisons de sécurité.
          </Typography>
        </Alert>
      )}

      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Tableau de bord
        </Typography>
        <IconButton onClick={loadDashboardData} color="primary">
          <RefreshIcon />
        </IconButton>
      </Box>
      
              <Typography variant="body1" color="text.secondary" paragraph>
          Vue d&apos;ensemble de vos données Insurforce
        </Typography>

      {/* User Profile Section - MOVED TO TOP */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
          <PersonIcon color="primary" />
          Profil Utilisateur
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} mb={3}>
                  <Avatar
                    sx={{
                      width: 64,
                      height: 64,
                      bgcolor: 'primary.main',
                      fontSize: '1.5rem',
                    }}
                  >
                    {user?.prenom?.charAt(0)}{user?.nom?.charAt(0)}
                  </Avatar>
                  <Box>
                    <Typography variant="h5" component="h2">
                      {user?.prenom} {user?.nom}
                    </Typography>
                    <Chip
                      label={user?.role}
                      color={user?.role === 'admin' ? 'error' : 'primary'}
                      icon={<SecurityIcon />}
                      sx={{ mt: 1 }}
                    />
                    {requiresPasswordChange && (
                      <Chip
                        label="Mot de passe à changer"
                        color="warning"
                        size="small"
                        icon={<LockIcon />}
                        sx={{ mt: 1, ml: 1 }}
                      />
                    )}
                  </Box>
                </Box>

                <Divider sx={{ my: 2 }} />

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Box display="flex" alignItems="center" gap={1} mb={2}>
                      <EmailIcon color="action" />
                      <Typography variant="body2" color="text.secondary">
                        Email
                      </Typography>
                    </Box>
                    <Typography variant="body1" fontWeight="medium">
                      {user?.email}
                    </Typography>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Box display="flex" alignItems="center" gap={1} mb={2}>
                      <CalendarIcon color="action" />
                      <Typography variant="body2" color="text.secondary">
                        Date de naissance
                      </Typography>
                    </Box>
                    <Typography variant="body1" fontWeight="medium">
                      {formatDate(user?.date_naissance)}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Informations système
                </Typography>
                
                <Box mt={2}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Statut de connexion
                  </Typography>
                  <Chip
                    label="Connecté"
                    color="success"
                    size="small"
                  />
                </Box>

                <Box mt={2}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Permissions
                  </Typography>
                  <Chip
                    label={user?.role === 'admin' ? 'Administrateur' : 'Utilisateur'}
                    color={user?.role === 'admin' ? 'error' : 'primary'}
                    size="small"
                  />
                </Box>

                {user?.role === 'admin' && (
                  <Box mt={2}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Accès admin
                    </Typography>
                    <Chip
                      label="Dashboard Admin"
                      color="warning"
                      size="small"
                      sx={{ mr: 1 }}
                    />
                    <Chip
                      label="Gestion Rôles"
                      color="warning"
                      size="small"
                    />
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* CLIENTES SECTION */}
      <Box mb={4}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
          <PeopleIcon color="primary" />
          Clients
        </Typography>
        
        <Grid container spacing={3}>
          {/* Main Stats Cards */}
          <Grid item xs={12} md={3}>
            <StatCard
              title="Total Clients"
              value={clientStats.total || 0}
              subtitle="Tous types confondus"
              icon={<PeopleIcon />}
              color="primary"
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <StatCard
              title="Particuliers"
              value={clientStats.particuliers || 0}
              subtitle={`${clientStats.total > 0 ? Math.round((clientStats.particuliers / clientStats.total) * 100) : 0}% du total`}
              icon={<PersonIcon />}
              color="success"
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <StatCard
              title="Sociétés"
              value={clientStats.societes || 0}
              subtitle={`${clientStats.total > 0 ? Math.round((clientStats.societes / clientStats.total) * 100) : 0}% du total`}
              icon={<BusinessIcon />}
              color="info"
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <StatCard
              title="Budget Moyen"
              value={`${clientStats.avgBudget || 0} DH`}
              subtitle="Par client"
              icon={<MonetizationOnIcon />}
              color="warning"
            />
          </Grid>

          {/* Detailed Stats */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Répartition par importance
                </Typography>
                <CustomProgressBar
                  value={clientStats.highImportance || 0}
                  maxValue={clientStats.total || 1}
                  color="success.main"
                  label={`Haute importance (${clientStats.highImportance || 0})`}
                />
                <CustomProgressBar
                  value={clientStats.mediumImportance || 0}
                  maxValue={clientStats.total || 1}
                  color="warning.main"
                  label={`Importance moyenne (${clientStats.mediumImportance || 0})`}
                />
                <CustomProgressBar
                  value={clientStats.lowImportance || 0}
                  maxValue={clientStats.total || 1}
                  color="error.main"
                  label={`Faible importance (${clientStats.lowImportance || 0})`}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Top Clients
                </Typography>
                <List dense>
                  {dashboardData.clients.data?.slice(0, 5).map((client, index) => (
                    <ListItem key={client.id}>
                      <ListItemIcon>
                        <Avatar sx={{ width: 32, height: 32, fontSize: '0.875rem' }}>
                          {index + 1}
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={client.nom || 'N/A'}
                        secondary={`${client.typeClient} - ${client.importance || 0}/10`}
                      />
                      {client.importance >= 8 && <StarIcon color="warning" />}
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* OPPORTUNITÉS SECTION */}
      <Box mb={4}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
          <AssignmentIcon color="secondary" />
          Opportunités
        </Typography>
        
        <Grid container spacing={3}>
          {/* Main Stats Cards */}
          <Grid item xs={12} md={3}>
            <StatCard
              title="Total Opportunités"
              value={opportunityStats.total || 0}
              subtitle="Toutes étapes confondues"
              icon={<AssignmentIcon />}
              color="secondary"
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <StatCard
              title="Transformées"
              value={opportunityStats.transformed || 0}
              subtitle={`${opportunityStats.transformationRate || 0}% de transformation`}
              icon={<TransformIcon />}
              color="success"
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <StatCard
              title="Gagnées"
              value={opportunityStats.gagnees || 0}
              subtitle={`${opportunityStats.successRate || 0}% de réussite`}
              icon={<CheckCircleIcon />}
              color="success"
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <StatCard
              title="En Cours"
              value={opportunityStats.enCours || 0}
              subtitle="À traiter"
              icon={<PendingIcon />}
              color="warning"
            />
          </Grid>

          {/* Detailed Stats */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Statut des opportunités
                </Typography>
                <Box display="flex" justifyContent="space-around" alignItems="center" mt={3}>
                  <Box textAlign="center">
                    <CircularProgress
                      variant="determinate"
                      value={opportunityStats.successRate || 0}
                      size={80}
                      thickness={4}
                      sx={{ color: 'success.main', mb: 1 }}
                    />
                    <Typography variant="h6" color="success.main">
                      {opportunityStats.successRate || 0}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Taux de réussite
                    </Typography>
                  </Box>
                  <Box textAlign="center">
                    <CircularProgress
                      variant="determinate"
                      value={opportunityStats.transformationRate || 0}
                      size={80}
                      thickness={4}
                      sx={{ color: 'info.main', mb: 1 }}
                    />
                    <Typography variant="h6" color="info.main">
                      {opportunityStats.transformationRate || 0}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Taux de transformation
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Répartition par étape
                </Typography>
                <CustomProgressBar
                  value={opportunityStats.gagnees || 0}
                  maxValue={opportunityStats.total || 1}
                  color="success.main"
                  label={`Gagnées (${opportunityStats.gagnees || 0})`}
                />
                <CustomProgressBar
                  value={opportunityStats.enCours || 0}
                  maxValue={opportunityStats.total || 1}
                  color="warning.main"
                  label={`En cours (${opportunityStats.enCours || 0})`}
                />
                <CustomProgressBar
                  value={opportunityStats.perdues || 0}
                  maxValue={opportunityStats.total || 1}
                  color="error.main"
                  label={`Perdues (${opportunityStats.perdues || 0})`}
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* CONTRATS SECTION */}
      <Box mb={4}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
          <DescriptionIcon color="info" />
          Contrats
        </Typography>
        
        <Grid container spacing={3}>
          {/* Main Stats Cards */}
          <Grid item xs={12} md={3}>
            <StatCard
              title="Total Contrats"
              value={contractStats.total || 0}
              subtitle="Tous types confondus"
              icon={<DescriptionIcon />}
              color="info"
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <StatCard
              title="Durée Ferme"
              value={contractStats.dureeFerme || 0}
              subtitle={`${contractStats.total > 0 ? Math.round((contractStats.dureeFerme / contractStats.total) * 100) : 0}% du total`}
              icon={<ScheduleIcon />}
              color="success"
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <StatCard
              title="Durée Campagne"
              value={contractStats.dureeCampagne || 0}
              subtitle={`${contractStats.total > 0 ? Math.round((contractStats.dureeCampagne / contractStats.total) * 100) : 0}% du total`}
              icon={<CalendarIcon />}
              color="warning"
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <StatCard
              title="Prime Moyenne"
              value={`${contractStats.avgPrime || 0} DH`}
              subtitle="Par contrat"
              icon={<AttachMoneyIcon />}
              color="primary"
            />
          </Grid>

          {/* Detailed Stats */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Aperçu financier
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Box textAlign="center" p={2}>
                      <Typography variant="h4" color="primary.main" fontWeight="bold">
                        {contractStats.totalPrime?.toLocaleString() || 0} DH
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Prime totale
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Box textAlign="center" p={2}>
                      <Typography variant="h4" color="success.main" fontWeight="bold">
                        {contractStats.recentContracts || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Contrats récents (6 mois)
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle1" gutterBottom>
                  Répartition par type
                </Typography>
                <CustomProgressBar
                  value={contractStats.dureeFerme || 0}
                  maxValue={contractStats.total || 1}
                  color="success.main"
                  label={`Durée ferme (${contractStats.dureeFerme || 0})`}
                />
                <CustomProgressBar
                  value={contractStats.dureeCampagne || 0}
                  maxValue={contractStats.total || 1}
                  color="warning.main"
                  label={`Durée campagne (${contractStats.dureeCampagne || 0})`}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance
                </Typography>
                <Box textAlign="center" mt={3}>
                  <CircularProgress
                    variant="determinate"
                    value={contractStats.total > 0 ? Math.round((contractStats.recentContracts / contractStats.total) * 100) : 0}
                    size={80}
                    thickness={4}
                    sx={{ color: 'info.main', mb: 1 }}
                  />
                  <Typography variant="h6" color="info.main">
                    {contractStats.total > 0 ? Math.round((contractStats.recentContracts / contractStats.total) * 100) : 0}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Contrats récents
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

    </Box>
  );
};

export default HomePage; 