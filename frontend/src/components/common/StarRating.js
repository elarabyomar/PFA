import React, { useState } from 'react';
import { Box, IconButton, Tooltip } from '@mui/material';
import { Star, StarBorder, StarHalf } from '@mui/icons-material';

const StarRating = ({ 
  value = 0, 
  onChange, 
  readOnly = false, 
  size = 'medium',
  showHalfStars = true,
  maxRating = 5 
}) => {
  const [hoverValue, setHoverValue] = useState(0);

  const handleStarClick = (starIndex, event) => {
    if (readOnly) return;
    
    const rect = event.currentTarget.getBoundingClientRect();
    const clickX = event.clientX - rect.left;
    const starWidth = rect.width;
    
    // Determine if it's half or full based on click position
    const isHalf = clickX < starWidth / 2;
    const starValue = starIndex + (isHalf ? 0.5 : 1);
    
    const newValue = value === starValue ? 0 : starValue;
    if (onChange) {
      onChange(newValue);
    }
  };

  const handleStarHover = (starIndex, event) => {
    if (readOnly) return;
    
    const rect = event.currentTarget.getBoundingClientRect();
    const clickX = event.clientX - rect.left;
    const starWidth = rect.width;
    
    // Determine if it's half or full based on click position
    const isHalf = clickX < starWidth / 2;
    const starValue = starIndex + (isHalf ? 0.5 : 1);
    
    setHoverValue(starValue);
  };

  const handleMouseLeave = () => {
    if (readOnly) return;
    setHoverValue(0);
  };

  const getStarIcon = (starIndex) => {
    const starValue = starIndex + 1;
    const halfStarValue = starIndex + 0.5;
    
    // Use hover value if available, otherwise use actual value
    const displayValue = hoverValue || value;
    
    if (displayValue >= starValue) {
      return <Star />;
    } else if (displayValue >= halfStarValue) {
      return <StarHalf />;
    } else {
      return <StarBorder />;
    }
  };

  const getStarColor = (starIndex) => {
    const starValue = starIndex + 1;
    const halfStarValue = starIndex + 0.5;
    
    // Use hover value if available, otherwise use actual value
    const displayValue = hoverValue || value;
    
    if (displayValue >= halfStarValue) {
      // If hovering, show blue; if selected, show grey
      return hoverValue ? '#1976d2' : '#757575';
    }
    return '#e0e0e0'; // Empty star color
  };

  return (
    <Box 
      display="flex" 
      alignItems="center"
      onMouseLeave={handleMouseLeave}
      sx={{ gap: '2px' }}
    >
      {Array.from({ length: maxRating }, (_, index) => (
        <Tooltip 
          key={index} 
          title={`${index + 0.5} ou ${index + 1} étoiles`}
          arrow
        >
          <IconButton
            size={size}
            onClick={(e) => handleStarClick(index, e)}
            onMouseMove={(e) => handleStarHover(index, e)}
                             sx={{
                   padding: '6px',
                   color: getStarColor(index),
                   '&:hover': {
                     color: readOnly ? getStarColor(index) : '#1976d2',
                   },
                   minWidth: '40px',
                   minHeight: '40px'
                 }}
            disabled={readOnly}
          >
            {getStarIcon(index)}
          </IconButton>
        </Tooltip>
      ))}
    </Box>
  );
};

export default StarRating;
