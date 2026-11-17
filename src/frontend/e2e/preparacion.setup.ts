/**
 * Preparación de sesiones: inicia sesión una sola vez por rol y guarda el estado del navegador
 * (el token en `localStorage`). Las pruebas lo reutilizan con `test.use({ storageState })` en lugar de
 * repetir el inicio de sesión en cada caso, que es la práctica que recomienda Playwright.
 */
import { mkdirSync, writeFileSync } from 'node:fs';
import { test as preparar } from '@playwright/test';
import { archivoSesion, autorizacion, type Rol, USUARIOS } from './datos';

for (const rol of Object.keys(USUARIOS) as Rol[]) {
  preparar(`guarda la sesión de ${rol}`, async ({ request, baseURL }) => {
    const { Authorization } = await autorizacion(request, rol);
    const token = Authorization.replace('Bearer ', '');
    mkdirSync('.auth', { recursive: true });
    writeFileSync(
      archivoSesion(rol),
      JSON.stringify({ cookies: [], origins: [{ origin: baseURL!, localStorage: [{ name: 'token', value: token }] }] }),
    );
  });
}
