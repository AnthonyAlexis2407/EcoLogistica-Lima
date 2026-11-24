import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import RutasPage from '../pages/RutasPage';
import { ApiError, reportesApi, rutasApi, type Optimizacion, type Ruta, type RutasActivas } from '../api';

// Leaflet necesita un navegador real (medidas de pantalla); en jsdom se sustituye por un doble que registra las llamadas.
const mapaDoble = vi.hoisted(() => {
  const objeto = { addTo: vi.fn().mockReturnThis() };
  const mapa = { setView: vi.fn().mockReturnThis(), fitBounds: vi.fn(), remove: vi.fn() };
  const grupo = { addTo: vi.fn().mockReturnThis(), clearLayers: vi.fn() };
  return {
    mapa, grupo, objeto,
    L: {
      map: vi.fn(() => mapa), tileLayer: vi.fn(() => objeto), layerGroup: vi.fn(() => grupo),
      polyline: vi.fn(() => objeto), marker: vi.fn(() => objeto), circleMarker: vi.fn(() => objeto),
      divIcon: vi.fn(() => ({})), latLngBounds: vi.fn(() => ({})),
    },
  };
});
vi.mock('leaflet', () => ({ default: mapaDoble.L }));

let rol = 'OPERADOR';
vi.mock('../AuthContext', () => ({
  useAuth: () => ({ token: 'tok', user: { nombre: 'Ana Pérez', rol } }),
}));
vi.mock('../api', async (original) => ({
  ...(await original<typeof import('../api')>()),
  rutasApi: { activas: vi.fn(), optimizar: vi.fn(), cancelar: vi.fn() },
  reportesApi: { descargar: vi.fn() },
}));

const ruta: Ruta = {
  ruta_id: 'r1', vehiculo_id: 'v1', placa: 'ABC-123', tipo_combustible: 'DIESEL', capacidad_kg: 1500, estado: 'PLANIFICADA',
  distancia_km: 42.3, carga_kg: 900, co2_kg: 16.2, duracion_min: 95,
  paradas: [
    { pedido_id: 'p1', orden: 1, direccion: 'Av. Lima 100', latitud: -12.05, longitud: -77.03, peso_kg: 400,
      distancia_desde_anterior_km: 5.1, llegada_estimada: '2026-11-24T14:00:00', espera_min: 0, en_ventana: true },
    { pedido_id: 'p2', orden: 2, direccion: 'Jr. Cusco 200', latitud: -12.06, longitud: -77.04, peso_kg: 500,
      distancia_desde_anterior_km: 3.2, llegada_estimada: '2026-11-24T14:30:00', espera_min: 12, en_ventana: false },
  ],
};
const activas = (rutas: Ruta[]): RutasActivas => ({ deposito: { latitud: -12.0464, longitud: -77.0428 }, rutas });

const optimizacion: Optimizacion = {
  optimizacion_id: 'o1', algoritmo: 'Clarke-Wright + 2-opt', pedidos_planificados: 2, pedidos_sin_asignar: 1,
  distancia_km: 42.3, distancia_base_km: 120, ahorro_km_pct: 64.8, co2_kg: 16.2, co2_base_kg: 45.9, co2_evitado_kg: 29.7,
  ahorro_co2_pct: 64.7, arboles_equivalentes: 1.36, tiempo_ms: 12.4, limite_alcanzado: false, rutas: [ruta],
  sin_asignar: [{ pedido_id: 'abcdef123456', motivo: 'No hay más vehículos disponibles para cubrir todas las rutas' }],
};

beforeEach(() => {
  vi.clearAllMocks();
  rol = 'OPERADOR';
  vi.mocked(rutasApi.activas).mockResolvedValue(activas([]));
});

