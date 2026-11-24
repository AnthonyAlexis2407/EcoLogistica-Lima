/**
 * Cola de acciones sin conexión del conductor (RNF-010, RF-004, RF-008).
 *
 * Cada entrega o reprogramación se guarda en el dispositivo con una clave única (`clave_sync`) y se envía en lote al
 * servidor cuando hay red. La clave hace que reenviar sea seguro: el servidor ignora lo que ya aplicó. El último
 * recorrido descargado también se guarda para poder verlo sin señal.
 */

import { conductorApi, type AccionSync, type ResultadoSync, type Ruta } from './api';

const CLAVE_COLA = 'cola-sync-v1';
const CLAVE_RUTA = 'ruta-offline-v1';
export const INTERVALO_SYNC_MS = 30_000; // la medida es ≤ 5 min tras recuperar la señal: se reintenta cada 30 s

function leer<T>(clave: string, defecto: T): T {
  try {
    const crudo = localStorage.getItem(clave);
    return crudo ? (JSON.parse(crudo) as T) : defecto;
  } catch {
    return defecto;
  }
}

function escribir(clave: string, valor: unknown): boolean {
  try {
    localStorage.setItem(clave, JSON.stringify(valor));
    return true;
  } catch {
    return false; // cuota llena o almacenamiento bloqueado
  }
}

/** Clave única e irrepetible para una acción (se genera una sola vez, al encolarla). */
export function nuevaClave(): string {
  const azar = typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID().replace(/-/g, '')
    : `${Date.now().toString(36)}${Math.random().toString(36).slice(2)}`;
  return azar.slice(0, 40);
}

export function leerCola(): AccionSync[] {
  return leer<AccionSync[]>(CLAVE_COLA, []);
}

export function encolar(accion: AccionSync): boolean {
  const cola = leerCola();
  if (cola.some((a) => a.clave_sync === accion.clave_sync)) return true;
  return escribir(CLAVE_COLA, [...cola, accion]);
}

export function vaciarCola(): void {
  escribir(CLAVE_COLA, []);
}

export function guardarRuta(ruta: Ruta | null): void {
  if (ruta) escribir(CLAVE_RUTA, ruta);
  else localStorage.removeItem(CLAVE_RUTA);
}

export function rutaGuardada(): Ruta | null {
  return leer<Ruta | null>(CLAVE_RUTA, null);
}

export interface ResumenSync {
  enviadas: number;
  rechazadas: ResultadoSync[];
}

/**
 * Envía la cola. Las acciones aplicadas o ya aplicadas (duplicadas) salen de la cola; las rechazadas también, porque
 * reenviarlas no cambiaría el resultado, y se devuelven para avisar al conductor.
 */
export async function sincronizar(token: string): Promise<ResumenSync> {
  const cola = leerCola();
  if (cola.length === 0) return { enviadas: 0, rechazadas: [] };
  const resultado = await conductorApi.sincronizar(token, cola);
  const resueltas = new Set(resultado.resultados.map((r) => r.clave_sync));
  escribir(CLAVE_COLA, cola.filter((a) => !resueltas.has(a.clave_sync)));
  return {
    enviadas: resultado.aplicadas + resultado.duplicadas,
    rechazadas: resultado.resultados.filter((r) => r.estado === 'RECHAZADA'),
  };
}
