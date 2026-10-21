import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import VehiculosPage from '../pages/VehiculosPage';
import { ApiError, vehiculosApi, type Vehiculo } from '../api';

const sesion = vi.hoisted(() => ({ rol: 'ADMIN_FLOTA' }));
vi.mock('../AuthContext', () => ({
  useAuth: () => ({ token: 'tok', user: { nombre: 'Ana', rol: sesion.rol } }),
}));
vi.mock('../api', async (original) => ({
  ...(await original<typeof import('../api')>()),
  vehiculosApi: { list: vi.fn(), create: vi.fn(), update: vi.fn(), delete: vi.fn() },
}));

const flota: Vehiculo[] = [
  { vehiculo_id: 'v1', placa: 'ABC-123', capacidad_kg: 1500, tipo_combustible: 'DIESEL', factor_emision_co2: 2.68, estado: 'DISPONIBLE' },
  { vehiculo_id: 'v2', placa: 'XYZ-987', capacidad_kg: 800, tipo_combustible: 'ELECTRICO', factor_emision_co2: null, estado: 'FUERA_DE_SERVICIO' },
];

beforeEach(() => {
  sesion.rol = 'ADMIN_FLOTA';
  vi.resetAllMocks();
  vi.mocked(vehiculosApi.list).mockResolvedValue(flota);
});

