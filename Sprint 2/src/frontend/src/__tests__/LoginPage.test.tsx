import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginPage from '../pages/LoginPage';
import { ApiError } from '../api';

const login = vi.fn();
vi.mock('../AuthContext', () => ({ useAuth: () => ({ login }) }));

beforeEach(() => {
  login.mockReset();
});

async function completar(usuario = userEvent.setup()) {
  await usuario.type(screen.getByLabelText('Correo electrónico'), 'ana@eco.pe');
  await usuario.type(screen.getByLabelText('Contraseña'), 'Clave2026!');
  await usuario.click(screen.getByRole('button', { name: 'Ingresar' }));
}

describe('LoginPage', () => {
  it('muestra el formulario de inicio de sesión', () => {
    render(<LoginPage />);
    expect(screen.getByRole('heading', { name: 'Iniciar Sesión' })).toBeInTheDocument();
    expect(screen.getByLabelText('Correo electrónico')).toBeRequired();
    expect(screen.getByLabelText('Contraseña')).toHaveAttribute('type', 'password');
  });

  it('envía las credenciales ingresadas', async () => {
    login.mockResolvedValue(undefined);
    render(<LoginPage />);
    await completar();
    expect(login).toHaveBeenCalledWith('ana@eco.pe', 'Clave2026!');
  });

  it('muestra el detalle cuando el servidor rechaza el acceso (EN-002)', async () => {
    login.mockImplementation(async () => { throw new ApiError(401, 'Credenciales inválidas. Intentos restantes: 2'); });
    render(<LoginPage />);
    await completar();
    expect(await screen.findByText(/Intentos restantes: 2/)).toBeInTheDocument();
  });

  it('muestra un mensaje genérico ante errores de red', async () => {
    login.mockImplementation(async () => { throw new Error('network'); });
    render(<LoginPage />);
    await completar();
    expect(await screen.findByText('Error de conexión con el servidor')).toBeInTheDocument();
  });
});
