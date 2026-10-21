import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '../AuthContext';
import { authApi } from '../api';

vi.mock('../api', () => ({
  authApi: { me: vi.fn(), login: vi.fn() },
}));

const usuario = { usuario_id: 'u1', nombre: 'Ana Pérez', email: 'ana@eco.pe', rol: 'OPERADOR', estado: 'ACTIVO', creado_en: '' };

function Sonda() {
  const { user, token, isLoading, login, logout } = useAuth();
  return (
    <div>
      <span data-testid="estado">{isLoading ? 'cargando' : 'listo'}</span>
      <span data-testid="usuario">{user?.nombre ?? 'anonimo'}</span>
      <span data-testid="token">{token ?? 'sin-token'}</span>
      <button onClick={() => void login('ana@eco.pe', 'clave')}>entrar</button>
      <button onClick={logout}>salir</button>
    </div>
  );
}

beforeEach(() => {
  vi.mocked(authApi.me).mockReset();
  vi.mocked(authApi.login).mockReset();
});

describe('AuthProvider', () => {
  it('sin token guardado termina de cargar como anónimo', async () => {
    render(<AuthProvider><Sonda /></AuthProvider>);
    await waitFor(() => expect(screen.getByTestId('estado')).toHaveTextContent('listo'));
    expect(screen.getByTestId('usuario')).toHaveTextContent('anonimo');
    expect(authApi.me).not.toHaveBeenCalled();
  });

  it('con token válido recupera al usuario', async () => {
    localStorage.setItem('token', 'tok-ok');
    vi.mocked(authApi.me).mockResolvedValue(usuario);
    render(<AuthProvider><Sonda /></AuthProvider>);

    await waitFor(() => expect(screen.getByTestId('usuario')).toHaveTextContent('Ana Pérez'));
    expect(authApi.me).toHaveBeenCalledWith('tok-ok');
  });

  it('con token inválido lo elimina y queda anónimo', async () => {
    localStorage.setItem('token', 'tok-malo');
    vi.mocked(authApi.me).mockRejectedValue(new Error('401'));
    render(<AuthProvider><Sonda /></AuthProvider>);

    await waitFor(() => expect(screen.getByTestId('token')).toHaveTextContent('sin-token'));
    expect(localStorage.getItem('token')).toBeNull();
  });

  it('login guarda el token y logout lo borra', async () => {
    vi.mocked(authApi.login).mockResolvedValue({ access_token: 'nuevo', token_type: 'bearer', usuario });
    vi.mocked(authApi.me).mockResolvedValue(usuario);
    render(<AuthProvider><Sonda /></AuthProvider>);
    await waitFor(() => expect(screen.getByTestId('estado')).toHaveTextContent('listo'));

    await act(async () => { screen.getByText('entrar').click(); });
    await waitFor(() => expect(screen.getByTestId('usuario')).toHaveTextContent('Ana Pérez'));
    expect(localStorage.getItem('token')).toBe('nuevo');

    await act(async () => { screen.getByText('salir').click(); });
    expect(screen.getByTestId('usuario')).toHaveTextContent('anonimo');
    expect(localStorage.getItem('token')).toBeNull();
  });

  it('useAuth fuera del proveedor lanza un error', () => {
    const silencio = vi.spyOn(console, 'error').mockImplementation(() => {});
    expect(() => render(<Sonda />)).toThrow('useAuth must be used within AuthProvider');
    silencio.mockRestore();
  });
});
