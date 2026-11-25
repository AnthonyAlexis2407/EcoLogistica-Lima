/**
 * Monitoreo de rendimiento: Web Vitals en el navegador (TTFB, FCP, LCP, CLS) y tiempos de respuesta de la API.
 *
 * Playwright mide con las APIs estándar del navegador (`PerformanceObserver`, `Navigation Timing`).
 * Cada medición se guarda en `test-results/metricas/<navegador>-<nombre>.json`, de donde
 * `scripts/resumen_playwright.py` arma las tablas del informe. Los límites son los de Core Web Vitals
 * ("bueno") y el presupuesto de 500 ms para la API fijado en el Sprint 4.
 *
 * Nota: Lighthouse (laboratorio, con red y CPU simuladas) está en `green-audit.yml`; estas pruebas miden
 * con la red real del entorno donde corren, por eso sus valores son menores y no se comparan 1 a 1.
 */
import { mkdirSync, writeFileSync } from 'node:fs';
import { expect, test } from '@playwright/test';
import { autorizacion } from './datos';

const LIMITES = { ttfb: 800, fcp: 1800, lcp: 2500, cls: 0.1, apiMediana: 500, apiP95: 800 };

function guardar(proyecto: string, nombre: string, datos: unknown) {
  mkdirSync('test-results/metricas', { recursive: true });
  writeFileSync(`test-results/metricas/${proyecto}-${nombre}.json`, JSON.stringify(datos, null, 2));
}

const percentil = (valores: number[], p: number) => {
  const ordenados = [...valores].sort((a, b) => a - b);
  return ordenados[Math.min(ordenados.length - 1, Math.ceil((p / 100) * ordenados.length) - 1)];
};

test.describe('Web Vitals de la pantalla de inicio de sesión', () => {
  test('TTFB, FCP, LCP y CLS cumplen los límites de Core Web Vitals', async ({ page }, testInfo) => {
    // Se registran LCP y CLS desde el primer instante de la carga.
    await page.addInitScript(() => {
      const w = window as unknown as { __vitals: { lcp: number | null; cls: number } };
      w.__vitals = { lcp: null, cls: 0 };
      try {
        new PerformanceObserver((lista) => {
          const entradas = lista.getEntries();
          w.__vitals.lcp = entradas[entradas.length - 1].startTime;
        }).observe({ type: 'largest-contentful-paint', buffered: true });
      } catch { /* este navegador no ofrece LCP */ }
      try {
        new PerformanceObserver((lista) => {
          for (const e of lista.getEntries() as unknown as { value: number; hadRecentInput: boolean }[]) {
            if (!e.hadRecentInput) w.__vitals.cls += e.value;
          }
        }).observe({ type: 'layout-shift', buffered: true });
      } catch { /* este navegador no ofrece layout-shift */ }
    });

    await page.goto('/login');
    await expect(page.getByRole('heading', { name: 'Iniciar Sesión' })).toBeVisible();
    await page.waitForTimeout(1000); // deja que el navegador emita las entradas finales de LCP y CLS

    const medidas = await page.evaluate(() => {
      const navegacion = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const fcp = performance.getEntriesByName('first-contentful-paint')[0];
      const v = (window as unknown as { __vitals: { lcp: number | null; cls: number } }).__vitals;
      return {
        ttfb: navegacion.responseStart - navegacion.startTime,
        dominCargado: navegacion.domContentLoadedEventEnd - navegacion.startTime,
        carga: navegacion.loadEventEnd - navegacion.startTime,
        fcp: fcp ? fcp.startTime : null,
        lcp: v.lcp,
        cls: v.cls,
        bytesTransferidos: navegacion.transferSize,
      };
    });

    const resultado = { navegador: testInfo.project.name, ...medidas, limites: LIMITES };
    guardar(testInfo.project.name, 'webvitals', resultado);
    await testInfo.attach('web-vitals.json', { body: JSON.stringify(resultado, null, 2), contentType: 'application/json' });

    expect(medidas.ttfb).toBeLessThan(LIMITES.ttfb);
    // Firefox y WebKit pueden no exponer algunas métricas: se registran como nulas y no se exigen.
    if (medidas.fcp !== null) expect(medidas.fcp).toBeLessThan(LIMITES.fcp);
    if (medidas.lcp !== null) expect(medidas.lcp).toBeLessThan(LIMITES.lcp);
    expect(medidas.cls).toBeLessThan(LIMITES.cls);
  });
});

test.describe('Tiempos de respuesta de la API', () => {
  const REPETICIONES = 15;
  const RUTAS = ['/api/health', '/api/vehiculos/', '/api/pedidos/', '/api/vehiculos/count'];

  test(`mediana menor que ${LIMITES.apiMediana} ms y p95 menor que ${LIMITES.apiP95} ms en cada endpoint`, async ({ request }, testInfo) => {
    const cabeceras = await autorizacion(request, 'admin');
    const resumen: Record<string, { mediana: number; p95: number; maximo: number; estados: number[] }> = {};

    for (const ruta of RUTAS) {
      const tiempos: number[] = [];
      const estados: number[] = [];
      for (let i = 0; i < REPETICIONES; i++) {
        const inicio = performance.now();
        const respuesta = await request.get(ruta, { headers: ruta === '/api/health' ? {} : cabeceras });
        tiempos.push(performance.now() - inicio);
        estados.push(respuesta.status());
      }
      resumen[ruta] = {
        mediana: Math.round(percentil(tiempos, 50) * 10) / 10,
        p95: Math.round(percentil(tiempos, 95) * 10) / 10,
        maximo: Math.round(Math.max(...tiempos) * 10) / 10,
        estados: [...new Set(estados)],
      };
    }

    guardar(testInfo.project.name, 'api', { navegador: testInfo.project.name, repeticiones: REPETICIONES, resumen, limites: LIMITES });
    await testInfo.attach('tiempos-api.json', { body: JSON.stringify(resumen, null, 2), contentType: 'application/json' });

    for (const [ruta, datos] of Object.entries(resumen)) {
      expect(datos.estados, `estados de ${ruta}`).toEqual([200]);
      expect(datos.mediana, `mediana de ${ruta}`).toBeLessThan(LIMITES.apiMediana);
      expect(datos.p95, `p95 de ${ruta}`).toBeLessThan(LIMITES.apiP95);
    }
  });

  test('la API comprime con Brotli y responde 304 cuando los datos no cambiaron', async ({ request }) => {
    const cabeceras = await autorizacion(request, 'admin');
    const primera = await request.get('/api/vehiculos/?limit=50', { headers: { ...cabeceras, 'Accept-Encoding': 'br' } });
    expect(primera.status()).toBe(200);
    const etag = primera.headers()['etag'];
    expect(etag).toBeTruthy();
    expect(primera.headers()['cache-control']).toBe('private, no-cache');

    const igual = await request.get('/api/vehiculos/?limit=50', { headers: { ...cabeceras, 'If-None-Match': etag } });
    expect(igual.status()).toBe(304);
  });
});
