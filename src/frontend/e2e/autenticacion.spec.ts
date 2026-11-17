/**
 * Autenticación (EN-002): ruta feliz, rutas infelices (clave errónea, bloqueo, validación) y sesión.
 * Estas pruebas parten SIN sesión; las cuentas que se bloquean se crean al vuelo para no afectar a otras pruebas.
 */
import { expect, test } from '@playwright/test';
import { archivoSesion, crearCuentaDePrueba, USUARIOS } from './datos';

test.describe('Autenticación', () => {
  test('ruta feliz: el administrador entra al Dashboard', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL(/\/login$/);

    await page.getByLabel('Correo electrónico').fill(USUARIOS.admin.email);
    await page.getByLabel('Contraseña').fill(USUARIOS.admin.password);
    await page.getByRole('button', { name: 'Ingresar' }).click();

    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
    await expect(page.getByText('Administrador de Flota')).toBeVisible();
  });

  test('ruta infeliz: una clave incorrecta informa los intentos restantes', async ({ page, request }) => {
    const cuenta = await crearCuentaDePrueba(request);
    await page.goto('/login');
    await page.getByLabel('Correo electrónico').fill(cuenta.email);
    await page.getByLabel('Contraseña').fill('clave-equivocada');
    await page.getByRole('button', { name: 'Ingresar' }).click();

    await expect(page.getByText('Credenciales inválidas. Intentos restantes: 2')).toBeVisible();
    await expect(page).toHaveURL(/\/login$/);
  });

  test('ruta infeliz: tres intentos fallidos bloquean la cuenta aunque luego se use la clave correcta', async ({ page, request }) => {
    const cuenta = await crearCuentaDePrueba(request);
    await page.goto('/login');
    for (let intento = 0; intento < 3; intento++) {
      await page.getByLabel('Correo electrónico').fill(cuenta.email);
      await page.getByLabel('Contraseña').fill('clave-equivocada');
      await page.getByRole('button', { name: 'Ingresar' }).click();
      await expect(page.getByText(/Credenciales inválidas|Cuenta bloqueada/)).toBeVisible();
    }

    await page.getByLabel('Contraseña').fill(cuenta.password);
    await page.getByRole('button', { name: 'Ingresar' }).click();
    await expect(page.getByText(/Cuenta bloqueada por múltiples intentos fallidos/)).toBeVisible();
    await expect(page).toHaveURL(/\/login$/);
  });

  test('validación del formulario: sin datos no se envía nada al servidor', async ({ page }) => {
    let peticionesDeLogin = 0;
    page.on('request', (r) => { if (r.url().includes('/api/auth/login')) peticionesDeLogin++; });

    await page.goto('/login');
    await page.getByRole('button', { name: 'Ingresar' }).click();

    // El navegador marca el campo obligatorio como inválido y no deja enviar.
    const correo = page.getByLabel('Correo electrónico');
    expect(await correo.evaluate((el: HTMLInputElement) => el.validity.valueMissing)).toBe(true);
    await page.getByLabel('Correo electrónico').fill('correo-sin-arroba');
    await page.getByLabel('Contraseña').fill('algo');
    await page.getByRole('button', { name: 'Ingresar' }).click();
    expect(await correo.evaluate((el: HTMLInputElement) => el.validity.typeMismatch)).toBe(true);
    expect(peticionesDeLogin).toBe(0);
  });

  test('una ruta protegida sin sesión redirige al inicio de sesión', async ({ page }) => {
    await page.goto('/vehiculos');
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole('heading', { name: 'Iniciar Sesión' })).toBeVisible();
  });
});

test.describe('Sesión iniciada', () => {
  test.use({ storageState: archivoSesion('admin') });

  test('cerrar sesión devuelve al inicio de sesión y borra el token', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

    await page.getByTitle('Cerrar sesión').click();
    await expect(page.getByRole('heading', { name: 'Iniciar Sesión' })).toBeVisible();
    expect(await page.evaluate(() => localStorage.getItem('token'))).toBeNull();
  });
});
