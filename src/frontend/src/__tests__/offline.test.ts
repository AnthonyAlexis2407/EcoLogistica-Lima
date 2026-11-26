import { beforeEach, describe, expect, it, vi } from 'vitest';
import { conductorApi, type AccionSync, type Ruta } from '../api';
import { encolar, guardarRuta, leerCola, nuevaClave, rutaGuardada, sincronizar, vaciarCola } from '../offline';

vi.mock('../api', async (original) => ({
  ...(await original<typeof import('../api')>()),
  conductorApi: { sincronizar: vi.fn() },
}));

const accion = (clave: string): AccionSync => ({
  tipo: 'ENTREGA', parada_id: 'p1', clave_sync: clave, evidencia_tipo: 'FIRMA', evidencia: 'data:image/png;base64,AAAA',
});

beforeEach(() => {
  vi.resetAllMocks();
});

describe('cola sin conexión (RNF-010)', () => {
  it('genera claves únicas e irrepetibles', () => {
    const claves = new Set(Array.from({ length: 200 }, () => nuevaClave()));
    expect(claves.size).toBe(200);
    expect([...claves].every((c) => c.length >= 8 && c.length <= 64)).toBe(true);
  });

  it('encolar es idempotente por clave y sobrevive a una recarga (localStorage)', () => {
    expect(encolar(accion('clave-0001'))).toBe(true);
    expect(encolar(accion('clave-0001'))).toBe(true);
    expect(encolar(accion('clave-0002'))).toBe(true);
    expect(leerCola().map((a) => a.clave_sync)).toEqual(['clave-0001', 'clave-0002']);
    vaciarCola();
    expect(leerCola()).toEqual([]);
  });

  it('si el almacenamiento falla, la cola se lee vacía y encolar informa el error', () => {
    const espiaLeer = vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => { throw new Error('bloqueado'); });
    expect(leerCola()).toEqual([]);
    espiaLeer.mockRestore();
    const espiaEscribir = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new Error('cuota'); });
    expect(encolar(accion('clave-0003'))).toBe(false);
    espiaEscribir.mockRestore();
  });

  it('sincroniza en lote y retira lo aplicado, lo duplicado y lo rechazado', async () => {
    ['clave-a001', 'clave-a002', 'clave-a003', 'clave-a004'].forEach((c) => encolar(accion(c)));
    vi.mocked(conductorApi.sincronizar).mockResolvedValue({
      aplicadas: 1, duplicadas: 1, rechazadas: 1,
      resultados: [
        { clave_sync: 'clave-a001', estado: 'APLICADA', detalle: '' },
        { clave_sync: 'clave-a002', estado: 'DUPLICADA', detalle: 'Ya aplicada' },
        { clave_sync: 'clave-a003', estado: 'RECHAZADA', detalle: 'La parada ya fue resuelta' },
      ],
    });
    const resumen = await sincronizar('tok');
    expect(resumen.enviadas).toBe(2);
    expect(resumen.rechazadas.map((r) => r.detalle)).toEqual(['La parada ya fue resuelta']);
    // Solo queda la acción que el servidor no devolvió (p. ej. porque el lote se cortó).
    expect(leerCola().map((a) => a.clave_sync)).toEqual(['clave-a004']);
  });

  it('sin acciones no llama al servidor y, si la red falla, conserva la cola', async () => {
    expect(await sincronizar('tok')).toEqual({ enviadas: 0, rechazadas: [] });
    expect(conductorApi.sincronizar).not.toHaveBeenCalled();
    encolar(accion('clave-b001'));
    vi.mocked(conductorApi.sincronizar).mockRejectedValue(new TypeError('Failed to fetch'));
    await expect(sincronizar('tok')).rejects.toThrow();
    expect(leerCola()).toHaveLength(1);
  });

  it('guarda y recupera la última ruta para verla sin señal', () => {
    const ruta = { ruta_id: 'r1', placa: 'ABC-123', paradas: [] } as unknown as Ruta;
    guardarRuta(ruta);
    expect(rutaGuardada()?.ruta_id).toBe('r1');
    guardarRuta(null);
    expect(rutaGuardada()).toBeNull();
  });
});
