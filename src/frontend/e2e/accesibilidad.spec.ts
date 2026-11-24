/**
 * Accesibilidad (RNF-007): auditoría automática con axe-core (WCAG 2.0/2.1/2.2 nivel A y AA) en cada pantalla, y
 * comprobación manual-automatizada de la navegación por teclado: el foco queda atrapado en el diálogo abierto, Escape lo
 * cierra y el foco vuelve al botón que lo abrió.
 *
 * El mapa de Leaflet se excluye del análisis: es un complemento visual y la información de las rutas está duplicada en
 * tablas de texto (WCAG 1.1.1), que sí se auditan.
 */
import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Page } from '@playwright/test';
import { archivoSesion } from './datos';

const ETIQUETAS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'];

async function auditar(page: Page) {
  const resultado = await new AxeBuilder({ page }).withTags(ETIQUETAS).exclude('.leaflet-container').analyze();
  const resumen = resultado.violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.map((n) => n.target.join(' ')).slice(0, 3).join(' | ')}`);
  expect(resumen, 'violaciones de accesibilidad').toEqual([]);
}

test.describe('Sin sesión', () => {
  test('el inicio de sesión cumple WCAG 2.2 AA', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: 'Iniciar Sesión' })).toBeVisible();
    await auditar(page);
  });
});

test.describe('Administrador', () => {
  test.use({ storageState: archivoSesion('admin') });

  for (const [ruta, titulo] of [
    ['/', 'Dashboard'], ['/vehiculos', 'Gestión de Flota Vehicular'], ['/pedidos', 'Gestión de Pedidos'],
    ['/rutas', 'Rutas Optimizadas'], ['/notificaciones', 'Notificaciones'], ['/administracion', 'Administración'],
  ]) {
    test(`${ruta} cumple WCAG 2.2 AA`, async ({ page }) => {
      await page.goto(ruta);
      await expect(page.getByRole('heading', { name: titulo, level: 2 })).toBeVisible();
      await page.waitForLoadState('networkidle');
      await auditar(page);
    });
  }

  test('las pestañas de administración cumplen WCAG 2.2 AA', async ({ page }) => {
    await page.goto('/administracion');
    for (const pestana of ['Conductores', 'Parámetros del algoritmo', 'Zonas protegidas', 'Privacidad']) {
      await page.getByRole('tab', { name: pestana }).click();
      await expect(page.getByRole('tab', { name: pestana })).toHaveAttribute('aria-selected', 'true');
      await auditar(page);
    }
  });

  test('el diálogo de pedido cumple WCAG 2.2 AA y atrapa el foco', async ({ page }) => {
    await page.goto('/pedidos');
    const abrir = page.getByRole('button', { name: /Registrar Pedido/ }).first();
    await abrir.click();
    const dialogo = page.getByRole('dialog', { name: 'Registrar Nuevo Pedido' });
    await expect(dialogo).toBeVisible();
    await auditar(page);

    // Tab repetido: el foco nunca sale del diálogo (WCAG 2.1.2 y 2.4.3).
    for (let i = 0; i < 25; i++) {
      await page.keyboard.press('Tab');
      expect(await page.evaluate(() => !!document.activeElement?.closest('[role="dialog"]')), `Tab ${i + 1}`).toBe(true);
    }
    for (let i = 0; i < 8; i++) {
      await page.keyboard.press('Shift+Tab');
      expect(await page.evaluate(() => !!document.activeElement?.closest('[role="dialog"]')), `Shift+Tab ${i + 1}`).toBe(true);
    }

    await page.keyboard.press('Escape');
    await expect(dialogo).toHaveCount(0);
    await expect(abrir).toBeFocused(); // el foco vuelve a quien abrió el diálogo
  });

  test('todo el menú es operable solo con el teclado', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Dashboard', level: 2 })).toBeVisible();
    const enlace = page.getByRole('navigation').getByRole('link', { name: /Rutas/ });
    await enlace.focus();
    await expect(enlace).toBeFocused();
    await page.keyboard.press('Enter');
    await expect(page.getByRole('heading', { name: 'Rutas Optimizadas' })).toBeVisible();
  });
});

test.describe('Conductor', () => {
  test.use({ storageState: archivoSesion('conductor') });

  test('Mi ruta cumple WCAG 2.2 AA', async ({ page }) => {
    await page.goto('/conductor');
    await expect(page.getByRole('heading', { name: 'Mi ruta', level: 2 })).toBeVisible();
    await page.waitForLoadState('networkidle');
    await auditar(page);
  });
});

test.describe('Dueño de bodega y auditor', () => {
  test.describe('Bodega', () => {
    test.use({ storageState: archivoSesion('bodega') });
    test('el portal de avisos cumple WCAG 2.2 AA', async ({ page }) => {
      await page.goto('/notificaciones');
      await expect(page.getByRole('heading', { name: 'Notificaciones', level: 2 })).toBeVisible();
      await page.waitForLoadState('networkidle');
      await auditar(page);
    });
  });

  test.describe('Auditor', () => {
    test.use({ storageState: archivoSesion('auditor') });
    test('el dashboard del auditor cumple WCAG 2.2 AA', async ({ page }) => {
      await page.goto('/');
      await expect(page.getByRole('heading', { name: 'Dashboard', level: 2 })).toBeVisible();
      await page.waitForLoadState('networkidle');
      await auditar(page);
    });
  });
});
