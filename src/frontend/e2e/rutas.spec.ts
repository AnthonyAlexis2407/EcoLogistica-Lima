/**
 * Rutas optimizadas (RF-003), mapa (RF-004), indicadores y CO₂ (RF-005, RF-010), reportes (RF-006) y SLA de 45 s (RNF-001).
 *
 * Optimizar toma TODOS los pedidos pendientes de la base compartida, por eso estas pruebas corren en proyectos propios
 * (`rutas-chromium`, `rutas-firefox`, `rutas-webkit`), en serie y después de todas las demás (ver playwright.config.ts).
 * Cada prueba deja la base como la encontró: cancela las rutas que creó para devolver sus pedidos a PENDIENTE.
 */
import { mkdirSync, writeFileSync } from 'node:fs';
import { expect, test, type APIRequestContext } from '@playwright/test';
import { archivoSesion, autorizacion, sufijo } from './datos';

test.describe.configure({ mode: 'serial' });

const AHORA = Date.now();

async function crearPedidos(request: APIRequestContext, cantidad: number, peso = 60) {
  const cabeceras = await autorizacion(request, 'operador');
  const marca = sufijo(4);
  for (let i = 0; i < cantidad; i++) {
    const respuesta = await request.post('/api/pedidos/', {
      headers: cabeceras,
      data: {
        direccion: `Av. Ruta ${marca}-${i} 100, Lima`,
        latitud: -12.0464 - ((i * 7) % 20) * 0.004,
        longitud: -77.0428 - ((i * 11) % 20) * 0.004,
        peso_kg: peso,
        ventana_inicio: new Date(AHORA).toISOString(),
        ventana_fin: new Date(AHORA + 8 * 3600 * 1000).toISOString(),
      },
    });
    expect(respuesta.status(), `alta del pedido ${i}`).toBe(201);
  }
}

/** Garantiza vehículos con capacidad suficiente para que la prueba no dependa de lo que dejaron otras. */
async function asegurarFlota(request: APIRequestContext) {
  const admin = await autorizacion(request, 'admin');
  const marca = sufijo(4);
  for (let i = 0; i < 3; i++) {
    await request.post('/api/vehiculos/', { headers: admin, data: { placa: `R${marca}-${i}`, capacidad_kg: 3000, tipo_combustible: 'GLP', factor_emision_co2: 1.51 } });
  }
}

async function cancelarRutas(request: APIRequestContext) {
  const cabeceras = await autorizacion(request, 'operador');
  const activas = await (await request.get('/api/rutas/', { headers: cabeceras })).json();
  for (const ruta of activas.rutas) {
    await request.post(`/api/rutas/${ruta.ruta_id}/cancelar`, { headers: cabeceras });
  }
}

test.beforeEach(async ({ request }) => {
  await cancelarRutas(request);
});

test.afterEach(async ({ request }) => {
  await cancelarRutas(request);
});

test.describe('Planificación de rutas (operador)', () => {
  test.use({ storageState: archivoSesion('operador') });

  test('ruta feliz: el operador optimiza y ve rutas, mapa, CO₂ evitado y tiempo de cálculo', async ({ page, request }) => {
    await crearPedidos(request, 5);
    await page.goto('/rutas');
    await expect(page.getByRole('heading', { name: 'Rutas Optimizadas' })).toBeVisible();
    await expect(page.getByRole('region', { name: 'Mapa de rutas' })).toBeVisible();

    await page.getByRole('button', { name: /Optimizar rutas/ }).click();

    await expect(page.getByText(/pedidos planificados en \d+ rutas/)).toBeVisible();
    await expect(page.getByText('CO₂ evitado', { exact: true })).toBeVisible();
    await expect(page.getByText(/SLA: 45 000 ms/)).toBeVisible();
    await expect(page.getByText(/^Vehículo /).first()).toBeVisible();
    await expect(page.getByRole('table').first().getByRole('row').nth(1)).toBeVisible();
    // Leaflet monta su contenedor y dibuja el recorrido (aunque las teselas del mapa no carguen sin internet).
    await expect(page.locator('.leaflet-container')).toBeVisible();
    await expect(page.locator('.parada-marcador').first()).toBeVisible();
  });

  test('cancelar una ruta pide confirmación y devuelve sus pedidos a PENDIENTE', async ({ page, request }) => {
    await crearPedidos(request, 3);
    await page.goto('/rutas');
    await page.getByRole('button', { name: /Optimizar rutas/ }).click();
    await expect(page.getByText(/pedidos planificados en/)).toBeVisible();

    page.once('dialog', (d) => d.dismiss());
    await page.getByRole('button', { name: /Cancelar la ruta/ }).first().click();
    await expect(page.getByText(/^Vehículo /).first()).toBeVisible(); // al rechazar la confirmación, la ruta sigue

    const antes = await page.getByRole('button', { name: /Cancelar la ruta/ }).count();
    page.once('dialog', (d) => d.accept());
    await page.getByRole('button', { name: /Cancelar la ruta/ }).first().click();
    await expect(page.getByText(/cancelada/)).toBeVisible();
    await expect(page.getByRole('button', { name: /Cancelar la ruta/ })).toHaveCount(antes - 1);
  });

  test('sin pedidos pendientes el servidor lo informa dentro de la pantalla', async ({ page, request }) => {
    // Se asignan todos los pendientes por la API y luego se pide optimizar desde la interfaz.
    await asegurarFlota(request);
    const cabeceras = await autorizacion(request, 'operador');
    await request.post('/api/rutas/optimizar', { headers: cabeceras });

    await page.goto('/rutas');
    await page.getByRole('button', { name: /Optimizar rutas/ }).click();
    await expect(page.getByText(/No hay pedidos pendientes para planificar/)).toBeVisible();
  });

  test('el dashboard muestra los indicadores reales de rutas y de compensación de carbono', async ({ page, request }) => {
    await crearPedidos(request, 4);
    await page.goto('/rutas');
    await page.getByRole('button', { name: /Optimizar rutas/ }).click();
    await expect(page.getByText(/pedidos planificados en/)).toBeVisible();

    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Rutas y compensación de carbono' })).toBeVisible();
    await expect(page.getByText('CO₂ evitado (acumulado)')).toBeVisible();
    await expect(page.getByText(/árboles$/).first()).toBeVisible();
  });
});

