/**
 * API Client — centraliza las llamadas HTTP al backend FastAPI.
 * Base URL configurable via env var VITE_API_URL.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
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

  return res.json();
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
    request<Vehiculo[]>(`/api/vehiculos/${estado ? `?estado=${estado}` : ''}`, { token }),

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
  bodega_id: string;
  direccion: string;
  latitud: number;
  longitud: number;
  peso_kg: number;
  ventana_inicio: string;
  ventana_fin: string;
}

export const pedidosApi = {
  list: (token: string, estado?: string) =>
    request<Pedido[]>(`/api/pedidos/${estado ? `?estado=${estado}` : ''}`, { token }),

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
//  HEALTH
// ═══════════════════════════════════════════════════════════════════════

export const healthApi = {
  check: () => request<{ status: string }>('/api/health'),
};

export { ApiError };
