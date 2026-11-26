/**
 * Administración (RF-008, RN-003, RN-008), permisos por rol en la interfaz y reportes sin datos personales para el auditor.
 */
import { expect, test } from '@playwright/test';
import { archivoSesion, autorizacion, sufijo } from './datos';

test.describe('Administrador', () => {
  test.use({ storageState: archivoSesion('admin') });

  test('registra un conductor y lo ve en la lista', async ({ page }) => {
    const marca = sufijo(6);
    await page.goto('/administracion');
    await page.getByRole('tab', { name: 'Conductores' }).click();
    await page.getByLabel('Nombre del conductor').fill(`Conductor ${marca}`);
    await page.getByLabel('Correo del conductor').fill(`chofer.${marca.toLowerCase()}@prueba.pe`);
    await page.getByLabel('Contraseña del conductor').fill('ClavePrueba2026!');
    await page.getByLabel('Licencia').fill(`Q${marca}9`);
    await page.getByRole('button', { name: 'Registrar conductor' }).click();
    await expect(page.getByText(/Conductor registrado/)).toBeVisible();
    await expect(page.getByRole('cell', { name: `Conductor ${marca}`, exact: true })).toBeVisible();
  });

  test('guarda los parámetros del algoritmo y los vuelve a leer', async ({ page, request }) => {
    await page.goto('/administracion');
    await page.getByRole('tab', { name: 'Parámetros del algoritmo' }).click();
    const velocidad = page.getByLabel('Velocidad media (km/h)');
    await velocidad.fill('27');
    await page.getByRole('button', { name: 'Guardar parámetros' }).click();
    await expect(page.getByText(/Parámetros guardados/)).toBeVisible();
    const guardados = await (await request.get('/api/admin/parametros', { headers: await autorizacion(request, 'admin') })).json();
    expect(guardados.velocidad_kmh).toBe(27);
    await velocidad.fill('25');
    await page.getByRole('button', { name: 'Guardar parámetros' }).click();
    await expect(page.getByText(/Parámetros guardados/)).toBeVisible();
  });

  test('registra y elimina una zona protegida', async ({ page }) => {
    const nombre = `Zona ${sufijo(6)}`;
    await page.goto('/administracion');
    await page.getByRole('tab', { name: 'Zonas protegidas' }).click();
    await page.getByLabel('Nombre de la zona').fill(nombre);
    await page.getByLabel('Latitud de la zona').fill('-11.9');
    await page.getByLabel('Longitud de la zona').fill('-76.9');
    await page.getByRole('button', { name: 'Registrar zona' }).click();
    await expect(page.getByRole('cell', { name: nombre, exact: true })).toBeVisible();
    page.once('dialog', (d) => d.accept());
    await page.getByRole('button', { name: `Eliminar la zona ${nombre}` }).click();
    await expect(page.getByRole('cell', { name: nombre, exact: true })).toHaveCount(0);
  });

  test('no se elimina físicamente la propia cuenta ni se cambia el propio rol', async ({ request }) => {
    const admin = await autorizacion(request, 'admin');
    const yo = await (await request.get('/api/auth/me', { headers: admin })).json();
    expect((await request.delete(`/api/admin/usuarios/${yo.usuario_id}?confirmar=true`, { headers: admin })).status()).toBe(409);
    expect((await request.put(`/api/admin/usuarios/${yo.usuario_id}`, { headers: admin, data: { rol: 'AUDITOR' } })).status()).toBe(409);
    expect((await request.delete(`/api/admin/usuarios/${yo.usuario_id}`, { headers: admin })).status()).toBe(400);
  });
});