test.describe('API de rutas, indicadores y reportes', () => {
  test('sin sesión responde 401 y la bodega, 403', async ({ request }) => {
    const bodega = await autorizacion(request, 'bodega');
    for (const ruta of ['/api/rutas/', '/api/indicadores/resumen', '/api/reportes/pedidos.csv']) {
      expect((await request.get(ruta)).status(), `${ruta} sin sesión`).toBe(401);
      expect((await request.get(ruta, { headers: bodega })).status(), `${ruta} con rol BODEGA`).toBe(403);
    }
    expect((await request.post('/api/rutas/optimizar', { headers: bodega })).status()).toBe(403);
  });

  test('los reportes CSV se descargan con codificación UTF-8 y encabezados', async ({ request }) => {
    const admin = await autorizacion(request, 'admin');
    for (const [reporte, encabezado] of [
      ['pedidos', 'pedido_id,direccion,latitud'],
      ['rutas', 'ruta_id,placa,combustible'],
      ['ambiental', 'optimizacion_id,fecha,algoritmo'],
    ]) {
      const respuesta = await request.get(`/api/reportes/${reporte}.csv`, { headers: admin });
      expect(respuesta.status()).toBe(200);
      expect(respuesta.headers()['content-type']).toContain('text/csv');
      expect(respuesta.headers()['content-disposition']).toContain(`${reporte}.csv`);
      const cuerpo = await respuesta.text();
      expect(cuerpo.replace('﻿', '').startsWith(encabezado)).toBe(true);
    }
  });

  test('RNF-001: 50 pedidos se planifican en menos de 45 s y se midió el CO₂ evitado', async ({ request }, testInfo) => {
    // Las ventanas horarias son restricciones duras (8 h): 50 paradas de 10 min no caben en un solo vehículo, por lo que
    // la prueba garantiza una flota suficiente (varios vehículos con capacidad amplia).
    for (let k = 0; k < 4; k++) await asegurarFlota(request);
    await crearPedidos(request, 50, 40);
    const cabeceras = await autorizacion(request, 'operador');

    const inicio = performance.now();
    const respuesta = await request.post('/api/rutas/optimizar', { headers: cabeceras, data: { limite_segundos: 40 } });
    const transcurridoMs = performance.now() - inicio;
    expect(respuesta.status()).toBe(201);
    const plan = await respuesta.json();

    const resultado = {
      navegador: testInfo.project.name,
      pedidos: plan.pedidos_planificados + plan.pedidos_sin_asignar,
      rutas: plan.rutas.length,
      sinAsignar: plan.pedidos_sin_asignar,
      tiempoCalculoMs: plan.tiempo_ms,
      tiempoRespuestaMs: Math.round(transcurridoMs),
      ahorroKmPct: plan.ahorro_km_pct,
      ahorroCo2Pct: plan.ahorro_co2_pct,
      co2EvitadoKg: plan.co2_evitado_kg,
      limiteSegundos: 45,
    };
    mkdirSync('test-results/metricas', { recursive: true });
    writeFileSync(`test-results/metricas/${testInfo.project.name}-optimizacion.json`, JSON.stringify(resultado, null, 2));
    await testInfo.attach('optimizacion.json', { body: JSON.stringify(resultado, null, 2), contentType: 'application/json' });

    expect(transcurridoMs).toBeLessThan(45_000);
    expect(plan.pedidos_planificados).toBeGreaterThanOrEqual(50);
    expect(plan.ahorro_km_pct).toBeGreaterThan(0);
    expect(plan.co2_evitado_kg).toBeGreaterThanOrEqual(0);
    expect(plan.limite_alcanzado).toBe(false);
  });
});
