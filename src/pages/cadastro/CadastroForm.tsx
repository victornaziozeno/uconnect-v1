import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Button, Typography, Box, TextField, Grid } from '@mui/material';
import BaseLayout from '../login/BaseLayout.tsx';

const CadastroForm = () => {
  const [redirect, setRedirect] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    nomeCompleto: '',
    email: '',
    celular: '',
    dataNascimento: '',
    matricula: '',
    curso: ''
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleContinuar = () => {
    console.log('Dados do cadastro:', formData);
    setRedirect('/dashboard-professor');
  };

  const handleVoltar = () => {
    setRedirect('/profile-selection');
  };

  if (redirect) {
    return <Navigate to={redirect} />;
  }

  return (
    <BaseLayout showBorder={false}>
      {/* Header */}
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

      {/* Título */}
      <Typography
        variant="h4"
        component="h1"
        sx={{
          fontWeight: 'bold',
          color: '#1976d2',
          mb: 1,
          textAlign: 'center',
        }}
      >
        Cadastre-se para usar o Uconnect!
      </Typography>

      {/* Subtítulo */}
      <Typography
        variant="body1"
        sx={{
          color: '#333',
          mb: 4,
          fontSize: '16px',
          textAlign: 'center',
        }}
      >
        Para criar sua conta, preencha as informações abaixo:
      </Typography>

      {/* Formulário */}
      <Box sx={{ width: '100%', mb: 4 }}>
        {/* Campo Nome Completo - Mais largo */}
        <Box sx={{ mb: 3 }}>
          <Typography
            variant="body2"
            sx={{
              color: '#333',
              mb: 1,
              fontWeight: 'bold',
              textAlign: 'left',
            }}
          >
            Nome completo
          </Typography>
          <TextField
            name="nomeCompleto"
            value={formData.nomeCompleto}
            onChange={handleInputChange}
            placeholder="Preencha seu nome"
            fullWidth
            variant="outlined"
            size="large"
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'white',
                height: '56px',
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

        
          {/* Coluna Esquerda */}
          <Grid item xs={12} md={6}>
            <Box sx={{ mb: 3 }}>
              <Typography
                variant="body2"
                sx={{
                  color: '#333',
                  mb: 1,
                  fontWeight: 'bold',
                  textAlign: 'left',
                }}
              >
                E-mail
              </Typography>
              <TextField
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Preencha seu e-mail"
                fullWidth
                variant="outlined"
                size="large"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'white',
                    height: '56px',
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
                  textAlign: 'left',
                }}
              >
                Celular
              </Typography>
              <TextField
                name="celular"
                value={formData.celular}
                onChange={handleInputChange}
                placeholder="(00) 00000-0000"
                fullWidth
                variant="outlined"
                size="large"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'white',
                    height: '56px',
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
          </Grid>

          {/* Coluna Direita */}
          <Grid item xs={12} md={6}>
            <Box sx={{ mb: 3 }}>
              <Typography
                variant="body2"
                sx={{
                  color: '#333',
                  mb: 1,
                  fontWeight: 'bold',
                  textAlign: 'left',
                }}
              >
                Data de nascimento
              </Typography>
              <TextField
                name="dataNascimento"
                value={formData.dataNascimento}
                onChange={handleInputChange}
                placeholder="00/00/0000"
                fullWidth
                variant="outlined"
                size="large"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'white',
                    height: '56px',
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
                  textAlign: 'left',
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
                size="large"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'white',
                    height: '56px',
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
                  textAlign: 'left',
                }}
              >
                Curso
              </Typography>
              <TextField
                name="curso"
                value={formData.curso}
                onChange={handleInputChange}
                placeholder="Preencha seu curso"
                fullWidth
                variant="outlined"
                size="large"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    backgroundColor: 'white',
                    height: '56px',
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
          </Grid>
       
      </Box>

      {/* Botões */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'space-between', width: '100%' }}>
        <Button
          variant="contained"
          onClick={handleVoltar}
          sx={{
            backgroundColor: '#90caf9',
            color: 'white',
            py: 1.5,
            px: 3,
            fontSize: '16px',
            fontWeight: 'bold',
            borderRadius: '8px',
            '&:hover': {
              backgroundColor: '#81c784',
            },
          }}
        >
          Voltar
        </Button>
        
        <Button
          variant="contained"
          onClick={handleContinuar}
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
          Continuar
        </Button>
      </Box>
    </BaseLayout>
  );
};

export default CadastroForm;