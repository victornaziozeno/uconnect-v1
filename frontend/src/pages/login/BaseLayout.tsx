import React from 'react';
import { Container, Box } from '@mui/material';
import Logo from '../../assets/Logo.png';

interface BaseLayoutProps {
  children: React.ReactNode;
  showBorder?: boolean;
}

const BaseLayout: React.FC<BaseLayoutProps> = ({ children, showBorder = false }) => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundImage: 'url("/Content (1).jpg")',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        position: 'relative',
        border: showBorder ? '5px solid #1976d2' : 'none',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 41, 87, 0.8)',
        }
      }}
    >
      <Container
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <Box
          sx={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '48px',
            textAlign: 'center',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
            maxWidth: '400px',
            width: '100%',
          }}
        >
          {/* Logo */}
          <Box sx={{ mb: 3 }}>
            <img
              src={Logo}
              alt="UCONNECT Logo"
              style={{ 
                width: '80px', 
                height: '80px', 
                borderRadius: '50%',
                marginBottom: '16px'
              }}
            />
          </Box>

          {/* Conteúdo dinâmico */}
          {children}
        </Box>
      </Container>
    </Box>
  );
};

export default BaseLayout; 