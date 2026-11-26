/**
 * Diseño adaptable en un móvil emulado (Pixel 7): Playwright reconstruye el dispositivo con su ventana,
 * eventos táctiles y agente de usuario. Verifica que ninguna pantalla se desplace en horizontal (WCAG 1.4.10).
 */
import { expect, test } from '@playwright/test';
import { archivoSesion } from './datos';

const sinDesbordeHorizontal = async (page: import('@playwright/test').Page) =>
  page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1);

test.describe('Móvil sin sesión', () => {
  test('el inicio de sesión cabe en la pantalla y se puede usar con toques', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: 'Iniciar Sesión' })).toBeVisible();
    expect(await sinDesbordeHorizontal(page)).toBe(true);
    await page.getByLabel('Correo electrónico').tap();
    await expect(page.getByLabel('Correo electrónico')).toBeFocused();
  });
});

test.describe('Móvil con sesión', () => {
  test.use({ storageState: archivoSesion('admin') });

  for (const [ruta, titulo] of [['/', 'Dashboard'], ['/vehiculos', 'Gestión de Flota Vehicular'], ['/pedidos', 'Gestión de Pedidos'], ['/rutas', 'Rutas Optimizadas']]) {
    test(`${ruta} no se desplaza en horizontal`, async ({ page }) => {
      await page.goto(ruta);
      await expect(page.getByRole('heading', { name: titulo })).toBeVisible();
      expect(await sinDesbordeHorizontal(page)).toBe(true);
    });
  }
});
