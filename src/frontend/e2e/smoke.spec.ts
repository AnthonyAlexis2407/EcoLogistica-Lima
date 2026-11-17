/**
 * Prueba de humo del entorno DESPLEGADO (monitoreo sintético).
 *
 * No necesita cuentas ni datos de demostración: comprueba que el sitio responde, que la API está viva y que la
 * interfaz carga. El flujo `deploy-production.yml` la ejecuta contra la URL de producción justo después del
 * despliegue:  E2E_BASE_URL=https://<url> npx playwright test --project=smoke
 */
import { expect, test } from '@playwright/test';

test.describe('Humo de producción @smoke', () => {
  test('el sitio entrega la interfaz y la API de salud responde ok', async ({ request, page }) => {
    const salud = await request.get('/api/health');
    expect(salud.status()).toBe(200);
    expect(await salud.json()).toMatchObject({ status: 'ok' });

    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Iniciar Sesión' })).toBeVisible();
    await expect(page).toHaveTitle(/EcoLogística Lima/);
  });

  test('los datos siguen protegidos: sin sesión la API responde 401', async ({ request }) => {
    expect((await request.get('/api/vehiculos/')).status()).toBe(401);
  });

  test('el sitio responde rápido: la página principal en menos de 3 s', async ({ request }) => {
    const inicio = Date.now();
    const respuesta = await request.get('/');
    expect(respuesta.status()).toBe(200);
    expect(Date.now() - inicio).toBeLessThan(3000);
  });
});
