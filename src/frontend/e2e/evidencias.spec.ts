/**
 * Capturas de pantalla de las pantallas clave, usadas como evidencia de la demostración del Sprint 4.
 *
 * Solo se ejecutan a demanda (`E2E_EVIDENCIAS=1`), para no añadir ruido a la suite habitual:
 *   E2E_EVIDENCIAS=1 npx playwright test --project=chromium e2e/evidencias.spec.ts
 * Las imágenes quedan en `test-results/evidencias/`.
 */
import { expect, test } from '@playwright/test';
import { archivoSesion } from './datos';

test.skip(process.env.E2E_EVIDENCIAS !== '1', 'Capturas de evidencia: se activan con E2E_EVIDENCIAS=1');

const destino = (nombre: string) => ({ path: `test-results/evidencias/${nombre}.png`, fullPage: false });

test.describe('Evidencias sin sesión', () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test('inicio de sesión y mensaje de clave incorrecta', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: 'Iniciar Sesión' })).toBeVisible();
    await page.screenshot(destino('01-inicio-de-sesion'));

    await page.getByLabel('Correo electrónico').fill('admin@ecologistica.pe');
    await page.getByLabel('Contraseña').fill('clave-incorrecta');
    await page.getByRole('button', { name: 'Ingresar' }).click();
    await expect(page.getByText(/Credenciales inválidas/)).toBeVisible();
    await page.screenshot(destino('02-clave-incorrecta-intentos-restantes'));
  });
});

test.describe('Evidencias con sesión de administrador', () => {
  test.use({ storageState: archivoSesion('admin') });

  test('dashboard, flota y pedidos', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
    await expect(page.getByText('API conectada')).toBeVisible();
    await page.screenshot(destino('03-dashboard'));

    await page.goto('/vehiculos');
    await expect(page.getByRole('heading', { name: 'Gestión de Flota Vehicular' })).toBeVisible();
    await expect(page.getByRole('table')).toBeVisible();
    await page.screenshot(destino('04-flota-vehicular'));

    await page.getByRole('button', { name: /Registrar Vehículo/ }).first().click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await page.screenshot(destino('05-formulario-de-vehiculo-con-ayuda'));
    await page.keyboard.press('Escape');

    await page.goto('/pedidos');
    await expect(page.getByRole('heading', { name: 'Gestión de Pedidos' })).toBeVisible();
    await page.screenshot(destino('06-gestion-de-pedidos'));

    await page.getByRole('button', { name: /Registrar Pedido/ }).click();
    await expect(page.getByText(/grados decimales/)).toBeVisible();
    await page.screenshot(destino('07-formulario-de-pedido-con-ayuda-de-coordenadas'));
  });

  test('vista móvil de la flota', async ({ page }) => {
    await page.setViewportSize({ width: 412, height: 915 });
    await page.goto('/vehiculos');
    await expect(page.getByRole('heading', { name: 'Gestión de Flota Vehicular' })).toBeVisible();
    await page.screenshot(destino('08-flota-en-movil'));
  });
});
