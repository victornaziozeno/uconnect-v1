import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Button, Typography, Box, TextField } from '@mui/material';
import BaseLayout from './BaseLayout.tsx';

const LoginForm = () => {
  const [redirect, setRedirect] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    matricula: '',
    senha: ''
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAcessar = () => {
    console.log('Dados do login:', formData);
    setRedirect('/dashboard-aluno');
  };

  const handleVoltar = () => {
    setRedirect('/profile-selection');
  };

  if (redirect) {
    return <Navigate to={redirect} />;
  }

  return (
    <BaseLayout showBorder={false}>
    
      <Box sx={{ position: 'absolute', top: 20, left: 20, zIndex: 10 }}>
        <Typography
          variant="h6"
          sx={{
            color: 'white',
            fontWeight: 'bold',
          }}
        >
       
        </Typography>
      </Box>

  
      <Typography
        variant="h4"
        component="h1"
        sx={{
          fontWeight: 'bold',
          color: '#1976d2',
          mb: 1,
        }}
      >
        Acesse o Uconnect!
      </Typography>

    
      <Typography
        variant="body1"
        sx={{
          color: '#666',
          mb: 4,
          fontSize: '16px',
        }}
      >
        Preencha as informações abaixo:
      </Typography>

 
      <Box sx={{ width: '100%', mb: 4 }}>
        <Box sx={{ mb: 3 }}>
          <Typography
            variant="body2"
            sx={{
              color: '#333',
              mb: 1,
              fontWeight: 'bold',
            }}
          >
            Matrícula
          </Typography>
          <TextField
            name="matricula"
            value={formData.matricula}
            onChange={handleInputChange}
            placeholder="Preencha sua matricula"
            fullWidth
            variant="outlined"
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'white',
                '& fieldset': {
                  borderColor: '#ccc',
                },
                '&:hover fieldset': {
                  borderColor: '#1976d2',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#1976d2',
                },
              },
            }}
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <Typography
            variant="body2"
            sx={{
              color: '#333',
              mb: 1,
              fontWeight: 'bold',
            }}
          >
            Senha
          </Typography>
          <TextField
            name="senha"
            type="password"
            value={formData.senha}
            onChange={handleInputChange}
            placeholder="Preencha sua senha"
            fullWidth
            variant="outlined"
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'white',
                '& fieldset': {
                  borderColor: '#ccc',
                },
                '&:hover fieldset': {
                  borderColor: '#1976d2',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#1976d2',
                },
              },
            }}
          />
        </Box>
      </Box>

    
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'space-between', width: '100%' }}>
        <Button
          variant="outlined"
          onClick={handleVoltar}
          sx={{
            borderColor: '#ccc',
            color: '#1976d2',
            py: 1.5,
            px: 3,
            fontSize: '16px',
            fontWeight: 'bold',
            borderRadius: '8px',
            '&:hover': {
              borderColor: '#1976d2',
              backgroundColor: 'rgba(25, 118, 210, 0.04)',
            },
          }}
        >
          Voltar
        </Button>
        
        <Button
          variant="contained"
          onClick={handleAcessar}
          sx={{
            backgroundColor: '#1976d2',
            color: 'white',
            py: 1.5,
            px: 3,
            fontSize: '16px',
            fontWeight: 'bold',
            borderRadius: '8px',
            '&:hover': {
              backgroundColor: '#1565c0',
            },
          }}
        >
          Acessar
        </Button>
      </Box>
    </BaseLayout>
  );
};

export default LoginForm; 