describe('RutasPage', () => {
  it('sin rutas muestra el estado vacío y la indicación de optimizar', async () => {
    render(<RutasPage />);
    expect(await screen.findByText('Sin rutas planificadas')).toBeInTheDocument();
    expect(screen.getByText(/pulse «Optimizar rutas»/)).toBeInTheDocument();
    expect(screen.getByRole('region', { name: 'Mapa de rutas' })).toBeInTheDocument();
  });

  it('crea el mapa una sola vez y lo destruye al salir', async () => {
    const { unmount } = render(<RutasPage />);
    await screen.findByText('Sin rutas planificadas');
    expect(mapaDoble.L.map).toHaveBeenCalledTimes(1);
    expect(mapaDoble.L.tileLayer).toHaveBeenCalledWith(expect.stringContaining('tile.openstreetmap.org'), expect.anything());
    unmount();
    expect(mapaDoble.mapa.remove).toHaveBeenCalledTimes(1);
  });

  it('lista las rutas con sus paradas, la ventana horaria y dibuja el recorrido', async () => {
    vi.mocked(rutasApi.activas).mockResolvedValue(activas([ruta]));
    render(<RutasPage />);

    expect(await screen.findByText('Vehículo ABC-123')).toBeInTheDocument();
    expect(screen.getByText('Av. Lima 100')).toBeInTheDocument();
    expect(screen.getByText('En ventana')).toBeInTheDocument();
    expect(screen.getByText('Fuera de ventana')).toBeInTheDocument();
    expect(screen.getByText(/espera 12 min/)).toBeInTheDocument();
    expect(mapaDoble.L.polyline).toHaveBeenCalledTimes(1); // un recorrido por ruta
    expect(mapaDoble.L.marker).toHaveBeenCalledTimes(2); // una marca por parada
    expect(mapaDoble.mapa.fitBounds).toHaveBeenCalled();
  });

  it('optimizar muestra el CO₂ evitado, la compensación, el tiempo y los pedidos sin asignar', async () => {
    vi.mocked(rutasApi.optimizar).mockResolvedValue(optimizacion);
    const usuario = userEvent.setup();
    render(<RutasPage />);

    await usuario.click(await screen.findByRole('button', { name: /Optimizar rutas/ }));

    expect(await screen.findByText('29.7')).toBeInTheDocument();
    expect(screen.getByText('64.7% menos que sin optimizar')).toBeInTheDocument();
    expect(screen.getByText('1.36')).toBeInTheDocument();
    expect(screen.getByText(/SLA: 45 000 ms/)).toBeInTheDocument();
    expect(screen.getByText('1 pedido(s) sin asignar')).toBeInTheDocument();
    expect(screen.getByText(/abcdef12: No hay más vehículos/)).toBeInTheDocument();
    expect(screen.getByText(/2 pedidos planificados en 1 rutas/)).toBeInTheDocument();
    expect(rutasApi.activas).toHaveBeenCalledTimes(2); // recarga el plan tras optimizar
  });

  it('muestra el mensaje del servidor si no hay pedidos pendientes', async () => {
    vi.mocked(rutasApi.optimizar).mockRejectedValue(new ApiError(409, 'No hay pedidos pendientes para planificar'));
    const usuario = userEvent.setup();
    render(<RutasPage />);
    await usuario.click(await screen.findByRole('button', { name: /Optimizar rutas/ }));
    expect(await screen.findByText(/No hay pedidos pendientes para planificar/)).toBeInTheDocument();
  });

  it('informa un error de conexión si la API no responde', async () => {
    vi.mocked(rutasApi.optimizar).mockRejectedValue(new Error('caída'));
    const usuario = userEvent.setup();
    render(<RutasPage />);
    await usuario.click(await screen.findByRole('button', { name: /Optimizar rutas/ }));
    expect(await screen.findByText(/Error de conexión/)).toBeInTheDocument();
  });

  it('cancelar una ruta pide confirmación y recarga el plan', async () => {
    vi.mocked(rutasApi.activas).mockResolvedValue(activas([ruta]));
    vi.mocked(rutasApi.cancelar).mockResolvedValue({ mensaje: 'ok' });
    const confirmar = vi.spyOn(window, 'confirm');
    const usuario = userEvent.setup();
    render(<RutasPage />);

    const boton = await screen.findByRole('button', { name: 'Cancelar la ruta del vehículo ABC-123' });
    confirmar.mockReturnValueOnce(false);
    await usuario.click(boton);
    expect(rutasApi.cancelar).not.toHaveBeenCalled();

    confirmar.mockReturnValueOnce(true);
    await usuario.click(boton);
    await waitFor(() => expect(rutasApi.cancelar).toHaveBeenCalledWith('tok', 'r1'));
    expect(await screen.findByText(/Ruta del vehículo ABC-123 cancelada/)).toBeInTheDocument();
    confirmar.mockRestore();
  });

  it('el auditor consulta pero no ve los botones de optimizar ni de cancelar', async () => {
    rol = 'AUDITOR';
    vi.mocked(rutasApi.activas).mockResolvedValue(activas([ruta]));
    render(<RutasPage />);
    await screen.findByText('Vehículo ABC-123');
    expect(screen.queryByRole('button', { name: /Optimizar rutas/ })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Cancelar la ruta/ })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Pedidos \(CSV\)/ })).toBeInTheDocument();
  });

  it('descarga el reporte CSV con el token y ofrece el archivo', async () => {
    const blob = new Blob(['a,b'], { type: 'text/csv' });
    vi.mocked(reportesApi.descargar).mockResolvedValue(blob);
    const crear = vi.fn(() => 'blob:prueba');
    const revocar = vi.fn();
    vi.stubGlobal('URL', { createObjectURL: crear, revokeObjectURL: revocar });
    const clic = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
    const usuario = userEvent.setup();
    render(<RutasPage />);

    await usuario.click(await screen.findByRole('button', { name: /Ambiental \(CSV\)/ }));

    await waitFor(() => expect(reportesApi.descargar).toHaveBeenCalledWith('tok', 'ambiental'));
    expect(crear).toHaveBeenCalledWith(blob);
    expect(clic).toHaveBeenCalled();
    expect(revocar).toHaveBeenCalledWith('blob:prueba');
    clic.mockRestore();
    vi.unstubAllGlobals();
  });

  it('informa si no se pudo descargar el reporte', async () => {
    vi.mocked(reportesApi.descargar).mockRejectedValue(new ApiError(403, 'Acceso denegado'));
    const usuario = userEvent.setup();
    render(<RutasPage />);
    await usuario.click(await screen.findByRole('button', { name: /Rutas \(CSV\)/ }));
    expect(await screen.findByText(/Acceso denegado/)).toBeInTheDocument();
  });
});
