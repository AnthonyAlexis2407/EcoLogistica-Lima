/**
 * LoginPage — Pantalla de autenticación con diseño glassmorphism.
 * Implementa EN-002: feedback de intentos restantes y lockout.
 */

import { useState, type FormEvent } from 'react';
import { useAuth } from '../AuthContext';
import { ApiError } from '../api';
import { Leaf } from 'lucide-react';

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError('Error de conexión con el servidor');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-left">
        <div className="login-brand">
          <div className="login-brand-icon">
            <Leaf size={36} color="white" />
          </div>
          <h1>EcoLogística Lima</h1>
          <p>Optimizador de Rutas Sostenibles</p>
        </div>

        <div className="login-card">
          <h2>Iniciar Sesión</h2>

          {error && <div className="login-error">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="email">Correo electrónico</label>
              <input
                id="email"
                className="form-input"
                type="email"
                placeholder="admin@ecologistica.pe"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="password">Contraseña</label>
              <input
                id="password"
                className="form-input"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
              />
            </div>

            <button
              type="submit"
              className="login-btn"
              disabled={loading}
            >
              {loading ? 'Autenticando...' : 'Ingresar'}
            </button>
          </form>

          <div className="login-footer">
            <p>DistriRápido S.A.C. — Lima, Perú</p>
            <p style={{ marginTop: '0.25rem', fontSize: '0.65rem' }}>
              v2.1.0 · Sprint 2 · Taller de Proyectos 2
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
