/**
 * API Client — centraliza las llamadas HTTP al backend FastAPI.
 * Base URL configurable via env var VITE_API_URL.
 */

// VITE_API_URL vacío = mismo origen (la API sirve el frontend compilado); sin definir = desarrollo local.
const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

/** Registros por página en los listados (Informe Green IT: bloques controlados de 12). */
export const PAGE_SIZE = 12;

interface RequestOptions {
  method?: string;
  body?: unknown;
  token?: string | null;
}

class ApiError extends Error {
  status: number;
  detail: string;
  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

async function requestRaw(endpoint: string, options: RequestOptions = {}): Promise<Response> {
  const { method = 'GET', body, token } = options;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({ detail: 'Error de conexión' }));
    throw new ApiError(res.status, data.detail || `Error ${res.status}`);
  }

  return res;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  return (await requestRaw(endpoint, options)).json();
}

/** Página de resultados: los registros y el total que el servidor informa en X-Total-Count. */
export interface Pagina<T> {
  items: T[];
  total: number;
}

export interface OpcionesListado {
  estado?: string;
  q?: string;
  page?: number;
  limit?: number;
}

function consulta(opciones: OpcionesListado): string {
  const params = new URLSearchParams();
  if (opciones.estado) params.set('estado', opciones.estado);
  if (opciones.q) params.set('q', opciones.q);
  if (opciones.page) params.set('page', String(opciones.page));
  if (opciones.limit) params.set('limit', String(opciones.limit));
  const texto = params.toString();
  return texto ? `?${texto}` : '';
}

async function requestPagina<T>(endpoint: string, token: string): Promise<Pagina<T>> {
  const res = await requestRaw(endpoint, { token });
  const items: T[] = await res.json();
  return { items, total: Number(res.headers.get('X-Total-Count') ?? items.length) };
}

// ═══════════════════════════════════════════════════════════════════════
//  AUTH
// ═══════════════════════════════════════════════════════════════════════

export interface Usuario {
  usuario_id: string;
  nombre: string;
  email: string;
  rol: string;
  estado: string;
  creado_en: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  usuario: Usuario;
}

export const authApi = {
  login: (email: string, password: string) =>
    request<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: { email, password },
    }),

  register: (data: { nombre: string; email: string; password: string; rol: string }) =>
    request<Usuario>('/api/auth/register', {
      method: 'POST',
      body: data,
    }),

  me: (token: string) =>
    request<Usuario>('/api/auth/me', { token }),
};

// ═══════════════════════════════════════════════════════════════════════
//  VEHÍCULOS (US-001)
// ═══════════════════════════════════════════════════════════════════════

export interface Vehiculo {
  vehiculo_id: string;
  placa: string;
  capacidad_kg: number;
  tipo_combustible: string;
  factor_emision_co2: number | null;
  estado: string;
}

export interface VehiculoForm {
  placa: string;
  capacidad_kg: number;
  tipo_combustible: string;
  factor_emision_co2?: number;
  estado?: string;
}

export const vehiculosApi = {
  list: (token: string, estado?: string) =>
    request<Vehiculo[]>(`/api/vehiculos/${consulta({ estado })}`, { token }),

  listPage: (token: string, opciones: OpcionesListado = {}) =>
    requestPagina<Vehiculo>(`/api/vehiculos/${consulta({ limit: PAGE_SIZE, ...opciones })}`, token),

  get: (token: string, id: string) =>
    request<Vehiculo>(`/api/vehiculos/${id}`, { token }),

  create: (token: string, data: VehiculoForm) =>
    request<Vehiculo>('/api/vehiculos/', { method: 'POST', body: data, token }),

  update: (token: string, id: string, data: Partial<VehiculoForm>) =>
    request<Vehiculo>(`/api/vehiculos/${id}`, { method: 'PUT', body: data, token }),

  delete: (token: string, id: string) =>
    request<{ mensaje: string }>(`/api/vehiculos/${id}`, { method: 'DELETE', token }),

  count: (token: string) =>
    request<Record<string, number>>('/api/vehiculos/count', { token }),
};

// ═══════════════════════════════════════════════════════════════════════
//  PEDIDOS (US-003)
// ═══════════════════════════════════════════════════════════════════════

export interface Pedido {
  pedido_id: string;
  bodega_id: string;
  direccion: string;
  latitud: number;
  longitud: number;
  peso_kg: number;
  ventana_inicio: string;
  ventana_fin: string;
  estado: string;
  creado_en: string;
}

