/**
 * AuthContext — Contexto global de autenticación con React Context.
 * Persiste el token en localStorage y provee login/logout a toda la app.
 */

import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { authApi, type Usuario, type AuthResponse } from './api';

interface AuthContextType {
  user: Usuario | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Usuario | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);

  // Verificar token existente al cargar
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setIsLoading(false);
        return;
      }
      try {
        const userData = await authApi.me(token);
        setUser(userData);
      } catch {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };
    verifyToken();
  }, [token]);

  const login = async (email: string, password: string) => {
    const data: AuthResponse = await authApi.login(email, password);
    localStorage.setItem('token', data.access_token);
    setToken(data.access_token);
    setUser(data.usuario);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
