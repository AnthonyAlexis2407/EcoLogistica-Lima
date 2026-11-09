import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Paginador from '../components/Paginador';

describe('Paginador', () => {
  it('no se muestra cuando todo cabe en una página', () => {
    const { container } = render(<Paginador page={1} total={12} pageSize={12} onChange={vi.fn()} />);
    expect(container).toBeEmptyDOMElement();
  });

  it('indica la página y avanza o retrocede', async () => {
    const usuario = userEvent.setup();
    const alCambiar = vi.fn();
    render(<Paginador page={2} total={30} pageSize={12} onChange={alCambiar} />);
    expect(screen.getByText('Página 2 de 3 · 30 registros')).toBeInTheDocument();

    await usuario.click(screen.getByRole('button', { name: 'Anterior' }));
    await usuario.click(screen.getByRole('button', { name: 'Siguiente' }));
    expect(alCambiar).toHaveBeenNthCalledWith(1, 1);
    expect(alCambiar).toHaveBeenNthCalledWith(2, 3);
  });

  it('deshabilita Siguiente en la última página', () => {
    render(<Paginador page={3} total={30} pageSize={12} onChange={vi.fn()} />);
    expect(screen.getByRole('button', { name: 'Siguiente' })).toBeDisabled();
  });
});