export interface PedidoForm {
  bodega_id?: string;
  direccion: string;
  latitud: number;
  longitud: number;
  peso_kg: number;
  ventana_inicio: string;
  ventana_fin: string;
}

export const pedidosApi = {
  list: (token: string, estado?: string) =>
    request<Pedido[]>(`/api/pedidos/${consulta({ estado })}`, { token }),

  listPage: (token: string, opciones: OpcionesListado = {}) =>
    requestPagina<Pedido>(`/api/pedidos/${consulta({ limit: PAGE_SIZE, ...opciones })}`, token),

  get: (token: string, id: string) =>
    request<Pedido>(`/api/pedidos/${id}`, { token }),

  create: (token: string, data: PedidoForm) =>
    request<Pedido>('/api/pedidos/', { method: 'POST', body: data, token }),

  update: (token: string, id: string, data: Partial<PedidoForm & { estado: string }>) =>
    request<Pedido>(`/api/pedidos/${id}`, { method: 'PUT', body: data, token }),

  cancel: (token: string, id: string) =>
    request<{ mensaje: string }>(`/api/pedidos/${id}`, { method: 'DELETE', token }),

  count: (token: string) =>
    request<Record<string, number>>('/api/pedidos/count', { token }),
};

// ═══════════════════════════════════════════════════════════════════════
//  RUTAS (RF-003, RF-004), INDICADORES (RF-005, RF-010) Y REPORTES (RF-006)
// ═══════════════════════════════════════════════════════════════════════

export interface ParadaRuta {
  pedido_id: string;
  orden: number;
  direccion: string;
  latitud: number;
  longitud: number;
  peso_kg: number;
  distancia_desde_anterior_km: number;
  llegada_estimada: string | null;
  espera_min: number;
  en_ventana: boolean | null;
}

export interface Ruta {
  ruta_id: string;
  vehiculo_id: string;
  placa: string;
  tipo_combustible: string;
  capacidad_kg: number;
  estado: string;
  distancia_km: number;
  carga_kg: number;
  co2_kg: number;
  duracion_min: number;
  paradas: ParadaRuta[];
}

export interface RutasActivas {
  deposito: { latitud: number; longitud: number };
  rutas: Ruta[];
}

export interface Optimizacion {
  optimizacion_id: string;
  algoritmo: string;
  pedidos_planificados: number;
  pedidos_sin_asignar: number;
  distancia_km: number;
  distancia_base_km: number;
  ahorro_km_pct: number;
  co2_kg: number;
  co2_base_kg: number;
  co2_evitado_kg: number;
  ahorro_co2_pct: number;
  arboles_equivalentes: number;
  tiempo_ms: number;
  limite_alcanzado: boolean;
  rutas: Ruta[];
  sin_asignar: { pedido_id: string; motivo: string }[];
  vehiculos_excluidos: { placa: string; motivo: string }[];
}

export interface Indicadores {
  vehiculos: Record<string, number>;
  pedidos: Record<string, number>;
  rutas_activas: number;
  distancia_planificada_km: number;
  co2_planificado_kg: number;
  pedidos_en_ventana_pct: number | null;
  optimizaciones: number;
  co2_evitado_kg: number;
  ahorro_co2_pct: number;
  ahorro_km_pct: number;
  arboles_equivalentes: number;
}

export type TipoReporte = 'pedidos' | 'rutas' | 'ambiental';

export const rutasApi = {
  activas: (token: string) => request<RutasActivas>('/api/rutas/', { token }),

  optimizar: (token: string, limiteSegundos?: number) =>
    request<Optimizacion>('/api/rutas/optimizar', {
      method: 'POST', body: limiteSegundos ? { limite_segundos: limiteSegundos } : undefined, token,
    }),

  cancelar: (token: string, id: string) =>
    request<{ mensaje: string }>(`/api/rutas/${id}/cancelar`, { method: 'POST', token }),
};

export const indicadoresApi = {
  resumen: (token: string) => request<Indicadores>('/api/indicadores/resumen', { token }),
};

export const reportesApi = {
  /** Descarga un reporte CSV; el token viaja en la cabecera, por eso no es un simple enlace. */
  descargar: async (token: string, tipo: TipoReporte): Promise<Blob> =>
    (await requestRaw(`/api/reportes/${tipo}.csv`, { token })).blob(),
};

// ═══════════════════════════════════════════════════════════════════════
//  HEALTH
// ═══════════════════════════════════════════════════════════════════════

export const healthApi = {
  check: () => request<{ status: string }>('/api/health'),
};

export { ApiError };
