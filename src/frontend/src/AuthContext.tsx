/**
 * AuthContext — Contexto global de autenticación con React Context.
 * Persiste el token en localStorage y provee login/logout a toda la app.
 */

import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { authApi, ApiError, type Usuario, type AuthResponse } from './api';

interface AuthContextType {
  user: Usuario | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

const CLAVE_USUARIO = 'usuario';

function guardarUsuario(usuario: Usuario): void {
  try {
    localStorage.setItem(CLAVE_USUARIO, JSON.stringify(usuario));
  } catch {
    /* almacenamiento bloqueado: la sesión funciona solo con conexión */
  }
}

function usuarioGuardado(): Usuario | null {
  try {
    const crudo = localStorage.getItem(CLAVE_USUARIO);
    return crudo ? (JSON.parse(crudo) as Usuario) : null;
  } catch {
    return null;
  }
}

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
        guardarUsuario(userData);
      } catch (err) {
        // Sin red (RNF-010) la sesión no se pierde: se usa el último perfil conocido. Si el servidor responde que el token
        // no es válido (cualquier respuesta HTTP de error), la sesión sí se cierra.
        const guardado = err instanceof ApiError ? null : usuarioGuardado();
        if (guardado) {
          setUser(guardado);
        } else {
          localStorage.removeItem('token');
          localStorage.removeItem(CLAVE_USUARIO);
          setToken(null);
          setUser(null);
        }
      } finally {
        setIsLoading(false);
      }
    };
    void verifyToken();
  }, [token]);

  const login = async (email: string, password: string) => {
    const data: AuthResponse = await authApi.login(email, password);
    localStorage.setItem('token', data.access_token);
    guardarUsuario(data.usuario);
    setToken(data.access_token);
    setUser(data.usuario);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem(CLAVE_USUARIO);
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
