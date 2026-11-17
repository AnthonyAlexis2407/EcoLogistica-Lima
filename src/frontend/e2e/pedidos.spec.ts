/**
 * Pedidos (US-003): registro con ventana horaria, rechazo por capacidad, cancelación y validación.
 * Usa la sesión del operador logístico (rol con permiso de alta y cancelación).
 */
import { expect, test } from '@playwright/test';
import { archivoSesion, sufijo } from './datos';

test.use({ storageState: archivoSesion('operador') });

async function abrirFormularioDeAlta(page: import('@playwright/test').Page) {
  await page.goto('/pedidos');
  await page.getByRole('button', { name: /Registrar Pedido/ }).click();
  return page.getByRole('dialog');
}

test.describe('Pedidos (US-003)', () => {
  test('ruta feliz: registra un pedido y queda en estado PENDIENTE', async ({ page }) => {
    const direccion = `Jr. E2E ${sufijo(6)} 123, Lima`;
    const dialogo = await abrirFormularioDeAlta(page);

    await dialogo.getByLabel('Dirección de Entrega *').fill(direccion);
    await dialogo.getByLabel('Peso del Paquete (kg) *').fill('120');
    await dialogo.getByRole('button', { name: 'Registrar Pedido' }).click();

    await expect(page.getByText('Pedido registrado exitosamente')).toBeVisible();
    await page.getByPlaceholder('Buscar por dirección...').fill(direccion);
    const fila = page.getByRole('row', { name: new RegExp(direccion.slice(0, 14)) });
    await expect(fila).toBeVisible();
    await expect(fila).toContainText('PENDIENTE');
  });

  test('ruta infeliz: un peso mayor que la capacidad de la flota se rechaza con un mensaje claro', async ({ page }) => {
    const dialogo = await abrirFormularioDeAlta(page);
    await dialogo.getByLabel('Dirección de Entrega *').fill(`Av. Pesada ${sufijo(5)}`);
    await dialogo.getByLabel('Peso del Paquete (kg) *').fill('999999');
    await dialogo.getByRole('button', { name: 'Registrar Pedido' }).click();

    await expect(dialogo.getByText(/excede la capacidad máxima/)).toBeVisible();
    await expect(dialogo).toBeVisible(); // el formulario sigue abierto para corregir
  });

  test('validación: el peso debe ser mayor que cero', async ({ page }) => {
    let altas = 0;
    page.on('request', (r) => { if (r.method() === 'POST' && r.url().includes('/api/pedidos')) altas++; });
    const dialogo = await abrirFormularioDeAlta(page);

    await dialogo.getByLabel('Peso del Paquete (kg) *').fill('0');
    await dialogo.getByRole('button', { name: 'Registrar Pedido' }).click();

    expect(await dialogo.getByLabel('Peso del Paquete (kg) *').evaluate((el: HTMLInputElement) => !el.validity.valid)).toBe(true);
    expect(altas).toBe(0);
  });

  test('usabilidad (mejora SUS): el formulario explica el formato de las coordenadas y lo asocia a los campos', async ({ page }) => {
    const dialogo = await abrirFormularioDeAlta(page);
    await expect(dialogo.getByText(/grados decimales/)).toBeVisible();
    await expect(dialogo.getByLabel('Latitud *')).toHaveAccessibleDescription(/grados decimales/);
    await expect(dialogo.getByLabel('Longitud *')).toHaveAccessibleDescription(/grados decimales/);
  });

  test('cancela un pedido solo tras confirmar y ya no ofrece cancelarlo otra vez', async ({ page }) => {
    const direccion = `Calle Cancelar ${sufijo(6)}`;
    const dialogo = await abrirFormularioDeAlta(page);
    await dialogo.getByLabel('Dirección de Entrega *').fill(direccion);
    await dialogo.getByLabel('Peso del Paquete (kg) *').fill('50');
    await dialogo.getByRole('button', { name: 'Registrar Pedido' }).click();
    await expect(page.getByText('Pedido registrado exitosamente')).toBeVisible();

    await page.getByPlaceholder('Buscar por dirección...').fill(direccion);
    const fila = page.getByRole('row', { name: new RegExp(direccion) });

    page.once('dialog', (d) => d.dismiss());
    await fila.getByRole('button', { name: 'Cancelar' }).click();
    await expect(fila).toContainText('PENDIENTE');

    page.once('dialog', (d) => d.accept());
    await fila.getByRole('button', { name: 'Cancelar' }).click();
    await expect(page.getByText('Pedido cancelado')).toBeVisible();
    await expect(fila).toContainText('CANCELADO');
    await expect(fila.getByRole('button', { name: 'Cancelar' })).toHaveCount(0);
  });

  test('el filtro por estado pide al servidor solo los pedidos de ese estado', async ({ page }) => {
    await page.goto('/pedidos');
    const respuesta = page.waitForResponse((r) => r.url().includes('/api/pedidos/') && r.url().includes('estado=CANCELADO'));
    await page.getByLabel('Filtrar por estado').selectOption('CANCELADO');
    expect((await respuesta).status()).toBe(200);
    for (const estado of await page.locator('tbody .badge').allTextContents()) expect(estado).toBe('CANCELADO');
  });
});
