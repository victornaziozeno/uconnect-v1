import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Button, Typography, Box } from '@mui/material';
import BaseLayout from './BaseLayout.tsx';

const ProfileSelection = () => {
  const [redirect, setRedirect] = useState<string | null>(null);

  const handleProfileSelect = (profile: string) => {
    if (profile === 'aluno') {
      setRedirect('/login-form');
    } else if (profile === 'professor') {
      setRedirect('/cadastro-form');
    } else if (profile === 'coordenacao') {
      setRedirect('/login-form');
    }
  };

  if (redirect) {
    return <Navigate to={redirect} />;
  }

  return (
    <BaseLayout showBorder={false}>
   
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

      
      <Typography
        variant="h6"
        sx={{
          fontWeight: 'bold',
          color: '#333',
          mb: 2,
        }}
      >
        Seja bem vindo(a)!
      </Typography>

    
      <Typography
        variant="body1"
        sx={{
          color: '#666',
          mb: 4,
          fontSize: '16px',
        }}
      >
        Escolha como gostaria de logar:
      </Typography>

  
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 3 }}>
        <Button
          variant="contained"
          size="large"
          onClick={() => handleProfileSelect('aluno')}
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
          Aluno(a)
        </Button>
        
        <Button
          variant="outlined"
          size="large"
          onClick={() => handleProfileSelect('aluno')}
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
          Professor(a)
        </Button>
      </Box>

      
      <Button
        variant="text"
        onClick={() => handleProfileSelect('coordenacao')}
        sx={{
          color: '#1976d2',
          fontSize: '16px',
          fontWeight: 'bold',
          textDecoration: 'underline',
          '&:hover': {
            backgroundColor: 'rgba(25, 118, 210, 0.04)',
          },
        }}
      >
        Coordenação
      </Button>
    </BaseLayout>
  );
};

export default ProfileSelection; 