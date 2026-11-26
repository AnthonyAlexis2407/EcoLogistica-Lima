/**
 * Portabilidad (RNF-010): la app del conductor es una PWA instalable que abre sin conexión.
 *
 * El modo sin conexión con service worker se verifica en Chromium; Firefox y WebKit comparten la comprobación del
 * manifiesto y de los iconos (el service worker offline depende del motor y de la política del navegador).
 */
import { expect, test } from '@playwright/test';

test.use({ serviceWorkers: 'allow' });
import { archivoSesion } from './datos';

test('el manifiesto declara una app instalable con iconos', async ({ request }) => {
  const respuesta = await request.get('/manifest.webmanifest');
  expect(respuesta.status()).toBe(200);
  const manifiesto = await respuesta.json();
  expect(manifiesto.display).toBe('standalone');
  expect(manifiesto.start_url).toBe('/conductor');
  expect(manifiesto.lang).toBe('es-PE');
  const tamanos = manifiesto.icons.map((i: { sizes: string }) => i.sizes);
  expect(tamanos).toEqual(expect.arrayContaining(['192x192', '512x512']));
  for (const icono of manifiesto.icons) expect((await request.get(icono.src)).status()).toBe(200);
});

test('el service worker se sirve desde la raíz y el HTML enlaza el manifiesto', async ({ request, page }) => {
  const sw = await request.get('/sw.js');
  expect(sw.status()).toBe(200);
  expect(sw.headers()['content-type']).toContain('javascript');
  expect(await sw.text()).toContain('self.addEventListener');
  await page.goto('/login');
  await expect(page.locator('link[rel="manifest"]')).toHaveAttribute('href', '/manifest.webmanifest');
  await expect(page.locator('meta[name="theme-color"]')).toHaveAttribute('content', '#047857');
});

test.describe('Sin conexión (Chromium)', () => {
  test.use({ storageState: archivoSesion('conductor') });

  test('registra el service worker y reabre la aplicación sin red', async ({ page, context, browserName }) => {
    test.skip(browserName !== 'chromium', 'El modo sin conexión con service worker se verifica en Chromium');
    await page.goto('/conductor');
    await expect(page.getByRole('heading', { name: 'Mi ruta', level: 2 })).toBeVisible();
    await page.evaluate(() => navigator.serviceWorker.ready);
    // El service worker guarda los recursos que la página le envía tras cargar.
    await expect.poll(async () => page.evaluate(async () => (await caches.keys()).length), { timeout: 10_000 }).toBeGreaterThan(0);
    await page.waitForTimeout(500);

    await context.setOffline(true);
    await page.reload();
    await expect(page.getByRole('heading', { name: 'Mi ruta', level: 2 })).toBeVisible();
    await expect(page.getByText(/Sin conexión/)).toBeVisible();
    await context.setOffline(false);
  });
});
