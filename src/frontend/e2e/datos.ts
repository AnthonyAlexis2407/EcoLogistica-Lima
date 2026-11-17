/**
 * Datos y ayudantes compartidos por las pruebas E2E.
 *
 * Las cuentas son las de los datos de demostración (`python -m app.seed`, o `SEED_DEMO_DATA=true` en el
 * servidor). Pueden cambiarse con variables de entorno para apuntar a otro entorno.
 */
import type { APIRequestContext } from '@playwright/test';

export const USUARIOS = {
  admin: {
    email: process.env.E2E_ADMIN_EMAIL ?? 'admin@ecologistica.pe',
    password: process.env.E2E_ADMIN_PASSWORD ?? 'Admin2026!',
    nombre: 'Administrador EcoLogística',
  },
  operador: {
    email: process.env.E2E_OPERADOR_EMAIL ?? 'operador@ecologistica.pe',
    password: process.env.E2E_OPERADOR_PASSWORD ?? 'Operador2026!',
  },
  bodega: {
    email: process.env.E2E_BODEGA_EMAIL ?? 'bodega@tienda.pe',
    password: process.env.E2E_BODEGA_PASSWORD ?? 'Bodega2026!',
  },
} as const;

export type Rol = keyof typeof USUARIOS;

/** Archivo donde `preparacion.setup.ts` guarda la sesión de cada rol (carpeta ignorada por Git). */
export const archivoSesion = (rol: Rol) => `.auth/${rol}.json`;

/** Texto aleatorio corto en mayúsculas y números, para que cada prueba use datos propios. */
export const sufijo = (largo = 4) =>
  Math.random().toString(36).replace(/[^a-z0-9]/g, '').toUpperCase().padEnd(largo, 'X').slice(0, largo);

/** Inicia sesión por la API y devuelve el encabezado de autorización. */
export async function autorizacion(request: APIRequestContext, rol: Rol) {
  const respuesta = await request.post('/api/auth/login', {
    data: { email: USUARIOS[rol].email, password: USUARIOS[rol].password },
  });
  if (!respuesta.ok()) throw new Error(`No se pudo iniciar sesión como ${rol}: ${respuesta.status()}`);
  const { access_token: token } = await respuesta.json();
  return { Authorization: `Bearer ${token}` };
}

/** Crea por la API una cuenta nueva con rol BODEGA (registro público) para pruebas de bloqueo. */
export async function crearCuentaDePrueba(request: APIRequestContext) {
  const email = `e2e.${sufijo(8).toLowerCase()}@prueba.pe`;
  const password = 'ClavePrueba2026!';
  const respuesta = await request.post('/api/auth/register', {
    data: { nombre: 'Cuenta de prueba E2E', email, password, rol: 'BODEGA' },
  });
  if (!respuesta.ok()) throw new Error(`No se pudo crear la cuenta de prueba: ${respuesta.status()}`);
  return { email, password };
}

/** Registra vehículos por la API (requiere sesión de administrador). */
export async function crearVehiculos(request: APIRequestContext, cabeceras: Record<string, string>, prefijo: string, cantidad: number) {
  for (let i = 1; i <= cantidad; i++) {
    const respuesta = await request.post('/api/vehiculos/', {
      headers: cabeceras,
      data: { placa: `${prefijo}-${String(i).padStart(2, '0')}`, capacidad_kg: 500 + i, tipo_combustible: 'GLP' },
    });
    if (respuesta.status() !== 201) throw new Error(`No se pudo crear el vehículo ${i}: ${respuesta.status()}`);
  }
}
