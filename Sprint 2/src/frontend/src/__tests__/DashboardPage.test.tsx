import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import DashboardPage from '../pages/DashboardPage';
import { pedidosApi, vehiculosApi } from '../api';

vi.mock('../AuthContext', () => ({
  useAuth: () => ({ token: 'tok', user: { nombre: 'Ana Pérez' } }),
}));
vi.mock('../api', () => ({
  vehiculosApi: { count: vi.fn(), list: vi.fn() },
  pedidosApi: { count: vi.fn(), list: vi.fn() },
}));

beforeEach(() => {
  vi.resetAllMocks();
});

describe('DashboardPage', () => {
  it('muestra los indicadores de flota y pedidos', async () => {
    vi.mocked(vehiculosApi.count).mockResolvedValue({ TOTAL: 3, DISPONIBLE: 2 });
    vi.mocked(pedidosApi.count).mockResolvedValue({ TOTAL: 7, PENDIENTE: 4, EN_RUTA: 2, ENTREGADO: 1 });
    vi.mocked(vehiculosApi.list).mockResolvedValue([
      { vehiculo_id: '1', placa: 'A', capacidad_kg: 1000, tipo_combustible: 'DIESEL', factor_emision_co2: 2, estado: 'DISPONIBLE' },
      { vehiculo_id: '2', placa: 'B', capacidad_kg: 500, tipo_combustible: 'GLP', factor_emision_co2: 1, estado: 'DISPONIBLE' },
    ]);
    vi.mocked(pedidosApi.list).mockResolvedValue([]);

    render(<MemoryRouter><DashboardPage /></MemoryRouter>);

    expect(screen.getByText('Bienvenido, Ana Pérez')).toBeInTheDocument();
    expect(await screen.findByText('4 pendientes · 2 en ruta')).toBeInTheDocument();
    expect(screen.getByText(/2 unidades operativas \(1[.,\s]?500 kg\)/)).toBeInTheDocument();
    expect(screen.getByText('1.50')).toBeInTheDocument();
  });

  it('usa valores por defecto si la API falla', async () => {
    vi.mocked(vehiculosApi.count).mockRejectedValue(new Error('x'));
    vi.mocked(pedidosApi.count).mockRejectedValue(new Error('x'));
    vi.mocked(vehiculosApi.list).mockRejectedValue(new Error('x'));
    vi.mocked(pedidosApi.list).mockRejectedValue(new Error('x'));

    render(<MemoryRouter><DashboardPage /></MemoryRouter>);

    expect(await screen.findByText('0 pendientes · 0 en ruta')).toBeInTheDocument();
    expect(screen.getByText('1.78')).toBeInTheDocument();
  });
});
