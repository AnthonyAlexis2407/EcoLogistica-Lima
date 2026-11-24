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
  distrito?: string;
  page?: number;
  limit?: number;
}

function consulta(opciones: OpcionesListado): string {
  const params = new URLSearchParams();
  if (opciones.estado) params.set('estado', opciones.estado);
  if (opciones.q) params.set('q', opciones.q);
  if (opciones.distrito) params.set('distrito', opciones.distrito);
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
  telefono?: string | null;
  canal_notificacion?: string;
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

  register: (data: { nombre: string; email: string; password: string; rol: string; telefono?: string; canal_notificacion?: string }) =>
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
  volumen_m3?: number | null;
  tipo_combustible: string;
  factor_emision_co2: number | null;
  estado: string;
}

export interface VehiculoForm {
  placa: string;
  capacidad_kg: number;
  volumen_m3?: number;
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
  volumen_m3?: number | null;
  distrito?: string | null;
  ventana_inicio: string;
  ventana_fin: string;
  estado: string;
  reprogramaciones?: number;
  entregado_en?: string | null;
  creado_en: string;
}

export interface PedidoForm {
  bodega_id?: string;
  direccion: string;
  latitud: number;
  longitud: number;
  peso_kg: number;
  volumen_m3?: number;
  distrito?: string;
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
  parada_id?: string;
  pedido_id: string;
  orden: number;
  estado?: string;
  distrito?: string | null;
  entregada_en?: string | null;
  evidencia_tipo?: string | null;
  motivo?: string | null;
  ventana_inicio?: string | null;
  ventana_fin?: string | null;
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
  distancia_base_km?: number;
  co2_base_kg?: number;
  conductor_id?: string | null;
  conductor_nombre?: string | null;
  iniciada_en?: string | null;
  completada_en?: string | null;
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
  desde_cache?: boolean;
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
  combustible_ahorrado_litros?: number;
  rutas_completadas?: number;
  co2_compensado_kg?: number;
  arboles_compensados?: number;
  distrito?: string | null;
}

export interface FiltrosDashboard {
  distrito?: string;
  desde?: string;
  hasta?: string;
}

export type FormatoReporte = 'csv' | 'xlsx' | 'pdf';

export type TipoIncidencia = 'VIA_CERRADA' | 'ACCIDENTE' | 'AVERIA' | 'PEDIDO_CANCELADO';

export interface IncidenciaForm {
  tipo: TipoIncidencia;
  descripcion?: string;
  latitud?: number;
  longitud?: number;
  radio_km?: number;
  pedido_id?: string;
}

export interface Reoptimizacion {
  tiempo_ms: number;
  dentro_del_sla: boolean;
  sugerencia: string;
  pedidos_devueltos: { pedido_id: string; motivo: string }[];
  nuevas_rutas: Ruta[];
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

  asignarConductor: (token: string, id: string, conductorId: string) =>
    request<Ruta>(`/api/rutas/${id}/conductor`, { method: 'POST', body: { conductor_id: conductorId }, token }),

  iniciar: (token: string, id: string) =>
    request<Ruta>(`/api/rutas/${id}/iniciar`, { method: 'POST', token }),

  completar: (token: string, id: string) =>
    request<{ mensaje: string }>(`/api/rutas/${id}/completar`, { method: 'POST', token }),

  incidencia: (token: string, id: string, datos: IncidenciaForm) =>
    request<Reoptimizacion>(`/api/rutas/${id}/incidencias`, { method: 'POST', body: datos, token }),
};

function filtros(f: FiltrosDashboard): string {
  const params = new URLSearchParams();
  if (f.distrito) params.set('distrito', f.distrito);
  if (f.desde) params.set('desde', f.desde);
  if (f.hasta) params.set('hasta', f.hasta);
  const texto = params.toString();
  return texto ? `?${texto}` : '';
}

export const indicadoresApi = {
  resumen: (token: string, f: FiltrosDashboard = {}) =>
    request<Indicadores>(`/api/indicadores/resumen${filtros(f)}`, { token }),

  distritos: (token: string) => request<string[]>('/api/indicadores/distritos', { token }),
};

export const reportesApi = {
  /** Descarga un reporte; el token viaja en la cabecera, por eso no es un simple enlace. */
  descargar: async (token: string, tipo: TipoReporte, formato: FormatoReporte = 'csv', f: FiltrosDashboard = {}): Promise<Blob> =>
    (await requestRaw(`/api/reportes/${tipo}.${formato}${filtros(f)}`, { token })).blob(),
};

// ═══════════════════════════════════════════════════════════════════════
//  CONDUCTOR (RF-004, RF-008) Y SINCRONIZACIÓN SIN CONEXIÓN (RNF-010)
// ═══════════════════════════════════════════════════════════════════════

export interface EvidenciaEntrega {
  evidencia_tipo: 'FOTO' | 'FIRMA';
  evidencia: string;
  latitud?: number;
  longitud?: number;
  momento?: string;
  clave_sync?: string;
}

export interface AccionSync extends Partial<EvidenciaEntrega> {
  tipo: 'ENTREGA' | 'REPROGRAMACION';
  parada_id: string;
  clave_sync: string;
  motivo?: string;
}

export interface ResultadoSync {
  clave_sync: string;
  estado: 'APLICADA' | 'DUPLICADA' | 'RECHAZADA';
  detalle: string;
}

export interface SyncResultado {
  resultados: ResultadoSync[];
  aplicadas: number;
  duplicadas: number;
  rechazadas: number;
}

