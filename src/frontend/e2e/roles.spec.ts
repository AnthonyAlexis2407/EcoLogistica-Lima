/**
 * Control de acceso por rol (RBAC, Documento 08): lo que cada rol ve en la interfaz y lo que la API le permite.
 * Cada bloque usa una sesión distinta; los contextos de Playwright están aislados entre sí.
 */
import { expect, test } from '@playwright/test';
import { archivoSesion, autorizacion, sufijo } from './datos';

test.describe('Administrador de flota', () => {
  test.use({ storageState: archivoSesion('admin') });

  test('ve el botón para registrar vehículos', async ({ page }) => {
    await page.goto('/vehiculos');
    await expect(page.getByRole('button', { name: /Registrar Vehículo/ })).toBeVisible();
  });
});

test.describe('Operador logístico', () => {
  test.use({ storageState: archivoSesion('operador') });

  test('puede consultar la flota pero la interfaz no le ofrece modificarla', async ({ page }) => {
    await page.goto('/vehiculos');
    await expect(page.getByRole('heading', { name: 'Gestión de Flota Vehicular' })).toBeVisible();
    await expect(page.getByRole('button', { name: /Registrar Vehículo/ })).toHaveCount(0);
    await expect(page.getByTitle('Editar')).toHaveCount(0);
  });

  test('la API rechaza con 403 un alta de vehículo hecha por el operador', async ({ request }) => {
    const respuesta = await request.post('/api/vehiculos/', {
      headers: await autorizacion(request, 'operador'),
      data: { placa: `O${sufijo(5)}`, capacidad_kg: 500, tipo_combustible: 'GLP' },
    });
    expect(respuesta.status()).toBe(403);
  });
});

test.describe('Dueño de bodega (aislamiento RN-010)', () => {
  test.use({ storageState: archivoSesion('bodega') });

  test('solo lista los pedidos de su propia bodega', async ({ request }) => {
    const cabeceras = await autorizacion(request, 'bodega');
    const propios = await (await request.get('/api/pedidos/?limit=50', { headers: cabeceras })).json();
    const todos = await (await request.get('/api/pedidos/?limit=50', { headers: await autorizacion(request, 'admin') })).json();

    expect(propios.length).toBeGreaterThan(0);
    expect(new Set(propios.map((p: { bodega_id: string }) => p.bodega_id)).size).toBe(1);
    expect(todos.length).toBeGreaterThanOrEqual(propios.length);
  });

  test('no puede registrar pedidos a nombre de otra bodega', async ({ request }) => {
    const respuesta = await request.post('/api/pedidos/', {
      headers: await autorizacion(request, 'bodega'),
      data: {
        bodega_id: '00000000-0000-0000-0000-000000000000',
        direccion: 'Av. Ajena 1', latitud: -12.05, longitud: -77.0, peso_kg: 10,
        ventana_inicio: new Date(Date.now() + 3_600_000).toISOString(),
        ventana_fin: new Date(Date.now() + 7_200_000).toISOString(),
      },
    });
    expect(respuesta.status()).toBe(403);
  });

  test('la interfaz no le ofrece ningún acceso a la gestión de flota', async ({ page }) => {
    await page.goto('/vehiculos');
    await expect(page.getByRole('button', { name: /Registrar Vehículo/ })).toHaveCount(0);
  });
});

test.describe('Registro público', () => {
  test('no permite autoasignarse un rol de administración', async ({ request }) => {
    const respuesta = await request.post('/api/auth/register', {
      data: { nombre: 'Intruso', email: `intruso.${sufijo(6).toLowerCase()}@prueba.pe`, password: 'ClavePrueba2026!', rol: 'ADMIN_FLOTA' },
    });
    expect(respuesta.status()).toBe(403);
  });
});
