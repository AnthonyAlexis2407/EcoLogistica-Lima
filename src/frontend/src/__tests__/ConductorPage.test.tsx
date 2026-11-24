import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ConductorPage from '../pages/ConductorPage';
import { ApiError, conductorApi, rutasApi, type Ruta } from '../api';
import { guardarRuta, leerCola } from '../offline';

// Leaflet necesita un navegador real; en jsdom se sustituye por un doble.
const mapaDoble = vi.hoisted(() => {
  const objeto = { addTo: vi.fn().mockReturnThis() };
  const mapa = { setView: vi.fn().mockReturnThis(), fitBounds: vi.fn(), remove: vi.fn() };
  const grupo = { addTo: vi.fn().mockReturnThis(), clearLayers: vi.fn() };
  return {
    L: {
      map: vi.fn(() => mapa), tileLayer: vi.fn(() => objeto), layerGroup: vi.fn(() => grupo), marker: vi.fn(() => objeto),
      circleMarker: vi.fn(() => objeto), divIcon: vi.fn(() => ({})), latLngBounds: vi.fn(() => ({})),
    },
  };
});
vi.mock('leaflet', () => ({ default: mapaDoble.L }));
vi.mock('../AuthContext', () => ({ useAuth: () => ({ token: 'tok', user: { nombre: 'Chofer', rol: 'CONDUCTOR' } }) }));
vi.mock('../api', async (original) => ({
  ...(await original<typeof import('../api')>()),
  conductorApi: { miRuta: vi.fn(), sincronizar: vi.fn(), ubicacion: vi.fn(), entregar: vi.fn(), reprogramar: vi.fn() },
  rutasApi: { iniciar: vi.fn(), completar: vi.fn() },
}));

const parada = (n: number, estado = 'PENDIENTE') => ({
  parada_id: `pa${n}`, pedido_id: `pe${n}`, orden: n, estado, direccion: `Jr. Prueba ${n}00`, latitud: -12.05 - n / 100, longitud: -77.03,
  peso_kg: 120, distancia_desde_anterior_km: 2, llegada_estimada: '2026-11-24T14:00:00', espera_min: 0, en_ventana: true,
  ventana_fin: '2026-11-24T18:00:00',
});
const ruta = (estado: string, paradas = [parada(1), parada(2)]): Ruta => ({
  ruta_id: 'r1', vehiculo_id: 'v1', placa: 'ABC-123', tipo_combustible: 'DIESEL', capacidad_kg: 1500, estado,
  distancia_km: 18.4, carga_kg: 240, co2_kg: 5, duracion_min: 60, paradas,
});

function enLinea(valor: boolean) {
  Object.defineProperty(window.navigator, 'onLine', { value: valor, configurable: true });
}

beforeEach(() => {
  vi.clearAllMocks();
  enLinea(true);
  vi.mocked(conductorApi.sincronizar).mockRejectedValue(new TypeError('Failed to fetch'));
});
afterEach(() => enLinea(true));

describe('ConductorPage (RF-004, RF-008, RNF-004, RNF-010)', () => {
  it('sin ruta asignada lo indica', async () => {
    vi.mocked(conductorApi.miRuta).mockRejectedValue(new ApiError(404, 'No tiene una ruta asignada'));
    render(<ConductorPage />);
    expect(await screen.findByRole('heading', { name: 'Sin ruta asignada' })).toBeInTheDocument();
  });

  it('una ruta planificada se inicia con un solo toque', async () => {
    const usuario = userEvent.setup();
    vi.mocked(conductorApi.miRuta).mockResolvedValue(ruta('PLANIFICADA'));
    vi.mocked(rutasApi.iniciar).mockResolvedValue(ruta('EN_CURSO'));
    render(<ConductorPage />);
    await usuario.click(await screen.findByRole('button', { name: /Iniciar ruta/ }));
    expect(rutasApi.iniciar).toHaveBeenCalledWith('tok', 'r1');
    expect(await screen.findByText(/Ruta iniciada/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Entregar parada 1' })).toBeInTheDocument();
  });

  it('Entregar abre la confirmación; sin evidencia (firma o foto) no se puede confirmar (RN-007)', async () => {
    const usuario = userEvent.setup();
    vi.mocked(conductorApi.miRuta).mockResolvedValue(ruta('EN_CURSO'));
    render(<ConductorPage />);
    await usuario.click(await screen.findByRole('button', { name: 'Entregar parada 1' }));
    expect(screen.getByRole('dialog', { name: 'Confirmar entrega' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Confirmar/ })).toBeDisabled();
    expect(screen.getByLabelText('Espacio para la firma del receptor')).toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: 'Volver' }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('reprogramar guarda la acción en la cola y la marca pendiente de sincronizar', async () => {
    const usuario = userEvent.setup();
    vi.mocked(conductorApi.miRuta).mockResolvedValue(ruta('EN_CURSO'));
    render(<ConductorPage />);
    await usuario.click(await screen.findByRole('button', { name: 'No pude entregar la parada 1' }));
    await usuario.selectOptions(screen.getByLabelText('Motivo'), 'Local cerrado');
    await usuario.click(screen.getByRole('button', { name: 'Reprogramar' }));

    expect(await screen.findByText('Reprogramada')).toBeInTheDocument();
    expect(await screen.findByText(/1 acción\(es\) pendiente\(s\) de sincronizar/)).toBeInTheDocument();
    const cola = leerCola();
    expect(cola).toHaveLength(1);
    expect(cola[0]).toMatchObject({ tipo: 'REPROGRAMACION', parada_id: 'pa1', motivo: 'Local cerrado' });
    expect(cola[0].clave_sync.length).toBeGreaterThanOrEqual(8);
  });

  it('sin conexión muestra la última ruta descargada y lo avisa', async () => {
    enLinea(false);
    guardarRuta(ruta('EN_CURSO'));
    vi.mocked(conductorApi.miRuta).mockRejectedValue(new TypeError('Failed to fetch'));
    render(<ConductorPage />);
    expect(await screen.findByText(/Sin conexión/)).toBeInTheDocument();
    expect(screen.getByText(/Jr\. Prueba 100/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Entregar parada 1' })).toBeInTheDocument();
  });

  it('con todas las paradas resueltas ofrece terminar la ruta', async () => {
    const usuario = userEvent.setup();
    vi.mocked(conductorApi.miRuta).mockResolvedValue(ruta('EN_CURSO', [parada(1, 'ENTREGADA'), parada(2, 'REPROGRAMADA')]));
    vi.mocked(rutasApi.completar).mockResolvedValue({ mensaje: 'Ruta completada. CO₂ evitado: 3.20 kg' });
    render(<ConductorPage />);
    await usuario.click(await screen.findByRole('button', { name: /Terminar ruta/ }));
    await waitFor(() => expect(rutasApi.completar).toHaveBeenCalledWith('tok', 'r1'));
    expect(await screen.findByText(/Ruta completada/)).toBeInTheDocument();
  });
});
