/**
 * Disponibilidad y resiliencia: códigos de estado HTTP, cabeceras de seguridad, sondeo de uptime y
 * comportamiento de la interfaz cuando la red o la API fallan (simulado con la intercepción de red de Playwright).
 *
 * Con `E2E_BASE_URL` apuntando al entorno desplegado, estas pruebas sirven como monitoreo sintético.
 */
import { mkdirSync, writeFileSync } from 'node:fs';
import { expect, test } from '@playwright/test';
import { archivoSesion, autorizacion } from './datos';

test.describe('Códigos de estado HTTP', () => {
  test('la página principal y la API de salud responden 200', async ({ request }) => {
    const inicio = await request.get('/');
    expect(inicio.status()).toBe(200);
    expect(inicio.headers()['content-type']).toContain('text/html');

    const salud = await request.get('/api/health');
    expect(salud.status()).toBe(200);
    expect(await salud.json()).toMatchObject({ status: 'ok' });
  });

  test('una ruta de la interfaz que no existe entrega la aplicación (200) y una de la API responde 404 en JSON', async ({ request }) => {
    expect((await request.get('/ruta-que-no-existe')).status()).toBe(200);
    const api = await request.get('/api/no-existe');
    expect(api.status()).toBe(404);
    expect(await api.json()).toHaveProperty('detail');
  });

  test('los datos exigen sesión: 401 sin token y con token inválido', async ({ request }) => {
    expect((await request.get('/api/vehiculos/')).status()).toBe(401);
    const invalido = await request.get('/api/vehiculos/', { headers: { Authorization: 'Bearer token-falso' } });
    expect(invalido.status()).toBe(401);
  });

  test('un cuerpo inválido se rechaza con 422 y no con un error del servidor', async ({ request }) => {
    const respuesta = await request.post('/api/vehiculos/', {
      headers: await autorizacion(request, 'admin'),
      data: { placa: '', capacidad_kg: -5, tipo_combustible: 'AGUA' },
    });
    expect(respuesta.status()).toBe(422);
  });

  test('las respuestas llevan las cabeceras de seguridad', async ({ request }) => {
    const cabeceras = (await request.get('/api/health')).headers();
    expect(cabeceras['x-content-type-options']).toBe('nosniff');
    expect(cabeceras['x-frame-options']).toBe('DENY');
    expect(cabeceras['referrer-policy']).toBe('no-referrer');
  });

  test('en producción la documentación interactiva de la API está oculta', async ({ request }) => {
    test.skip(process.env.E2E_DOCS_VISIBLES === '1', 'Entorno de desarrollo: /docs está habilitado a propósito.');
    // Las rutas desconocidas entregan la interfaz (200), así que se comprueba que NO sea Swagger ni el esquema OpenAPI.
    const docs = await request.get('/docs');
    expect(await docs.text()).not.toContain('swagger-ui');
    const esquema = await request.get('/openapi.json');
    expect(esquema.headers()['content-type'] ?? '').not.toContain('application/json');
  });
});

test.describe('Uptime', () => {
  test('30 sondeos seguidos a /api/health: 100 % de disponibilidad', async ({ request }, testInfo) => {
    const SONDEOS = 30;
    const tiempos: number[] = [];
    let correctos = 0;
    for (let i = 0; i < SONDEOS; i++) {
      const inicio = performance.now();
      const respuesta = await request.get('/api/health');
      tiempos.push(performance.now() - inicio);
      if (respuesta.status() === 200) correctos++;
      await new Promise((resolver) => setTimeout(resolver, 150));
    }
    const ordenados = [...tiempos].sort((a, b) => a - b);
    const resultado = {
      navegador: testInfo.project.name,
      sondeos: SONDEOS,
      correctos,
      disponibilidadPorcentaje: (correctos / SONDEOS) * 100,
      latenciaMedianaMs: Math.round(ordenados[Math.floor(SONDEOS / 2)] * 10) / 10,
      latenciaMaximaMs: Math.round(ordenados[SONDEOS - 1] * 10) / 10,
    };
    mkdirSync('test-results/metricas', { recursive: true });
    writeFileSync(`test-results/metricas/${testInfo.project.name}-uptime.json`, JSON.stringify(resultado, null, 2));
    await testInfo.attach('uptime.json', { body: JSON.stringify(resultado, null, 2), contentType: 'application/json' });

    expect(correctos).toBe(SONDEOS);
  });
});

test.describe('Resiliencia ante fallas de red', () => {
  test.use({ storageState: archivoSesion('admin') });

  test('si la API de vehículos no responde, la pantalla no se rompe y muestra el estado vacío', async ({ page }) => {
    const errores: string[] = [];
    page.on('pageerror', (e) => errores.push(e.message));
    await page.route('**/api/vehiculos/**', (ruta) => ruta.abort('failed'));

    await page.goto('/vehiculos');
    await expect(page.getByRole('heading', { name: 'Gestión de Flota Vehicular' })).toBeVisible();
    await expect(page.getByText('Sin vehículos que coincidan')).toBeVisible();
    expect(errores).toEqual([]);
  });

  test('un error 500 del servidor se maneja sin errores no controlados', async ({ page }) => {
    const errores: string[] = [];
    page.on('pageerror', (e) => errores.push(e.message));
    await page.route('**/api/pedidos/**', (ruta) =>
      ruta.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Error interno simulado' }) }));

    await page.goto('/pedidos');
    await expect(page.getByRole('heading', { name: 'Gestión de Pedidos' })).toBeVisible();
    await expect(page.getByText('Sin pedidos registrados')).toBeVisible();
    expect(errores).toEqual([]);
  });

  test('una API lenta muestra el indicador de carga y luego los datos', async ({ page }) => {
    await page.route('**/api/vehiculos/?**', async (ruta) => {
      await new Promise((resolver) => setTimeout(resolver, 1500));
      await ruta.continue();
    });

    await page.goto('/vehiculos');
    await expect(page.getByText('Cargando catálogo de flota...')).toBeVisible();
    await expect(page.getByRole('table')).toBeVisible({ timeout: 10_000 });
  });

  test('con la API de salud caída, la barra superior lo informa', async ({ page }) => {
    await page.route('**/api/health', (ruta) => ruta.abort('failed'));
    await page.goto('/');
    await expect(page.getByText('API sin conexión')).toBeVisible();
  });

  test('con la API de salud activa, la barra superior muestra "API conectada"', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('API conectada')).toBeVisible();
  });
});
