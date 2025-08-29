import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Box,
  Typography,
  IconButton,
  Stack
} from '@mui/material';
import {
  Person as PersonIcon,
  Business as BusinessIcon,
  Close as CloseIcon
} from '@mui/icons-material';

const ClientTypeModal = ({ open, onClose, onTypeSelect }) => {
  const handleTypeSelect = (type) => {
    onTypeSelect(type);
    onClose();
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h5" component="div">
            Choisir le type de client
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Stack>
      </DialogTitle>
      
      <DialogContent>
        <Stack direction="row" spacing={4} justifyContent="center" sx={{ py: 4 }}>
          {/* Particulier Block */}
          <Box
            onClick={() => handleTypeSelect('PARTICULIER')}
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              p: 4,
              border: '2px solid #e0e0e0',
              borderRadius: 2,
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              '&:hover': {
                borderColor: '#1976d2',
                backgroundColor: '#f5f5f5',
                '& .type-icon': {
                  color: '#1976d2'
                },
                '& .type-text': {
                  color: '#1976d2'
                }
              }
            }}
          >
            <PersonIcon 
              className="type-icon"
              sx={{ 
                fontSize: 80, 
                color: '#9e9e9e',
                mb: 2,
                transition: 'color 0.3s ease'
              }} 
            />
            <Typography 
              className="type-text"
              variant="h6" 
              sx={{ 
                color: '#9e9e9e',
                fontWeight: 'bold',
                transition: 'color 0.3s ease'
              }}
            >
              Particulier
            </Typography>
          </Box>

          {/* Societe Block */}
          <Box
            onClick={() => handleTypeSelect('SOCIETE')}
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              p: 4,
              border: '2px solid #e0e0e0',
              borderRadius: 2,
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              '&:hover': {
                borderColor: '#1976d2',
                backgroundColor: '#f5f5f5',
                '& .type-icon': {
                  color: '#1976d2'
                },
                '& .type-text': {
                  color: '#1976d2'
                }
              }
            }}
          >
            <BusinessIcon 
              className="type-icon"
              sx={{ 
                fontSize: 80, 
                color: '#9e9e9e',
                mb: 2,
                transition: 'color 0.3s ease'
              }} 
            />
            <Typography 
              className="type-text"
              variant="h6" 
              sx={{ 
                color: '#9e9e9e',
                fontWeight: 'bold',
                transition: 'color 0.3s ease'
              }}
            >
              Societe
            </Typography>
          </Box>
        </Stack>
      </DialogContent>
    </Dialog>
  );
};

export default ClientTypeModal;