describe('VehiculosPage (US-001)', () => {
  it('lista los vehículos de la flota', async () => {
    render(<VehiculosPage />);
    expect(screen.getByText('Cargando catálogo de flota...')).toBeInTheDocument();
    expect(await screen.findByText('ABC-123')).toBeInTheDocument();
    expect(screen.getByText('XYZ-987')).toBeInTheDocument();
  });

  it('filtra por placa y por estado', async () => {
    const usuario = userEvent.setup();
    render(<VehiculosPage />);
    await screen.findByText('ABC-123');

    await usuario.type(screen.getByPlaceholderText('Buscar por placa...'), 'xyz');
    expect(screen.queryByText('ABC-123')).not.toBeInTheDocument();
    expect(screen.getByText('XYZ-987')).toBeInTheDocument();

    await usuario.clear(screen.getByPlaceholderText('Buscar por placa...'));
    await usuario.selectOptions(screen.getByRole('combobox'), 'DISPONIBLE');
    expect(screen.queryByText('XYZ-987')).not.toBeInTheDocument();
    expect(screen.getByText('ABC-123')).toBeInTheDocument();
  });

  it('registra un vehículo nuevo y recarga la lista', async () => {
    const usuario = userEvent.setup();
    vi.mocked(vehiculosApi.create).mockResolvedValue(flota[0]);
    render(<VehiculosPage />);
    await screen.findByText('ABC-123');

    await usuario.click(screen.getByRole('button', { name: /Registrar Vehículo/ }));
    const dialogo = screen.getByRole('dialog');
    await usuario.type(within(dialogo).getByLabelText('Placa del Vehículo *'), 'new-001');
    await usuario.click(within(dialogo).getByRole('button', { name: 'Registrar Vehículo' }));

    expect(vehiculosApi.create).toHaveBeenCalledWith('tok', expect.objectContaining({ placa: 'NEW-001' }));
    expect(await screen.findByText(/registrado en la flota/)).toBeInTheDocument();
    expect(vehiculosApi.list).toHaveBeenCalledTimes(2);
  });

  it('muestra el rechazo por placa duplicada dentro del formulario', async () => {
    const usuario = userEvent.setup();
    vi.mocked(vehiculosApi.create).mockRejectedValue(new ApiError(409, 'Registro rechazado por duplicidad'));
    render(<VehiculosPage />);
    await screen.findByText('ABC-123');

    await usuario.click(screen.getByRole('button', { name: /Registrar Vehículo/ }));
    const dialogo = screen.getByRole('dialog');
    await usuario.type(within(dialogo).getByLabelText('Placa del Vehículo *'), 'abc-123');
    await usuario.click(within(dialogo).getByRole('button', { name: 'Registrar Vehículo' }));

    expect(await within(dialogo).findByText(/rechazado por duplicidad/)).toBeInTheDocument();
  });

  it('informa error de conexión cuando falla la red al guardar', async () => {
    const usuario = userEvent.setup();
    vi.mocked(vehiculosApi.create).mockRejectedValue(new Error('network'));
    render(<VehiculosPage />);
    await screen.findByText('ABC-123');

    await usuario.click(screen.getByRole('button', { name: /Registrar Vehículo/ }));
    const dialogo = screen.getByRole('dialog');
    await usuario.type(within(dialogo).getByLabelText('Placa del Vehículo *'), 'ERR-001');
    await usuario.click(within(dialogo).getByRole('button', { name: 'Registrar Vehículo' }));

    expect(await within(dialogo).findByText(/Error de conexión/)).toBeInTheDocument();
  });

  it('edita un vehículo existente', async () => {
    const usuario = userEvent.setup();
    vi.mocked(vehiculosApi.update).mockResolvedValue(flota[0]);
    render(<VehiculosPage />);
    await screen.findByText('ABC-123');

    await usuario.click(screen.getAllByTitle('Editar')[0]);
    const dialogo = screen.getByRole('dialog');
    expect(within(dialogo).getByText('Editar Vehículo')).toBeInTheDocument();
    await usuario.click(within(dialogo).getByRole('button', { name: 'Guardar Cambios' }));

    expect(vehiculosApi.update).toHaveBeenCalledWith('tok', 'v1', expect.objectContaining({ placa: 'ABC-123' }));
    expect(await screen.findByText(/actualizado exitosamente/)).toBeInTheDocument();
  });

  it('el filtro y el botón de cierre tienen nombre accesible y Escape cierra el modal (WCAG)', async () => {
    const usuario = userEvent.setup();
    render(<VehiculosPage />);
    await screen.findByText('ABC-123');
    expect(screen.getByRole('combobox', { name: 'Filtrar por estado' })).toBeInTheDocument();

    await usuario.click(screen.getByRole('button', { name: /Registrar Vehículo/ }));
    expect(screen.getByRole('button', { name: 'Cerrar ventana' })).toBeInTheDocument();
    await usuario.keyboard('{Escape}');
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('cierra el modal con Cancelar', async () => {
    const usuario = userEvent.setup();
    render(<VehiculosPage />);
    await screen.findByText('ABC-123');

    await usuario.click(screen.getByRole('button', { name: /Registrar Vehículo/ }));
    await usuario.click(screen.getByRole('button', { name: 'Cancelar' }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('da de baja un vehículo solo tras confirmar', async () => {
    const usuario = userEvent.setup();
    vi.mocked(vehiculosApi.delete).mockResolvedValue({ mensaje: 'ok' });
    const confirmar = vi.spyOn(window, 'confirm').mockReturnValueOnce(false).mockReturnValueOnce(true);
    render(<VehiculosPage />);
    await screen.findByText('ABC-123');

    // Solo el vehículo en servicio ofrece "Dar de baja".
    const baja = screen.getByTitle('Dar de baja');
    await usuario.click(baja);
    expect(vehiculosApi.delete).not.toHaveBeenCalled();

    await usuario.click(baja);
    expect(vehiculosApi.delete).toHaveBeenCalledWith('tok', 'v1');
    expect(await screen.findByText(/dado de baja/)).toBeInTheDocument();
    expect(confirmar).toHaveBeenCalledTimes(2);
  });

  it('muestra el error del servidor si la baja falla', async () => {
    const usuario = userEvent.setup();
    vi.mocked(vehiculosApi.delete).mockRejectedValue(new ApiError(403, 'Sin permiso'));
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    render(<VehiculosPage />);
    await screen.findByText('ABC-123');

    await usuario.click(screen.getByTitle('Dar de baja'));
    expect(await screen.findByText(/Sin permiso/)).toBeInTheDocument();
  });

  it.each(['OPERADOR', 'AUDITOR'])('el rol %s solo consulta: sin botones de alta, edición ni baja (RBAC)', async (rol) => {
    sesion.rol = rol;
    render(<VehiculosPage />);
    await screen.findByText('ABC-123');

    expect(screen.queryByRole('button', { name: /Registrar Vehículo/ })).not.toBeInTheDocument();
    expect(screen.queryByTitle('Editar')).not.toBeInTheDocument();
    expect(screen.queryByTitle('Dar de baja')).not.toBeInTheDocument();
  });

  it('tolera un fallo al cargar la lista', async () => {
    vi.mocked(vehiculosApi.list).mockRejectedValue(new Error('x'));
    render(<VehiculosPage />);
    await vi.waitFor(() => expect(screen.queryByText('Cargando catálogo de flota...')).not.toBeInTheDocument());
  });
});
