import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Button, Typography, Box } from '@mui/material';
import BaseLayout from './BaseLayout.tsx';

const Login = () => {
  const [redirect, setRedirect] = useState<string | null>(null);

  const handleLoginClick = () => {
    setRedirect('/profile-selection');
  };

  const handleCadastroClick = () => {
    setRedirect('/cadastro-form');
  };


  if (redirect) {
    return <Navigate to={redirect} />;
  }

  return (
    <BaseLayout>
      {/* Título */}
      <Typography
        variant="h4"
        component="h1"
        sx={{
          fontWeight: 'bold',
          color: '#1976d2',
          mb: 1,
        }}
      >
        UCONNECT
      </Typography>

      {/* Slogan */}
      <Typography
        variant="body1"
        sx={{
          color: '#666',
          mb: 4,
          fontSize: '16px',
        }}
      >
        A sua plataforma unificada de comunicação!
      </Typography>

      {/* Botões */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Button
          variant="contained"
          size="large"
          onClick={handleLoginClick}
          sx={{
            backgroundColor: '#1976d2',
            color: 'white',
            py: 1.5,
            fontSize: '16px',
            fontWeight: 'bold',
            borderRadius: '8px',
            '&:hover': {
              backgroundColor: '#1565c0',
            },
          }}
        >
          Login
        </Button>
        
        <Button
          variant="outlined"
          size="large"
          onClick={handleCadastroClick}
          sx={{
            borderColor: '#1976d2',
            color: '#1976d2',
            py: 1.5,
            fontSize: '16px',
            fontWeight: 'bold',
            borderRadius: '8px',
            '&:hover': {
              borderColor: '#1565c0',
              backgroundColor: 'rgba(25, 118, 210, 0.04)',
            },
          }}
        >
          Cadastro
        </Button>
      </Box>
    </BaseLayout>
  );
};

export default Login;
