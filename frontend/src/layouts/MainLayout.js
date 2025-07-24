import React, { useState } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Alert,
  Chip,
  Button,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Home as HomeIcon,
  AdminPanelSettings as AdminIcon,
  Security as SecurityIcon,
  Person as PersonIcon,
  ExitToApp as LogoutIcon,
  AccountCircle as AccountIcon,
  Group as GroupIcon,
  Lock as LockIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const drawerWidth = 240;

const MainLayout = ({ children }) => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const { user, logout, requiresPasswordChange } = useAuth();
  const navigate = useNavigate();

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
    handleProfileMenuClose();
  };

  const menuItems = [
    { text: 'Accueil', icon: <HomeIcon />, path: '/home' },
    ...(user?.role === 'admin' ? [
      { text: 'Dashboard Admin', icon: <AdminIcon />, path: '/admin' },
      { text: 'Gestion des Utilisateurs', icon: <GroupIcon />, path: '/admin/users' },
      { text: 'Gestion des Rôles', icon: <SecurityIcon />, path: '/admin/roles' },
    ] : []),
    // Ajouter le lien de changement de mot de passe si nécessaire
    ...(requiresPasswordChange ? [
      { 
        text: 'Changer le mot de passe', 
        icon: <LockIcon />, 
        path: '/change-password',
        highlight: true 
      }
    ] : []),
  ];

  const drawer = (
    <Box>
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Avatar sx={{ bgcolor: 'primary.main' }}>
          <PersonIcon />
        </Avatar>
        <Box>
          <Typography variant="subtitle1" fontWeight="bold">
            {user?.prenom} {user?.nom}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {user?.role}
          </Typography>
          {requiresPasswordChange && (
            <Chip
              icon={<WarningIcon />}
              label="Mot de passe à changer"
              color="warning"
              size="small"
              sx={{ mt: 1 }}
            />
          )}
        </Box>
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem
            key={item.text}
            button
            onClick={() => {
              navigate(item.path);
              setDrawerOpen(false);
            }}
            sx={item.highlight ? {
              bgcolor: 'warning.light',
              '&:hover': {
                bgcolor: 'warning.main',
              }
            } : {}}
          >
            <ListItemIcon sx={item.highlight ? { color: 'warning.dark' } : {}}>
              {item.icon}
            </ListItemIcon>
            <ListItemText 
              primary={item.text} 
              sx={item.highlight ? { color: 'warning.dark', fontWeight: 'bold' } : {}}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Crystal Assur
          </Typography>
          <IconButton
            size="large"
            edge="end"
            aria-label="account of current user"
            aria-controls="menu-appbar"
            aria-haspopup="true"
            onClick={handleProfileMenuOpen}
            color="inherit"
          >
            <AccountIcon />
          </IconButton>
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
          >
            <MenuItem onClick={handleProfileMenuClose}>
              <ListItemIcon>
                <PersonIcon fontSize="small" />
              </ListItemIcon>
              Profil
            </MenuItem>
            {requiresPasswordChange && (
              <MenuItem onClick={() => {
                navigate('/change-password');
                handleProfileMenuClose();
              }}>
                <ListItemIcon>
                  <LockIcon fontSize="small" />
                </ListItemIcon>
                Changer le mot de passe
              </MenuItem>
            )}
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              Déconnexion
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={drawerOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar />
        {requiresPasswordChange && (
          <Alert 
            severity="warning" 
            sx={{ mb: 2 }}
            action={
              <Button 
                color="inherit" 
                size="small"
                onClick={() => navigate('/change-password')}
              >
                Changer maintenant
              </Button>
            }
          >
            Votre mot de passe par défaut doit être changé pour des raisons de sécurité.
          </Alert>
        )}
        {children}
      </Box>
    </Box>
  );
};

export default MainLayout; 