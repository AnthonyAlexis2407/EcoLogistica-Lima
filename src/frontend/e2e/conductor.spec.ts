/**
 * App del conductor (RF-004, RF-008, RNF-004, RNF-010): ruta del día, entrega con evidencia en pocos toques, trabajo sin
 * conexión con sincronización posterior y cierre de la ruta con su compensación de carbono (RF-010).
 *
 * Como optimizar toma todos los pedidos pendientes de la base compartida, estas pruebas corren en los proyectos de rutas,
 * en serie y al final (ver playwright.config.ts). Cada una arma su propia ruta por la API y la deja cerrada o cancelada.
 */
import { expect, test, type APIRequestContext, type Page } from '@playwright/test';
import { archivoSesion, autorizacion, sufijo, USUARIOS } from './datos';

test.describe.configure({ mode: 'serial' });
test.setTimeout(120_000);

const AHORA = Date.now();

/** Cancela las rutas abiertas y los pedidos pendientes que dejaron otras pruebas, para planificar solo lo propio. */
async function limpiar(request: APIRequestContext) {
  const operador = await autorizacion(request, 'operador');
  const activas = await (await request.get('/api/rutas/', { headers: operador })).json();
  for (const ruta of activas.rutas) await request.post(`/api/rutas/${ruta.ruta_id}/cancelar`, { headers: operador });
  for (let pagina = 0; pagina < 5; pagina++) {
    const lista = await (await request.get('/api/pedidos/?estado=PENDIENTE&limit=50', { headers: operador })).json();
    if (lista.length === 0) break;
    for (const pedido of lista) await request.delete(`/api/pedidos/${pedido.pedido_id}`, { headers: operador });
  }
}

/** Planifica `cantidad` pedidos y asigna la ruta resultante al conductor de demostración. */
async function prepararRuta(request: APIRequestContext, cantidad = 2) {
  await limpiar(request);
  const operador = await autorizacion(request, 'operador');
  const admin = await autorizacion(request, 'admin');
  const marca = sufijo(4);
  await request.post('/api/vehiculos/', {
    headers: admin, data: { placa: `C${marca}-1`, capacidad_kg: 3000, tipo_combustible: 'GLP', factor_emision_co2: 1.51 },
  });
  for (let i = 0; i < cantidad; i++) {
    const respuesta = await request.post('/api/pedidos/', {
      headers: operador,
      data: {
        direccion: `Jr. Conductor ${marca}-${i} 200, SJL`, latitud: -12.0464 - i * 0.01, longitud: -77.0428 - i * 0.012, peso_kg: 40,
        ventana_inicio: new Date(AHORA).toISOString(), ventana_fin: new Date(AHORA + 10 * 3600 * 1000).toISOString(),
      },
    });
    expect(respuesta.status()).toBe(201);
  }
  const plan = await (await request.post('/api/rutas/optimizar', { headers: operador })).json();
  expect(plan.rutas.length).toBeGreaterThan(0);
  const ruta = plan.rutas[0];
  const conductores = await (await request.get('/api/admin/conductores', { headers: operador })).json();
  const chofer = conductores.find((c: { email: string }) => c.email === USUARIOS.conductor.email);
  const asignada = await request.post(`/api/rutas/${ruta.ruta_id}/conductor`, {
    headers: operador, data: { conductor_id: chofer.conductor_id },
  });
  expect(asignada.status()).toBe(200);
  return ruta as { ruta_id: string; paradas: unknown[] };
}

/** Dibuja la firma con un solo trazo (un gesto). */
async function firmar(page: Page) {
  const caja = await page.getByLabel('Espacio para la firma del receptor').boundingBox();
  if (!caja) throw new Error('No se encontró el lienzo de firma');
  await page.mouse.move(caja.x + 20, caja.y + 30);
  await page.mouse.down();
  await page.mouse.move(caja.x + 120, caja.y + 95, { steps: 6 });
  await page.mouse.move(caja.x + 230, caja.y + 40, { steps: 6 });
  await page.mouse.up();
}

/** Entrega la primera parada pendiente: «Entregar», un trazo de firma y «Confirmar» (3 toques). */
async function entregarPrimera(page: Page) {
  await page.getByRole('button', { name: /^Entregar parada/ }).first().click(); // toque 1
  await firmar(page); // toque 2: un solo gesto
  await page.getByRole('button', { name: /Confirmar/ }).click(); // toque 3
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await expect(page.getByText(/Entrega (registrada|guardada)/)).toBeVisible();
}

