import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Modal from '../components/Modal';

describe('Modal accesible (RNF-007)', () => {
  it('es un diálogo con nombre y envía el foco al primer campo', () => {
    render(<Modal titulo="Nuevo registro" onCerrar={vi.fn()}><div className="modal-body"><input aria-label="Campo" /></div></Modal>);
    expect(screen.getByRole('dialog', { name: 'Nuevo registro' })).toHaveAttribute('aria-modal', 'true');
    expect(screen.getByLabelText('Campo')).toHaveFocus();
  });

  it('atrapa el foco: Tab desde el último elemento vuelve al primero y Shift+Tab al revés', async () => {
    const user = userEvent.setup();
    render(
      <Modal titulo="Trampa" onCerrar={vi.fn()} pie={<button>Aceptar</button>}>
        <div className="modal-body"><input aria-label="Uno" /><input aria-label="Dos" /></div>
      </Modal>,
    );
    const cerrar = screen.getByRole('button', { name: 'Cerrar ventana' });
    const aceptar = screen.getByRole('button', { name: 'Aceptar' });
    aceptar.focus();
    await user.tab();
    expect(cerrar).toHaveFocus(); // del último vuelve al primero (el botón de cerrar)
    await user.tab({ shift: true });
    expect(aceptar).toHaveFocus(); // del primero va al último
  });

  it('se cierra con Escape y devuelve el foco al elemento que lo abrió', async () => {
    const user = userEvent.setup();
    const onCerrar = vi.fn();
    const { rerender } = render(<button>Abrir</button>);
    const abrir = screen.getByRole('button', { name: 'Abrir' });
    abrir.focus();
    rerender(<><button>Abrir</button><Modal titulo="Cerrable" onCerrar={onCerrar}><input aria-label="Dato" /></Modal></>);
    await user.keyboard('{Escape}');
    expect(onCerrar).toHaveBeenCalledTimes(1);
    rerender(<button>Abrir</button>);
    expect(screen.getByRole('button', { name: 'Abrir' })).toHaveFocus();
  });

  it('un clic fuera del cuadro lo cierra y un clic dentro no', async () => {
    const user = userEvent.setup();
    const onCerrar = vi.fn();
    render(<Modal titulo="Fuera" onCerrar={onCerrar}><p>Contenido</p></Modal>);
    await user.click(screen.getByText('Contenido'));
    expect(onCerrar).not.toHaveBeenCalled();
    await user.click(screen.getByRole('presentation'));
    expect(onCerrar).toHaveBeenCalledTimes(1);
  });
});
