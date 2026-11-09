import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiError, authApi, healthApi, pedidosApi, vehiculosApi } from '../api';

const fetchMock = vi.fn();

function respuesta(body: unknown, status = 200, cabeceras: Record<string, string> = {}) {
  return {
    ok: status < 400, status, json: () => Promise.resolve(body),
    headers: { get: (nombre: string) => cabeceras[nombre] ?? null },
  } as unknown as Response;
}

beforeEach(() => {
  vi.stubGlobal('fetch', fetchMock);
  fetchMock.mockReset();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('cliente HTTP', () => {
  it('envía el token como Bearer y devuelve el JSON', async () => {
    fetchMock.mockResolvedValue(respuesta([{ placa: 'ABC-123' }]));
    const data = await vehiculosApi.list('tok-1');

    expect(data).toEqual([{ placa: 'ABC-123' }]);
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toContain('/api/vehiculos/');
    expect(init.headers.Authorization).toBe('Bearer tok-1');
    expect(init.method).toBe('GET');
  });

  it('listPage devuelve los registros y el total de la cabecera X-Total-Count', async () => {
    fetchMock.mockResolvedValue(respuesta([{ placa: 'A' }, { placa: 'B' }], 200, { 'X-Total-Count': '37' }));
    expect(await vehiculosApi.listPage('tok')).toEqual({ items: [{ placa: 'A' }, { placa: 'B' }], total: 37 });
  });

  it('listPage usa la cantidad de registros si el servidor no informa el total', async () => {
    fetchMock.mockResolvedValue(respuesta([{ pedido_id: 'p1' }]));
    expect((await pedidosApi.listPage('tok')).total).toBe(1);
  });

  it('serializa el cuerpo en POST y no envía Authorization sin token', async () => {
    fetchMock.mockResolvedValue(respuesta({ access_token: 'x' }));
    await authApi.login('a@b.pe', 'clave');

    const [, init] = fetchMock.mock.calls[0];
    expect(init.method).toBe('POST');
    expect(JSON.parse(init.body)).toEqual({ email: 'a@b.pe', password: 'clave' });
    expect(init.headers.Authorization).toBeUndefined();
  });

  it('lanza ApiError con el detalle del servidor', async () => {
    fetchMock.mockResolvedValue(respuesta({ detail: 'Placa duplicada' }, 409));
    const error = await vehiculosApi.create('t', { placa: 'A', capacidad_kg: 1, tipo_combustible: 'GLP' }).catch((e) => e);

    expect(error).toBeInstanceOf(ApiError);
    expect(error.status).toBe(409);
    expect(error.detail).toBe('Placa duplicada');
  });

  it('usa un mensaje genérico si la respuesta de error no es JSON', async () => {
    fetchMock.mockResolvedValue({ ok: false, status: 500, json: () => Promise.reject(new Error('no json')) } as Response);
    const error = await healthApi.check().catch((e) => e);

    expect(error).toBeInstanceOf(ApiError);
    expect(error.detail).toBe('Error de conexión');
  });

  it('usa el código HTTP cuando el error no trae detail', async () => {
    fetchMock.mockResolvedValue(respuesta({}, 503));
    const error = await healthApi.check().catch((e) => e);
    expect(error.detail).toBe('Error 503');
  });
});

describe('rutas de cada recurso', () => {
  beforeEach(() => {
    fetchMock.mockResolvedValue(respuesta({}));
  });

  const llamadas: [string, () => Promise<unknown>, string, string][] = [
    ['auth.register', () => authApi.register({ nombre: 'N', email: 'e@e.pe', password: 'p', rol: 'BODEGA' }), 'POST', '/api/auth/register'],
    ['auth.me', () => authApi.me('t'), 'GET', '/api/auth/me'],
    ['vehiculos.list filtrado', () => vehiculosApi.list('t', 'DISPONIBLE'), 'GET', '/api/vehiculos/?estado=DISPONIBLE'],
    ['vehiculos.get', () => vehiculosApi.get('t', 'v1'), 'GET', '/api/vehiculos/v1'],
    ['vehiculos.update', () => vehiculosApi.update('t', 'v1', { capacidad_kg: 5 }), 'PUT', '/api/vehiculos/v1'],
    ['vehiculos.delete', () => vehiculosApi.delete('t', 'v1'), 'DELETE', '/api/vehiculos/v1'],
    ['vehiculos.count', () => vehiculosApi.count('t'), 'GET', '/api/vehiculos/count'],
    ['pedidos.list filtrado', () => pedidosApi.list('t', 'PENDIENTE'), 'GET', '/api/pedidos/?estado=PENDIENTE'],
    ['vehiculos.listPage', () => vehiculosApi.listPage('t', { page: 2, q: 'abc', estado: 'DISPONIBLE' }), 'GET', '/api/vehiculos/?estado=DISPONIBLE&q=abc&page=2&limit=12'],
    ['pedidos.listPage', () => pedidosApi.listPage('t'), 'GET', '/api/pedidos/?limit=12'],
    ['pedidos.get', () => pedidosApi.get('t', 'p1'), 'GET', '/api/pedidos/p1'],
    ['pedidos.create', () => pedidosApi.create('t', { bodega_id: 'b', direccion: 'd', latitud: 0, longitud: 0, peso_kg: 1, ventana_inicio: 'i', ventana_fin: 'f' }), 'POST', '/api/pedidos/'],
    ['pedidos.update', () => pedidosApi.update('t', 'p1', { estado: 'ASIGNADO' }), 'PUT', '/api/pedidos/p1'],
    ['pedidos.cancel', () => pedidosApi.cancel('t', 'p1'), 'DELETE', '/api/pedidos/p1'],
    ['pedidos.count', () => pedidosApi.count('t'), 'GET', '/api/pedidos/count'],
    ['health', () => healthApi.check(), 'GET', '/api/health'],
  ];

  it.each(llamadas)('%s', async (_nombre, ejecutar, metodo, ruta) => {
    await ejecutar();
    const [url, init] = fetchMock.mock.calls[0];
    expect(url.endsWith(ruta)).toBe(true);
    expect(init.method).toBe(metodo);
  });
});