test.describe('Conductor', () => {
  test.use({ storageState: archivoSesion('conductor'), permissions: [] });

  test.afterEach(async ({ request }) => {
    await limpiar(request);
  });

  test('ruta feliz: inicia, entrega todas las paradas con firma, termina y se registra la compensación', async ({ page, request }) => {
    await prepararRuta(request, 2);
    await page.goto('/conductor');
    await expect(page.getByRole('heading', { name: 'Mi ruta' })).toBeVisible();
    await expect(page.getByRole('region', { name: 'Mapa de mis paradas' })).toBeVisible();

    await page.getByRole('button', { name: /Iniciar ruta/ }).click();
    await expect(page.getByText(/Ruta iniciada/)).toBeVisible();

    while (await page.getByRole('button', { name: /^Entregar parada/ }).count() > 0) await entregarPrimera(page);
    await expect(page.locator('#pendientes-sync')).toHaveCount(0, { timeout: 20_000 });

    await page.getByRole('button', { name: /Terminar ruta/ }).click();
    await expect(page.getByText(/Ruta completada/)).toBeVisible();

    const admin = await autorizacion(request, 'admin');
    const indicadores = await (await request.get('/api/indicadores/resumen', { headers: admin })).json();
    expect(indicadores.rutas_completadas).toBeGreaterThanOrEqual(1);
    expect(indicadores.arboles_compensados).toBeGreaterThanOrEqual(0);

    // RF-009: la bodega recibió los avisos de asignación, salida y entrega.
    const bodega = await autorizacion(request, 'bodega');
    const avisos = await (await request.get('/api/notificaciones/', { headers: bodega })).json();
    const tipos = new Set(avisos.map((a: { tipo: string }) => a.tipo));
    for (const tipo of ['ASIGNACION', 'EN_RUTA', 'ENTREGA']) expect(tipos.has(tipo), `aviso ${tipo}`).toBe(true);
  });

  test('RNF-004: confirmar una entrega toma 3 toques y menos de 20 segundos', async ({ page, request }) => {
    await prepararRuta(request, 1);
    await page.goto('/conductor');
    await page.getByRole('button', { name: /Iniciar ruta/ }).click();
    await expect(page.getByRole('button', { name: /^Entregar parada/ })).toBeVisible();

    const inicio = Date.now();
    await entregarPrimera(page); // incluye esperar el aviso «Entrega registrada»
    expect(Date.now() - inicio).toBeLessThan(20_000);
  });

  test('RN-007: no se puede confirmar una entrega sin firma ni foto', async ({ page, request }) => {
    await prepararRuta(request, 1);
    await page.goto('/conductor');
    await page.getByRole('button', { name: /Iniciar ruta/ }).click();
    await page.getByRole('button', { name: /^Entregar parada/ }).first().click();
    await expect(page.getByRole('button', { name: /Confirmar/ })).toBeDisabled();
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).toHaveCount(0);
  });

  test('RNF-010: sin conexión la entrega queda en cola y se sincroniza al volver la señal', async ({ page, context, request }) => {
    const ruta = await prepararRuta(request, 2);
    await page.goto('/conductor');
    await page.getByRole('button', { name: /Iniciar ruta/ }).click();
    await expect(page.getByText(/Ruta iniciada/)).toBeVisible();

    await context.setOffline(true);
    await entregarPrimera(page);
    await expect(page.getByText(/Entrega guardada/)).toBeVisible();
    await expect(page.locator('#pendientes-sync')).toContainText('1 acción');

    await context.setOffline(false);
    await expect(page.locator('#pendientes-sync')).toHaveCount(0, { timeout: 45_000 });

    const operador = await autorizacion(request, 'operador');
    const guardada = await (await request.get(`/api/rutas/${ruta.ruta_id}`, { headers: operador })).json();
    expect(guardada.paradas.filter((p: { estado: string }) => p.estado === 'ENTREGADA')).toHaveLength(1);
  });

  test('una parada se reprograma con su motivo y el pedido vuelve a pendiente', async ({ page, request }) => {
    await prepararRuta(request, 2);
    await page.goto('/conductor');
    await page.getByRole('button', { name: /Iniciar ruta/ }).click();
    await page.getByRole('button', { name: /^No pude entregar la parada/ }).first().click();
    await page.getByLabel('Motivo').selectOption('Cliente ausente');
    await page.getByRole('button', { name: 'Reprogramar' }).click();
    await expect(page.getByText('Reprogramada', { exact: true })).toBeVisible();
    await expect(page.locator('#pendientes-sync')).toHaveCount(0, { timeout: 20_000 });
  });

  test('la API sincroniza por lotes sin duplicar acciones repetidas (idempotencia)', async ({ request }) => {
    const ruta = await prepararRuta(request, 1);
    const chofer = await autorizacion(request, 'conductor');
    await request.post(`/api/rutas/${ruta.ruta_id}/iniciar`, { headers: chofer });
    const propia = await (await request.get('/api/conductor/ruta', { headers: chofer })).json();
    const accion = {
      tipo: 'ENTREGA', parada_id: propia.paradas[0].parada_id, clave_sync: `e2e-${sufijo(10)}`,
      evidencia_tipo: 'FIRMA', evidencia: 'data:image/png;base64,iVBORw0KGgo=', latitud: -12.05, longitud: -77.04,
    };
    const primera = await (await request.post('/api/conductor/sync', { headers: chofer, data: { acciones: [accion] } })).json();
    const segunda = await (await request.post('/api/conductor/sync', { headers: chofer, data: { acciones: [accion] } })).json();
    expect(primera.aplicadas).toBe(1);
    expect(segunda.duplicadas).toBe(1);
    expect(segunda.aplicadas).toBe(0);
  });
});
