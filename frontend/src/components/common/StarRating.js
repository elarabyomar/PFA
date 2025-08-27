import React, { useState } from 'react';
import { Box, IconButton, Tooltip } from '@mui/material';
import { Star as StarIcon, StarHalf as StarHalfIcon, StarBorder as StarBorderIcon } from '@mui/icons-material';

const StarRating = ({ 
  value = 0, 
  maxValue = 5, 
  size = 'small', 
  readOnly = true, 
  onChange,
  showValue = false 
}) => {
  const [hoverValue, setHoverValue] = useState(0);
  
  const handleStarClick = (starValue) => {
    if (!readOnly && onChange) {
      onChange(starValue);
    }
  };

  const handleStarHover = (starValue) => {
    if (!readOnly) {
      setHoverValue(starValue);
    }
  };

  const handleMouseLeave = () => {
    if (!readOnly) {
      setHoverValue(0);
    }
  };

  const renderStar = (index) => {
    const starValue = index + 1;
    const halfStarValue = index + 0.5;
    
    // Determine which value to use for display
    const displayValue = readOnly ? value : hoverValue || value;
    
    let icon;
    let color;
    
    if (displayValue >= starValue) {
      // Full star
      icon = <StarIcon />;
      color = '#FFD700'; // Gold
    } else if (displayValue >= halfStarValue) {
      // Half star
      icon = <StarHalfIcon />;
      color = '#FFD700'; // Gold
    } else {
      // Empty star
      icon = <StarBorderIcon />;
      color = '#D3D3D3'; // Light gray
    }
    
    return (
      <IconButton
        key={index}
        size={size}
        onClick={() => handleStarClick(starValue)}
        onMouseEnter={() => handleStarHover(starValue)}
        onMouseLeave={handleMouseLeave}
        sx={{
          p: 0.5,
          color: color,
          '&:hover': {
            color: readOnly ? color : '#FFD700',
          },
          cursor: readOnly ? 'default' : 'pointer',
        }}
        disabled={readOnly}
      >
        {icon}
      </IconButton>
    );
  };

  const renderHalfStar = (index) => {
    const halfStarValue = index + 0.5;
    
    // Determine which value to use for display
    const displayValue = readOnly ? value : hoverValue || value;
    
    let icon;
    let color;
    
    if (displayValue >= halfStarValue) {
      // Half star
      icon = <StarHalfIcon />;
      color = '#FFD700'; // Gold
    } else {
      // Empty star
      icon = <StarBorderIcon />;
      color = '#D3D3D3'; // Light gray
    }
    
    return (
      <IconButton
        key={`half-${index}`}
        size={size}
        onClick={() => handleStarClick(halfStarValue)}
        onMouseEnter={() => handleStarHover(halfStarValue)}
        onMouseLeave={handleMouseLeave}
        sx={{
          p: 0.5,
          color: color,
          '&:hover': {
            color: readOnly ? color : '#FFD700',
          },
          cursor: readOnly ? 'default' : 'pointer',
        }}
        disabled={readOnly}
      >
        {icon}
      </IconButton>
    );
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        {Array.from({ length: maxValue }, (_, index) => (
          <React.Fragment key={index}>
            {renderStar(index)}
            {index < maxValue - 1 && renderHalfStar(index)}
          </React.Fragment>
        ))}
      </Box>
      {showValue && (
        <Box sx={{ ml: 1, fontSize: '0.875rem', color: 'text.secondary' }}>
          {value.toFixed(1)}
        </Box>
      )}
    </Box>
  );
};

export default StarRating;
