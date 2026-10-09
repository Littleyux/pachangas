import { useState } from 'react';
import API from './api';
import './App.css';
import './icons.css';

function Login({ onLogin }) {
  const [modo, setModo] = useState('login'); // 'login' o 'register'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [nombre, setNombre] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await API.post('/auth/login', { email, password });
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('usuario', JSON.stringify(response.data.usuario));
      onLogin(response.data.usuario);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await API.post('/auth/register', { nombre, email, password });
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('usuario', JSON.stringify(response.data.usuario));
      onLogin(response.data.usuario);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al registrar usuario');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setError('');
    setGoogleLoading(true);

    try {
      // En desarrollo, usaremos un token dummy
      // En producción, usaríamos Google Identity Services o firebase.auth()
      const googleToken = btoa(JSON.stringify({ email, name: nombre || email.split('@')[0] }));
      
      const response = await API.post('/auth/google', { google_token: googleToken });
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('usuario', JSON.stringify(response.data.usuario));
      onLogin(response.data.usuario);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al iniciar con Google');
    } finally {
      setGoogleLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <h1 className="login-title">Pachangas</h1>
          <p className="login-subtitle">Organiza tus partidos de fútbol</p>
        </div>

        <div className="login-tabs">
          <button
            className={`login-tab ${modo === 'login' ? 'active' : ''}`}
            onClick={() => { setModo('login'); setError(''); }}
          >
            Iniciar Sesión
          </button>
          <button
            className={`login-tab ${modo === 'register' ? 'active' : ''}`}
            onClick={() => { setModo('register'); setError(''); }}
          >
            Registrar
          </button>
        </div>

        {error && <div className="login-error">{error}</div>}

        {modo === 'login' ? (
          <form onSubmit={handleLogin} className="login-form">
            <div className="form-group">
              <label htmlFor="login-email">Correo Electrónico</label>
              <input
                id="login-email"
                type="email"
                placeholder="ejemplo@correo.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="login-password">Contraseña</label>
              <input
                id="login-password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="button button-primary" disabled={loading}>
              {loading ? 'Iniciando...' : 'Iniciar Sesión'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="login-form">
            <div className="form-group">
              <label htmlFor="register-nombre">Nombre Completo</label>
              <input
                id="register-nombre"
                type="text"
                placeholder="Tu nombre"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="register-email">Correo Electrónico</label>
              <input
                id="register-email"
                type="email"
                placeholder="ejemplo@correo.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="register-password">Contraseña</label>
              <input
                id="register-password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength="6"
              />
              <small className="form-hint">Mínimo 6 caracteres</small>
            </div>
            <button type="submit" className="button button-primary" disabled={loading}>
              {loading ? 'Creando cuenta...' : 'Registrar Usuario'}
            </button>
          </form>
        )}

        <div className="login-divider">
          <span className="login-divider-text">o inicia con</span>
        </div>

        <button
          className="button button-google"
          onClick={handleGoogleLogin}
          disabled={googleLoading}
        >
          <span className="icon icon-google"></span>
          {googleLoading ? 'Verificando...' : 'Continuar con Google'}
        </button>

        <div className="login-footer">
          <p className="login-footer-text">
            Al continuar, aceptas nuestros términos y condiciones
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
