import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';
import { authApi, conductorApi, healthApi, indicadoresApi, notificacionesApi, pedidosApi, vehiculosApi } from '../api';

vi.mock('../api', async (original) => ({
  ...(await original<typeof import('../api')>()),
  authApi: { me: vi.fn(), login: vi.fn() },
  healthApi: { check: vi.fn() },
  vehiculosApi: { count: vi.fn(), list: vi.fn(), listPage: vi.fn() },
  pedidosApi: { count: vi.fn(), list: vi.fn(), listPage: vi.fn() },
  indicadoresApi: { resumen: vi.fn(), distritos: vi.fn() },
  notificacionesApi: { mias: vi.fn() },
  conductorApi: { miRuta: vi.fn(), sincronizar: vi.fn(), ubicacion: vi.fn() },
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
  vi.mocked(indicadoresApi.resumen).mockRejectedValue(new Error('sin datos'));
  vi.mocked(indicadoresApi.distritos).mockResolvedValue([]);
  vi.mocked(notificacionesApi.mias).mockResolvedValue({ items: [], noLeidas: 0 });
  vi.mocked(vehiculosApi.listPage).mockResolvedValue({ items: [], total: 0 });
  vi.mocked(pedidosApi.listPage).mockResolvedValue({ items: [], total: 0 });
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

  it('cada rol ve solo su menú (Documento 08): el conductor entra a Mi ruta y no ve la administración', async () => {
    localStorage.setItem('token', 'tok');
    vi.mocked(authApi.me).mockResolvedValue({ ...usuario, rol: 'CONDUCTOR' });
    vi.mocked(conductorApi.miRuta).mockRejectedValue(new Error('sin ruta'));
    render(<App />);
    expect(await screen.findByRole('link', { name: /Mi ruta/ })).toBeInTheDocument();
    expect(window.location.pathname).toBe('/conductor');
    expect(screen.queryByRole('link', { name: /Administración/ })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /Vehículos/ })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /Dashboard/ })).not.toBeInTheDocument();
  });

  it('el administrador ve la administración y la bodega solo pedidos y avisos', async () => {
    localStorage.setItem('token', 'tok');
    vi.mocked(authApi.me).mockResolvedValue(usuario);
    const { unmount } = render(<App />);
    expect(await screen.findByRole('link', { name: /Administración/ })).toBeInTheDocument();
    unmount();

    window.history.pushState({}, '', '/administracion');
    vi.mocked(authApi.me).mockResolvedValue({ ...usuario, rol: 'BODEGA' });
    render(<App />);
    expect(await screen.findByRole('link', { name: /Notificaciones/ })).toBeInTheDocument();
    expect(window.location.pathname).toBe('/pedidos'); // la ruta de administración no está permitida para su rol
    expect(screen.queryByRole('link', { name: /Administración/ })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /Rutas/ })).not.toBeInTheDocument();
  });
});
