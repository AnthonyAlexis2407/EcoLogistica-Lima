import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AdminPage from '../pages/AdminPage';
import NotificacionesPage from '../pages/NotificacionesPage';
import { adminApi, notificacionesApi, privacidadApi, type Notificacion } from '../api';

let rol = 'ADMIN_FLOTA';
vi.mock('../AuthContext', () => ({
  useAuth: () => ({ token: 'tok', user: { usuario_id: 'yo', nombre: 'Ana', rol } }),
}));
vi.mock('../api', async (original) => ({
  ...(await original<typeof import('../api')>()),
  adminApi: {
    usuarios: vi.fn(), conductores: vi.fn(), crearConductor: vi.fn(), actualizarConductor: vi.fn(), parametros: vi.fn(),
    guardarParametros: vi.fn(), zonas: vi.fn(), crearZona: vi.fn(), eliminarZona: vi.fn(), solicitudes: vi.fn(),
    atenderSolicitud: vi.fn(), actualizarUsuario: vi.fn(), eliminarUsuario: vi.fn(),
  },
  notificacionesApi: { mias: vi.fn(), pendientesDeContacto: vi.fn(), marcarLeida: vi.fn() },
  privacidadApi: { solicitarBaja: vi.fn() },
}));

const aviso = (id: string, tipo: string, leida = false): Notificacion => ({
  notificacion_id: id, pedido_id: 'p1', tipo, canal: 'PORTAL', mensaje: `Mensaje ${tipo}`, hora_estimada: '2026-11-24T15:30:00',
  estado_envio: 'ENVIADA', leida, creado_en: '2026-11-24T12:00:00',
});

beforeEach(() => {
  vi.resetAllMocks();
  rol = 'ADMIN_FLOTA';
  vi.mocked(adminApi.usuarios).mockResolvedValue([]);
  vi.mocked(adminApi.conductores).mockResolvedValue([]);
  vi.mocked(adminApi.zonas).mockResolvedValue([]);
  vi.mocked(adminApi.solicitudes).mockResolvedValue([]);
  vi.mocked(adminApi.parametros).mockResolvedValue({ velocidad_kmh: 25, servicio_min: 10, limite_segundos: 40, algoritmo: 'clarke_wright_2opt' });
  vi.mocked(notificacionesApi.pendientesDeContacto).mockResolvedValue([]);
});

describe('NotificacionesPage (RF-009, RN-010)', () => {
  it('lista los avisos de la cuenta, con la hora estimada, y permite marcarlos como leídos', async () => {
    const usuario = userEvent.setup();
    rol = 'BODEGA';
    vi.mocked(notificacionesApi.mias).mockResolvedValue({ items: [aviso('n1', 'ASIGNACION'), aviso('n2', 'ENTREGA', true)], noLeidas: 1 });
    vi.mocked(notificacionesApi.marcarLeida).mockResolvedValue({ mensaje: 'ok' });
    render(<NotificacionesPage />);

    expect(await screen.findByText('Mensaje ASIGNACION')).toBeInTheDocument();
    expect(screen.getByText('1 sin leer')).toBeInTheDocument();
    expect(screen.getAllByText(/Hora estimada/)).toHaveLength(2);
    expect(screen.queryByText('Clientes pendientes de contacto')).not.toBeInTheDocument(); // solo personal de la empresa
    await usuario.click(screen.getByRole('button', { name: 'Marcar como leída' }));
    expect(notificacionesApi.marcarLeida).toHaveBeenCalledWith('tok', 'n1');
  });

  it('el operador ve además los clientes pendientes de contacto', async () => {
    rol = 'OPERADOR';
    vi.mocked(notificacionesApi.mias).mockResolvedValue({ items: [], noLeidas: 0 });
    vi.mocked(notificacionesApi.pendientesDeContacto).mockResolvedValue([{ ...aviso('n9', 'ASIGNACION'), mensaje: 'Pendiente de contacto: asignado', estado_envio: 'NO_ENTREGADA' }]);
    render(<NotificacionesPage />);
    expect(await screen.findByText('Clientes pendientes de contacto')).toBeInTheDocument();
    expect(await screen.findByText(/Pendiente de contacto: asignado/)).toBeInTheDocument();
    expect(screen.getByText(/Aún no tiene avisos/)).toBeInTheDocument();
  });

  it('el titular puede pedir la eliminación de sus datos (5 días hábiles)', async () => {
    const usuario = userEvent.setup();
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    vi.mocked(notificacionesApi.mias).mockResolvedValue({ items: [], noLeidas: 0 });
    vi.mocked(privacidadApi.solicitarBaja).mockResolvedValue({
      solicitud_id: 's1', usuario_id: 'yo', estado: 'PENDIENTE', solicitada_en: '2026-11-24T10:00:00',
      plazo_limite: '2026-12-01T10:00:00', atendida_en: null,
    });
    render(<NotificacionesPage />);
    await usuario.click(await screen.findByRole('button', { name: /Solicitar eliminación/ }));
    expect(await screen.findByText(/Solicitud registrada/)).toBeInTheDocument();
  });
});