test.describe('Operador y bodega: permisos en la interfaz', () => {
  test.describe('Operador', () => {
    test.use({ storageState: archivoSesion('operador') });
    test('no ve la administración y su acceso directo lo devuelve al inicio', async ({ page }) => {
      await page.goto('/');
      await expect(page.getByRole('link', { name: /Administración/ })).toHaveCount(0);
      await page.goto('/administracion');
      await expect(page.getByRole('heading', { name: 'Dashboard', level: 2 })).toBeVisible();
    });
  });

  test.describe('Bodega', () => {
    test.use({ storageState: archivoSesion('bodega') });
    test('ve pedidos y notificaciones, no rutas ni flota', async ({ page }) => {
      await page.goto('/');
      await expect(page.getByRole('heading', { name: 'Gestión de Pedidos', level: 2 })).toBeVisible();
      await expect(page.getByRole('link', { name: /Notificaciones/ })).toBeVisible();
      await expect(page.getByRole('link', { name: /^Rutas/ })).toHaveCount(0);
      await expect(page.getByRole('link', { name: /Vehículos/ })).toHaveCount(0);
    });

    test('puede pedir la eliminación de sus datos personales (5 días hábiles)', async ({ page }) => {
      await page.goto('/notificaciones');
      page.once('dialog', (d) => d.accept());
      await page.locator('#btn-solicitar-baja').click();
      await expect(page.getByText(/Solicitud registrada/)).toBeVisible();
    });
  });
});

test.describe('Auditor (solo lectura, sin datos personales)', () => {
  test.use({ storageState: archivoSesion('auditor') });

  test('ve el dashboard y los filtros pero no la gestión de flota ni de pedidos', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('group', { name: 'Filtros del dashboard' })).toBeVisible();
    await expect(page.getByRole('link', { name: /Vehículos/ })).toHaveCount(0);
    await expect(page.getByRole('link', { name: /Administración/ })).toHaveCount(0);
  });

  test('los reportes del auditor no incluyen direcciones ni coordenadas', async ({ request }) => {
    const auditor = await autorizacion(request, 'auditor');
    for (const reporte of ['pedidos', 'rutas']) {
      const csv = await (await request.get(`/api/reportes/${reporte}.csv`, { headers: auditor })).text();
      const encabezado = csv.replace('﻿', '').split('\r\n')[0];
      expect(encabezado).not.toMatch(/direccion|latitud|longitud/);
      expect(encabezado).toContain('distrito');
    }
    const admin = await autorizacion(request, 'admin');
    const completo = (await (await request.get('/api/reportes/pedidos.csv', { headers: admin })).text()).split('\r\n')[0];
    expect(completo).toContain('direccion');
  });

  test('los reportes se descargan en Excel y PDF', async ({ request }) => {
    const auditor = await autorizacion(request, 'auditor');
    const xlsx = await request.get('/api/reportes/ambiental.xlsx', { headers: auditor });
    expect(xlsx.status()).toBe(200);
    expect((await xlsx.body()).subarray(0, 2).toString()).toBe('PK'); // un .xlsx es un ZIP
    const pdf = await request.get('/api/reportes/ambiental.pdf', { headers: auditor });
    expect((await pdf.body()).subarray(0, 5).toString()).toBe('%PDF-');
  });

  test('la API le niega cualquier escritura', async ({ request }) => {
    const auditor = await autorizacion(request, 'auditor');
    expect((await request.post('/api/rutas/optimizar', { headers: auditor })).status()).toBe(403);
    expect((await request.post('/api/vehiculos/', { headers: auditor, data: { placa: 'AUD-001', capacidad_kg: 1, tipo_combustible: 'GLP' } })).status()).toBe(403);
    expect((await request.get('/api/admin/usuarios', { headers: auditor })).status()).toBe(403);
  });
});

test.describe('Cabeceras y salud', () => {
  test('la salud lista la base de datos y la respuesta lleva HSTS y política de permisos', async ({ request }) => {
    const listo = await request.get('/api/health/ready');
    expect(listo.status()).toBe(200);
    expect((await listo.json()).db).toBe('ok');
    expect(listo.headers()['strict-transport-security']).toContain('max-age=');
    expect(listo.headers()['permissions-policy']).toContain('geolocation=(self)');
  });
});
