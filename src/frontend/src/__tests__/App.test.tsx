import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';
import { authApi, healthApi, pedidosApi, vehiculosApi } from '../api';

vi.mock('../api', async (original) => ({
  ...(await original<typeof import('../api')>()),
  authApi: { me: vi.fn(), login: vi.fn() },
  healthApi: { check: vi.fn() },
  vehiculosApi: { count: vi.fn(), list: vi.fn() },
  pedidosApi: { count: vi.fn(), list: vi.fn() },
}));

const usuario = { usuario_id: 'u1', nombre: 'Ana Pérez', email: 'ana@eco.pe', rol: 'ADMIN_FLOTA', estado: 'ACTIVO', creado_en: '' };

beforeEach(() => {
  vi.resetAllMocks();
  window.history.pushState({}, '', '/');
  vi.mocked(healthApi.check).mockResolvedValue({ status: 'ok' });
  vi.mocked(vehiculosApi.count).mockResolvedValue({});
  vi.mocked(pedidosApi.count).mockResolvedValue({});
  vi.mocked(vehiculosApi.list).mockResolvedValue([]);
  vi.mocked(pedidosApi.list).mockResolvedValue([]);
});

describe('App', () => {
  it('redirige al inicio de sesión cuando no hay sesión', async () => {
    render(<App />);
    expect(await screen.findByRole('heading', { name: 'Iniciar Sesión' })).toBeInTheDocument();
    expect(window.location.pathname).toBe('/login');
  });

  it('muestra el layout con el usuario autenticado y navega entre módulos', async () => {
    localStorage.setItem('token', 'tok');
    vi.mocked(authApi.me).mockResolvedValue(usuario);
    const user = userEvent.setup();
    render(<App />);

    expect(await screen.findByText('Administrador de Flota')).toBeInTheDocument();
    expect(screen.getByText('AP')).toBeInTheDocument(); // iniciales
    expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument();

    await user.click(screen.getByRole('link', { name: /Vehículos/ }));
    expect(await screen.findByRole('heading', { name: 'Gestión de Flota Vehicular' })).toBeInTheDocument();

    await user.click(screen.getByRole('link', { name: /Pedidos/ }));
    expect(await screen.findByRole('heading', { name: 'Gestión de Pedidos' })).toBeInTheDocument();
  });

  it('muestra el estado real de la API en la barra superior', async () => {
    localStorage.setItem('token', 'tok');
    vi.mocked(authApi.me).mockResolvedValue(usuario);
    render(<App />);
    expect(await screen.findByText('API conectada')).toBeInTheDocument();
  });

  it('avisa cuando la API no responde', async () => {
    localStorage.setItem('token', 'tok');
    vi.mocked(authApi.me).mockResolvedValue(usuario);
    vi.mocked(healthApi.check).mockRejectedValue(new Error('caída'));
    render(<App />);
    expect(await screen.findByText('API sin conexión')).toBeInTheDocument();
  });

  it('cierra la sesión y vuelve al login', async () => {
    localStorage.setItem('token', 'tok');
    vi.mocked(authApi.me).mockResolvedValue(usuario);
    const user = userEvent.setup();
    render(<App />);

    await user.click(await screen.findByTitle('Cerrar sesión'));
    expect(await screen.findByRole('heading', { name: 'Iniciar Sesión' })).toBeInTheDocument();
    expect(localStorage.getItem('token')).toBeNull();
  });
});