describe('AdminPage', () => {
  it('registra un conductor y recarga la lista', async () => {
    const usuario = userEvent.setup();
    vi.mocked(adminApi.crearConductor).mockResolvedValue({
      conductor_id: 'c1', usuario_id: 'u1', nombre: 'Luis', email: 'luis@eco.pe', licencia: 'Q99999999', telefono: null, activo: true,
    });
    render(<AdminPage />);
    await usuario.click(screen.getByRole('tab', { name: 'Conductores' }));
    await usuario.type(screen.getByLabelText('Nombre del conductor'), 'Luis');
    await usuario.type(screen.getByLabelText('Correo del conductor'), 'luis@eco.pe');
    await usuario.type(screen.getByLabelText('Contraseña del conductor'), 'ClaveSegura1');
    await usuario.type(screen.getByLabelText('Licencia'), 'Q99999999');
    await usuario.click(screen.getByRole('button', { name: 'Registrar conductor' }));
    await waitFor(() => expect(adminApi.crearConductor).toHaveBeenCalledWith('tok', expect.objectContaining({ licencia: 'Q99999999' })));
    expect(await screen.findByText(/Conductor registrado/)).toBeInTheDocument();
  });

  it('guarda los parámetros del algoritmo', async () => {
    const usuario = userEvent.setup();
    vi.mocked(adminApi.guardarParametros).mockImplementation(async (_t, p) => p);
    render(<AdminPage />);
    await usuario.click(screen.getByRole('tab', { name: 'Parámetros del algoritmo' }));
    const velocidad = await screen.findByLabelText('Velocidad media (km/h)');
    await usuario.clear(velocidad);
    await usuario.type(velocidad, '30');
    await usuario.click(screen.getByRole('button', { name: 'Guardar parámetros' }));
    await waitFor(() => expect(adminApi.guardarParametros).toHaveBeenCalledWith('tok', { velocidad_kmh: 30, servicio_min: 10, limite_segundos: 40, algoritmo: 'clarke_wright_2opt' }));
  });

  it('las zonas protegidas se registran y se eliminan con confirmación', async () => {
    const usuario = userEvent.setup();
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    vi.mocked(adminApi.zonas).mockResolvedValue([{ zona_id: 'z1', nombre: 'Reserva A', latitud: -12, longitud: -77, radio_km: 1.5, activa: true }]);
    vi.mocked(adminApi.eliminarZona).mockResolvedValue({ mensaje: 'ok' });
    render(<AdminPage />);
    await usuario.click(screen.getByRole('tab', { name: 'Zonas protegidas' }));
    await usuario.click(await screen.findByRole('button', { name: 'Eliminar la zona Reserva A' }));
    expect(adminApi.eliminarZona).toHaveBeenCalledWith('tok', 'z1');
  });

  it('la anonimización de datos pide confirmación y se atiende desde Privacidad', async () => {
    const usuario = userEvent.setup();
    const confirmar = vi.spyOn(window, 'confirm').mockReturnValue(true);
    vi.mocked(adminApi.solicitudes).mockResolvedValue([{
      solicitud_id: 's1', usuario_id: 'otro', estado: 'PENDIENTE', solicitada_en: '2026-11-24T10:00:00',
      plazo_limite: '2026-12-01T10:00:00', atendida_en: null,
    }]);
    vi.mocked(adminApi.atenderSolicitud).mockResolvedValue({
      solicitud_id: 's1', usuario_id: 'otro', estado: 'ATENDIDA', solicitada_en: '', plazo_limite: '', atendida_en: '',
    });
    render(<AdminPage />);
    await usuario.click(screen.getByRole('tab', { name: 'Privacidad' }));
    await usuario.click(await screen.findByRole('button', { name: 'Anonimizar datos' }));
    expect(confirmar).toHaveBeenCalled();
    expect(adminApi.atenderSolicitud).toHaveBeenCalledWith('tok', 's1');
  });
});
