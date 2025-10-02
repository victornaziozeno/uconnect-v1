import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Calendario from './components';
import Login from './pages/login/Login.tsx';
import ProfileSelection from './pages/login/ProfileSelection.tsx';
import LoginForm from './pages/login/LoginForm.tsx';
import CadastroForm from './pages/cadastro/CadastroForm.tsx';
import DashboardAluno from './pages/dashboard/DashboardAluno.tsx';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/*<Route path="/" element={<Login />} />*/} //Comentar o calendario e descomentar aqui para login
          <Route path="/" element={<Calendario />} />
          <Route path="/profile-selection" element={<ProfileSelection />} />
          <Route path="/login-form" element={<LoginForm />} />
          <Route path="/cadastro-form" element={<CadastroForm />} />
          <Route path="/dashboard-aluno" element={<DashboardAluno />} />
          <Route path="/dashboard-professor" element={<LoginForm />} />
          <Route path="/dashboard-coordenacao" element={<LoginForm />} />
          <Route path="/calendario" element={<Calendario />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
