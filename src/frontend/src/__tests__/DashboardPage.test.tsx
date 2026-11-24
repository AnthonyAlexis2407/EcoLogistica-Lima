import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import DashboardPage from '../pages/DashboardPage';
import { indicadoresApi, pedidosApi, vehiculosApi } from '../api';

vi.mock('../AuthContext', () => ({
  useAuth: () => ({ token: 'tok', user: { nombre: 'Ana Pérez' } }),
}));
vi.mock('../api', () => ({
  vehiculosApi: { count: vi.fn(), list: vi.fn() },
  pedidosApi: { count: vi.fn(), list: vi.fn() },
  indicadoresApi: { resumen: vi.fn() },
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
    vi.mocked(indicadoresApi.resumen).mockRejectedValue(new Error('sin datos'));

    render(<MemoryRouter><DashboardPage /></MemoryRouter>);

    expect(screen.getByText('Bienvenido, Ana Pérez')).toBeInTheDocument();
    expect(await screen.findByText('4 pendientes · 2 en ruta')).toBeInTheDocument();
    expect(screen.getByText(/2 unidades operativas \(1[.,\s]?500 kg\)/)).toBeInTheDocument();
    expect(screen.getByText('1.50')).toBeInTheDocument();
    expect(screen.getByText('1 de 7 pedidos entregados')).toBeInTheDocument();
  });

  it('usa valores por defecto si la API falla', async () => {
    vi.mocked(vehiculosApi.count).mockRejectedValue(new Error('x'));
    vi.mocked(pedidosApi.count).mockRejectedValue(new Error('x'));
    vi.mocked(vehiculosApi.list).mockRejectedValue(new Error('x'));
    vi.mocked(pedidosApi.list).mockRejectedValue(new Error('x'));
    vi.mocked(indicadoresApi.resumen).mockRejectedValue(new Error('x'));

    render(<MemoryRouter><DashboardPage /></MemoryRouter>);

    expect(await screen.findByText('0 pendientes · 0 en ruta')).toBeInTheDocument();
    expect(screen.getByText('—')).toBeInTheDocument(); // sin vehículos no se inventa un factor de emisión
    expect(screen.getByText(/Aún no hay rutas optimizadas/)).toBeInTheDocument();
    expect(screen.getByText('Sin pedidos registrados')).toBeInTheDocument();
  });

  it('entrega la ilustración con AVIF y WebP adaptativos y respaldo PNG (picture)', () => {
    vi.mocked(vehiculosApi.count).mockResolvedValue({});
    vi.mocked(pedidosApi.count).mockResolvedValue({});
    vi.mocked(vehiculosApi.list).mockResolvedValue([]);
    vi.mocked(pedidosApi.list).mockResolvedValue([]);
    vi.mocked(indicadoresApi.resumen).mockRejectedValue(new Error('x'));

    const { container } = render(<MemoryRouter><DashboardPage /></MemoryRouter>);

    const fuentes = Array.from(container.querySelectorAll('picture.hero-ilustracion source'));
    expect(fuentes.map((f) => f.getAttribute('type'))).toEqual(['image/avif', 'image/webp']);
    for (const fuente of fuentes) {
      expect(fuente.getAttribute('srcset')).toMatch(/280w, .*560w/);
      expect(fuente.getAttribute('sizes')).toBe('280px');
    }
    const img = container.querySelector('picture.hero-ilustracion img')!;
    expect(img.getAttribute('src')).toBe('/img/hero-rutas-560.png');
    expect(img.getAttribute('width')).toBe('280');
    expect(img.getAttribute('height')).toBe('160');
    expect(img.getAttribute('alt')).toBe('');
    expect(img.getAttribute('loading')).toBe('lazy');
    expect(img.getAttribute('decoding')).toBe('async');
  });

  it('muestra los indicadores reales de rutas y de CO₂ evitado (RF-005, RF-010)', async () => {
    vi.mocked(vehiculosApi.count).mockResolvedValue({});
    vi.mocked(pedidosApi.count).mockResolvedValue({});
    vi.mocked(vehiculosApi.list).mockResolvedValue([]);
    vi.mocked(pedidosApi.list).mockResolvedValue([]);
    vi.mocked(indicadoresApi.resumen).mockResolvedValue({
      vehiculos: {}, pedidos: {}, rutas_activas: 3, distancia_planificada_km: 120.5, co2_planificado_kg: 30.2,
      pedidos_en_ventana_pct: 87.5, optimizaciones: 2, co2_evitado_kg: 410.3, ahorro_co2_pct: 82.1, ahorro_km_pct: 81.9,
      arboles_equivalentes: 18.85,
    });

    render(<MemoryRouter><DashboardPage /></MemoryRouter>);

    expect(await screen.findByText('2 optimizaciones')).toBeInTheDocument();
    expect(screen.getByText(/410[.,\s]?3 kg/)).toBeInTheDocument();
    expect(screen.getByText(/82\.1% menos CO₂ y 81\.9% menos km/)).toBeInTheDocument();
    expect(screen.getByText(/18[.,]85 árboles/)).toBeInTheDocument();
    expect(screen.getByText('87.5%')).toBeInTheDocument();
  });
});
