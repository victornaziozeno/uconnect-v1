import React from 'react';
import { Typography } from '@mui/material';
import BaseLayout from '../login/BaseLayout.tsx';

const DashboardAluno = () => {
  return (
    <BaseLayout showBorder={false}>
      <Typography variant="h4" color="primary">
        Dashboard do Aluno
      </Typography>
      <Typography variant="body1">
        Bem-vindo ao seu dashboard!
      </Typography>
    </BaseLayout>
  );
};

export default DashboardAluno; 