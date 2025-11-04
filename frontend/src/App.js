import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Chat from './components/Chat';
import Login from './components/login';
import ProtectedRoute from './components/ProtectedRoute';
import MuralComunicados from './components/MuralComunicados';
import CriarEditarPublicacao from './components/CriarEditarPublicacao';
import Calendario from './components/calendario';
import NotificationProvider from './components/NotificationProvider';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route element={<ProtectedRoute />}>
            <Route
              path="/*"
              element={
                <NotificationProvider>
                  <Routes>
                    <Route path="/chat" element={<Chat />} />
                    <Route path="/comunicados/novo" element={<CriarEditarPublicacao />} />
                    <Route path="/comunicados/editar/:postId" element={<CriarEditarPublicacao />} />
                    <Route path="/comunicados" element={<MuralComunicados />} />
                    <Route path="/calendario" element={<Calendario />} />
                    <Route path="/" element={<Navigate to="/calendario" replace />} />
                  </Routes>
                </NotificationProvider>
              }
            />
          </Route>

          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;