import React from 'react';
import { Box, Container, Paper, Typography } from '@mui/material';
import { Security as SecurityIcon } from '@mui/icons-material';

const AuthLayout = ({ children }) => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        p: 2,
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={8}
          sx={{
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            borderRadius: 3,
          }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              mb: 3,
            }}
          >
            <SecurityIcon sx={{ fontSize: 40, color: 'primary.main' }} />
            <Typography variant="h4" component="h1" fontWeight="bold">
              Crystal Assur
            </Typography>
          </Box>
          <Typography variant="body1" color="text.secondary" textAlign="center" mb={3}>
            Connectez-vous à votre compte pour accéder à la plateforme de gestion des courtiers
          </Typography>
          {children}
        </Paper>
      </Container>
    </Box>
  );
};

export default AuthLayout; 