export const conductorApi = {
  miRuta: (token: string) => request<Ruta>('/api/conductor/ruta', { token }),

  entregar: (token: string, paradaId: string, datos: EvidenciaEntrega) =>
    request<{ ruta_completable: boolean; reoptimizada: boolean; mensaje: string }>(
      `/api/conductor/paradas/${paradaId}/entregar`, { method: 'POST', body: datos, token },
    ),

  reprogramar: (token: string, paradaId: string, motivo: string, claveSync?: string) =>
    request<{ ruta_completable: boolean; mensaje: string }>(
      `/api/conductor/paradas/${paradaId}/reprogramar`, { method: 'POST', body: { motivo, clave_sync: claveSync }, token },
    ),

  sincronizar: (token: string, acciones: AccionSync[]) =>
    request<SyncResultado>('/api/conductor/sync', { method: 'POST', body: { acciones }, token }),

  ubicacion: (token: string, latitud: number, longitud: number) =>
    request<{ desviado: boolean; desviacion_km: number; reoptimizada: boolean; mensaje: string }>(
      '/api/conductor/ubicacion', { method: 'POST', body: { latitud, longitud }, token },
    ),
};

// ═══════════════════════════════════════════════════════════════════════
//  NOTIFICACIONES (RF-009)
// ═══════════════════════════════════════════════════════════════════════

export interface Notificacion {
  notificacion_id: string;
  pedido_id: string | null;
  tipo: string;
  canal: string;
  mensaje: string;
  hora_estimada: string | null;
  estado_envio: string;
  leida: boolean;
  creado_en: string;
}

export const notificacionesApi = {
  mias: async (token: string): Promise<{ items: Notificacion[]; noLeidas: number }> => {
    const res = await requestRaw('/api/notificaciones/', { token });
    return { items: await res.json(), noLeidas: Number(res.headers.get('X-Unread-Count') ?? 0) };
  },

  pendientesDeContacto: (token: string) =>
    request<Notificacion[]>('/api/notificaciones/pendientes-de-contacto', { token }),

  marcarLeida: (token: string, id: string) =>
    request<{ mensaje: string }>(`/api/notificaciones/${id}/leida`, { method: 'PUT', token }),
};

// ═══════════════════════════════════════════════════════════════════════
//  ADMINISTRACIÓN (usuarios, conductores, parámetros, zonas, privacidad)
// ═══════════════════════════════════════════════════════════════════════

export interface Conductor {
  conductor_id: string;
  usuario_id: string;
  nombre: string;
  email: string;
  licencia: string;
  telefono: string | null;
  activo: boolean;
}

export interface ConductorForm {
  nombre: string;
  email: string;
  password: string;
  licencia: string;
  telefono?: string;
}

export interface Parametros {
  velocidad_kmh: number;
  servicio_min: number;
  limite_segundos: number;
}

export interface Zona {
  zona_id: string;
  nombre: string;
  latitud: number;
  longitud: number;
  radio_km: number;
  activa: boolean;
}

export interface SolicitudPrivacidad {
  solicitud_id: string;
  usuario_id: string;
  estado: string;
  solicitada_en: string;
  plazo_limite: string;
  atendida_en: string | null;
}

export const adminApi = {
  usuarios: (token: string) => request<Usuario[]>('/api/admin/usuarios', { token }),

  actualizarUsuario: (token: string, id: string, datos: Partial<{ nombre: string; telefono: string; canal_notificacion: string; rol: string; password: string }>) =>
    request<Usuario>(`/api/admin/usuarios/${id}`, { method: 'PUT', body: datos, token }),

  eliminarUsuario: (token: string, id: string) =>
    request<{ mensaje: string }>(`/api/admin/usuarios/${id}?confirmar=true`, { method: 'DELETE', token }),

  conductores: (token: string) => request<Conductor[]>('/api/admin/conductores', { token }),

  crearConductor: (token: string, datos: ConductorForm) =>
    request<Conductor>('/api/admin/conductores', { method: 'POST', body: datos, token }),

  actualizarConductor: (token: string, id: string, datos: Partial<{ nombre: string; licencia: string; telefono: string; activo: boolean }>) =>
    request<Conductor>(`/api/admin/conductores/${id}`, { method: 'PUT', body: datos, token }),

  parametros: (token: string) => request<Parametros>('/api/admin/parametros', { token }),

  guardarParametros: (token: string, datos: Parametros) =>
    request<Parametros>('/api/admin/parametros', { method: 'PUT', body: datos, token }),

  zonas: (token: string) => request<Zona[]>('/api/admin/zonas', { token }),

  crearZona: (token: string, datos: Omit<Zona, 'zona_id' | 'activa'>) =>
    request<Zona>('/api/admin/zonas', { method: 'POST', body: datos, token }),

  eliminarZona: (token: string, id: string) =>
    request<{ mensaje: string }>(`/api/admin/zonas/${id}`, { method: 'DELETE', token }),

  solicitudes: (token: string) => request<SolicitudPrivacidad[]>('/api/privacidad/solicitudes', { token }),

  atenderSolicitud: (token: string, id: string) =>
    request<SolicitudPrivacidad>(`/api/privacidad/solicitudes/${id}/atender`, { method: 'POST', token }),
};

export const privacidadApi = {
  solicitarBaja: (token: string) =>
    request<SolicitudPrivacidad>('/api/privacidad/solicitudes', { method: 'POST', token }),
};

// ═══════════════════════════════════════════════════════════════════════
//  HEALTH
// ═══════════════════════════════════════════════════════════════════════

export const healthApi = {
  check: () => request<{ status: string }>('/api/health'),
};

export { ApiError };
