/**
 * Gestión de flota (US-001): alta, placa duplicada, búsqueda, edición, baja lógica y paginación de 12.
 * Todas las pruebas usan la sesión del administrador y placas únicas por ejecución.
 */
import { expect, test } from '@playwright/test';
import { archivoSesion, autorizacion, crearVehiculos, sufijo } from './datos';

test.use({ storageState: archivoSesion('admin') });

async function abrirFormularioDeAlta(page: import('@playwright/test').Page) {
  await page.goto('/vehiculos');
  await page.getByRole('button', { name: /Registrar Vehículo/ }).click();
  return page.getByRole('dialog');
}

test.describe('Vehículos (US-001)', () => {
  test('ruta feliz: registra un vehículo y aparece en la tabla', async ({ page }) => {
    const placa = `E${sufijo(5)}`;
    const dialogo = await abrirFormularioDeAlta(page);

    await dialogo.getByLabel('Placa del Vehículo *').fill(placa);
    await dialogo.getByLabel('Capacidad de Carga (kg) *').fill('1800');
    await dialogo.getByLabel('Tipo de Combustible *').selectOption('ELECTRICO');
    await dialogo.getByRole('button', { name: 'Registrar Vehículo' }).click();

    await expect(page.getByText(`Vehículo ${placa} registrado en la flota`)).toBeVisible();
    await page.getByPlaceholder('Buscar por placa...').fill(placa);
    const fila = page.getByRole('row', { name: new RegExp(placa) });
    await expect(fila).toBeVisible();
    await expect(fila).toContainText('ELECTRICO');
    await expect(fila).toContainText('DISPONIBLE');
  });

  test('ruta infeliz: una placa duplicada se rechaza dentro del formulario', async ({ page }) => {
    const placa = `D${sufijo(5)}`;
    let dialogo = await abrirFormularioDeAlta(page);
    await dialogo.getByLabel('Placa del Vehículo *').fill(placa);
    await dialogo.getByLabel('Capacidad de Carga (kg) *').fill('900');
    await dialogo.getByRole('button', { name: 'Registrar Vehículo' }).click();
    await expect(page.getByText(`Vehículo ${placa} registrado en la flota`)).toBeVisible();

    await page.getByRole('button', { name: /Registrar Vehículo/ }).first().click();
    dialogo = page.getByRole('dialog');
    await dialogo.getByLabel('Placa del Vehículo *').fill(placa);
    await dialogo.getByLabel('Capacidad de Carga (kg) *').fill('900');
    await dialogo.getByRole('button', { name: 'Registrar Vehículo' }).click();

    await expect(dialogo.getByText(/Registro rechazado por duplicidad/)).toBeVisible();
  });

  test('validación: no se registra un vehículo con capacidad vacía', async ({ page }) => {
    let altas = 0;
    page.on('request', (r) => { if (r.method() === 'POST' && r.url().includes('/api/vehiculos')) altas++; });
    const dialogo = await abrirFormularioDeAlta(page);

    await dialogo.getByLabel('Placa del Vehículo *').fill(`V${sufijo(5)}`);
    await dialogo.getByLabel('Capacidad de Carga (kg) *').fill('');
    await dialogo.getByRole('button', { name: 'Registrar Vehículo' }).click();

    expect(await dialogo.getByLabel('Capacidad de Carga (kg) *').evaluate((el: HTMLInputElement) => el.validity.valueMissing)).toBe(true);
    expect(altas).toBe(0);
  });

  test('edita la capacidad de un vehículo existente', async ({ page, request }) => {
    const prefijo = `U${sufijo(3)}`;
    await crearVehiculos(request, await autorizacion(request, 'admin'), prefijo, 1);
    await page.goto('/vehiculos');
    await page.getByPlaceholder('Buscar por placa...').fill(prefijo);

    const fila = page.getByRole('row', { name: new RegExp(prefijo) });
    await fila.getByTitle('Editar').click();
    const dialogo = page.getByRole('dialog');
    await dialogo.getByLabel('Capacidad de Carga (kg) *').fill('2750');
    await dialogo.getByRole('button', { name: 'Guardar Cambios' }).click();

    await expect(page.getByText(/actualizado exitosamente/)).toBeVisible();
    await expect(fila).toContainText(/2[.,]750/);
  });

  test('da de baja un vehículo solo después de confirmar y conserva el registro', async ({ page, request }) => {
    const prefijo = `B${sufijo(3)}`;
    await crearVehiculos(request, await autorizacion(request, 'admin'), prefijo, 1);
    await page.goto('/vehiculos');
    await page.getByPlaceholder('Buscar por placa...').fill(prefijo);
    const fila = page.getByRole('row', { name: new RegExp(prefijo) });

    // Primero se cancela la confirmación: no cambia nada.
    page.once('dialog', (d) => d.dismiss());
    await fila.getByTitle('Dar de baja').click();
    await expect(fila).toContainText('DISPONIBLE');

    page.once('dialog', (d) => d.accept());
    await fila.getByTitle('Dar de baja').click();
    await expect(page.getByText(/dado de baja/)).toBeVisible();
    await expect(fila).toContainText('FUERA_DE_SERVICIO');
  });

  test('la búsqueda se hace en el servidor y el filtro por estado combina con ella', async ({ page, request }) => {
    const prefijo = `S${sufijo(3)}`;
    await crearVehiculos(request, await autorizacion(request, 'admin'), prefijo, 3);
    await page.goto('/vehiculos');

    await page.getByPlaceholder('Buscar por placa...').fill(prefijo);
    await expect(page.getByRole('row', { name: new RegExp(prefijo) })).toHaveCount(3);

    await page.getByLabel('Filtrar por estado').selectOption('EN_MANTENIMIENTO');
    await expect(page.getByText('Sin vehículos que coincidan')).toBeVisible();
  });

  test('paginación: 13 vehículos se muestran de 12 en 12 con el total informado', async ({ page, request }) => {
    const prefijo = `P${sufijo(4)}`;
    await crearVehiculos(request, await autorizacion(request, 'admin'), prefijo, 13);
    await page.goto('/vehiculos');
    await page.getByPlaceholder('Buscar por placa...').fill(prefijo);

    await expect(page.getByText('Página 1 de 2 · 13 registros')).toBeVisible();
    await expect(page.getByRole('row', { name: new RegExp(prefijo) })).toHaveCount(12);
    await expect(page.getByRole('button', { name: 'Anterior' })).toBeDisabled();

    await page.getByRole('button', { name: 'Siguiente' }).click();
    await expect(page.getByText('Página 2 de 2 · 13 registros')).toBeVisible();
    await expect(page.getByRole('row', { name: new RegExp(prefijo) })).toHaveCount(1);
    await expect(page.getByRole('button', { name: 'Siguiente' })).toBeDisabled();
  });
});
