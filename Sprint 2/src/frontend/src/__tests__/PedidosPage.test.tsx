import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PedidosPage from '../pages/PedidosPage';
import { ApiError, pedidosApi, type Pedido } from '../api';

vi.mock('../AuthContext', () => ({
  useAuth: () => ({ token: 'tok', user: { nombre: 'Ana', rol: 'OPERADOR' } }),
}));
vi.mock('../api', async (original) => ({
  ...(await original<typeof import('../api')>()),
  pedidosApi: { list: vi.fn(), create: vi.fn(), cancel: vi.fn() },
}));

const pedido = (id: string, direccion: string, estado: string): Pedido => ({
  pedido_id: id, bodega_id: 'b1', direccion, latitud: -12, longitud: -77, peso_kg: 120,
  ventana_inicio: '2026-10-20T10:00:00Z', ventana_fin: '2026-10-20T12:00:00Z',
  estado, creado_en: '2026-10-20T08:00:00Z',
});

const lista = [
  pedido('p1', 'Jr. Los Pinos 123, El Agustino', 'PENDIENTE'),
  pedido('p2', 'Av. Lima 456, Ate', 'CANCELADO'),
];

beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(pedidosApi.list).mockResolvedValue(lista);
});

describe('PedidosPage (US-003)', () => {
  it('lista los pedidos registrados', async () => {
    render(<PedidosPage />);
    expect(screen.getByText('Cargando cola de pedidos...')).toBeInTheDocument();
    expect(await screen.findByText(/Los Pinos 123/)).toBeInTheDocument();
    expect(screen.getByText(/Av. Lima 456/)).toBeInTheDocument();
  });

  it('filtra por dirección en la tabla', async () => {
    const usuario = userEvent.setup();
    render(<PedidosPage />);
    await screen.findByText(/Los Pinos 123/);

    await usuario.type(screen.getByPlaceholderText('Buscar por dirección...'), 'ate');
    expect(screen.queryByText(/Los Pinos 123/)).not.toBeInTheDocument();
    expect(screen.getByText(/Av. Lima 456/)).toBeInTheDocument();
  });

  it('pide al servidor solo el estado elegido', async () => {
    const usuario = userEvent.setup();
    render(<PedidosPage />);
    await screen.findByText(/Los Pinos 123/);

    await usuario.selectOptions(screen.getByRole('combobox'), 'CANCELADO');
    await vi.waitFor(() => expect(pedidosApi.list).toHaveBeenLastCalledWith('tok', 'CANCELADO'));
  });

  it('registra un pedido con el formulario prellenado', async () => {
    const usuario = userEvent.setup();
    vi.mocked(pedidosApi.create).mockResolvedValue(lista[0]);
    render(<PedidosPage />);
    await screen.findByText(/Los Pinos 123/);

    await usuario.click(screen.getByRole('button', { name: /Registrar Pedido/ }));
    const dialogo = screen.getByRole('dialog');
    await usuario.click(within(dialogo).getByRole('button', { name: /Registrar/ , hidden: false }));

    expect(pedidosApi.create).toHaveBeenCalledWith(
      'tok',
      expect.objectContaining({ bodega_id: 'b1', peso_kg: 350 }),
    );
    expect(await screen.findByText(/Pedido registrado exitosamente/)).toBeInTheDocument();
  });

  it('muestra el rechazo por capacidad dentro del formulario', async () => {
    const usuario = userEvent.setup();
    vi.mocked(pedidosApi.create).mockRejectedValue(new ApiError(422, 'El peso excede la capacidad máxima'));
    render(<PedidosPage />);
    await screen.findByText(/Los Pinos 123/);

    await usuario.click(screen.getByRole('button', { name: /Registrar Pedido/ }));
    const dialogo = screen.getByRole('dialog');
    await usuario.click(within(dialogo).getByRole('button', { name: /Registrar/ }));

    expect(await within(dialogo).findByText(/excede la capacidad/)).toBeInTheDocument();
  });

  it('informa error de conexión si el registro falla por red', async () => {
    const usuario = userEvent.setup();
    vi.mocked(pedidosApi.create).mockRejectedValue(new Error('network'));
    render(<PedidosPage />);
    await screen.findByText(/Los Pinos 123/);

    await usuario.click(screen.getByRole('button', { name: /Registrar Pedido/ }));
    await usuario.click(within(screen.getByRole('dialog')).getByRole('button', { name: /Registrar/ }));

    expect(await screen.findByText('Error de conexión')).toBeInTheDocument();
  });

  it('cancela un pedido pendiente tras confirmar y no ofrece cancelar los ya cancelados', async () => {
    const usuario = userEvent.setup();
    vi.mocked(pedidosApi.cancel).mockResolvedValue({ mensaje: 'ok' });
    vi.spyOn(window, 'confirm').mockReturnValueOnce(false).mockReturnValueOnce(true);
    render(<PedidosPage />);
    await screen.findByText(/Los Pinos 123/);

    const cancelar = screen.getByRole('button', { name: 'Cancelar' });
    expect(screen.getAllByRole('button', { name: 'Cancelar' })).toHaveLength(1);

    await usuario.click(cancelar);
    expect(pedidosApi.cancel).not.toHaveBeenCalled();

    await usuario.click(cancelar);
    expect(pedidosApi.cancel).toHaveBeenCalledWith('tok', 'p1');
    expect(await screen.findByText(/Pedido cancelado/)).toBeInTheDocument();
  });

  it('muestra el error del servidor si la cancelación falla', async () => {
    const usuario = userEvent.setup();
    vi.mocked(pedidosApi.cancel).mockRejectedValue(new ApiError(400, 'El pedido ya se encuentra cancelado'));
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    render(<PedidosPage />);
    await screen.findByText(/Los Pinos 123/);

    await usuario.click(screen.getByRole('button', { name: 'Cancelar' }));
    expect(await screen.findByText(/ya se encuentra cancelado/)).toBeInTheDocument();
  });

  it('cierra el modal haciendo clic fuera del cuadro', async () => {
    const usuario = userEvent.setup();
    render(<PedidosPage />);
    await screen.findByText(/Los Pinos 123/);

    await usuario.click(screen.getByRole('button', { name: /Registrar Pedido/ }));
    const dialogo = screen.getByRole('dialog');
    await usuario.click(dialogo); // el clic dentro no cierra
    expect(screen.getByRole('dialog')).toBeInTheDocument();

    await usuario.click(dialogo.parentElement as HTMLElement);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });
});
