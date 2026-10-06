/**
 * PedidosPage — Registro y gestión de pedidos (US-003).
 * - Registro con dirección, ventana horaria, peso y geolocalización
 * - Validación de capacidad vehicular (RF-002)
 * - Aislamiento por bodega (RN-010) se maneja en el backend
 */

import { useEffect, useState, type FormEvent } from 'react';
import { useAuth } from '../AuthContext';
import { pedidosApi, ApiError, type Pedido, type PedidoForm } from '../api';
import { Plus, Package, X, AlertCircle, MapPin, Clock } from 'lucide-react';

const estadoBadge: Record<string, string> = {
  PENDIENTE: 'badge-amber',
  ASIGNADO: 'badge-blue',
  EN_RUTA: 'badge-teal',
  ENTREGADO: 'badge-green',
  CANCELADO: 'badge-red',
};

const emptyForm: PedidoForm = {
  bodega_id: '',
  direccion: '',
  latitud: -12.0464,
  longitud: -77.0428,
  peso_kg: 0,
  ventana_inicio: '',
  ventana_fin: '',
};

export default function PedidosPage() {
  const { token, user } = useAuth();
  const canCreate = user?.rol === 'OPERADOR' || user?.rol === 'BODEGA';

  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<PedidoForm>(emptyForm);
  const [formError, setFormError] = useState('');
  const [toast, setToast] = useState<{ type: string; msg: string } | null>(null);
  const [filter, setFilter] = useState('');

  const load = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await pedidosApi.list(token, filter || undefined);
      setPedidos(data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  useEffect(() => { load(); }, [token, filter]);

  const showToast = (type: string, msg: string) => {
    setToast({ type, msg });
    setTimeout(() => setToast(null), 4500);
  };

  const openCreate = () => {
    setForm(emptyForm);
    setFormError('');
    setShowModal(true);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setFormError('');

    try {
      await pedidosApi.create(token, form);
      showToast('success', 'Pedido registrado exitosamente');
      setShowModal(false);
      load();
    } catch (err) {
      if (err instanceof ApiError) {
        setFormError(err.detail);
      } else {
        setFormError('Error de conexión');
      }
    }
  };

  const handleCancel = async (p: Pedido) => {
    if (!token) return;
    if (!confirm(`¿Cancelar el pedido a "${p.direccion}"?`)) return;
    try {
      await pedidosApi.cancel(token, p.pedido_id);
      showToast('success', 'Pedido cancelado');
      load();
    } catch (err) {
      if (err instanceof ApiError) showToast('error', err.detail);
    }
  };

  const formatDate = (iso: string) => {
    return new Date(iso).toLocaleString('es-PE', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  };

  return (
    <>
      {toast && (
        <div className={`toast toast-${toast.type}`}>
          {toast.type === 'success' ? '✓' : '✕'} {toast.msg}
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
            {pedidos.length} pedido{pedidos.length !== 1 ? 's' : ''}
          </p>
          <select
            className="form-input form-select"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            style={{ width: 'auto', fontSize: '0.8125rem', padding: '0.35rem 2rem 0.35rem 0.5rem' }}
          >
            <option value="">Todos los estados</option>
            <option value="PENDIENTE">Pendiente</option>
            <option value="ASIGNADO">Asignado</option>
            <option value="EN_RUTA">En ruta</option>
            <option value="ENTREGADO">Entregado</option>
            <option value="CANCELADO">Cancelado</option>
          </select>
        </div>
        {canCreate && (
          <button className="btn btn-primary" onClick={openCreate} id="btn-add-pedido">
            <Plus size={16} /> Registrar Pedido
          </button>
        )}
      </div>

      <div className="card">
        <div className="table-container">
          {loading ? (
            <div className="loading-spinner"><div className="spinner" /></div>
          ) : pedidos.length === 0 ? (
            <div className="empty-state">
              <Package size={48} />
              <h4>Sin pedidos registrados</h4>
              <p>Registre el primer pedido para incorporarlo a la cola de planificación.</p>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Dirección</th>
                  <th>Peso</th>
                  <th>Ventana Horaria</th>
                  <th>Estado</th>
                  <th>Creado</th>
                  {user?.rol === 'OPERADOR' && <th style={{ textAlign: 'right' }}>Acciones</th>}
                </tr>
              </thead>
              <tbody>
                {pedidos.map((p) => (
                  <tr key={p.pedido_id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                        <MapPin size={14} style={{ color: 'var(--color-primary)', marginTop: '2px', flexShrink: 0 }} />
                        <div>
                          <div style={{ fontWeight: 500 }}>{p.direccion}</div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>
                            {Number(p.latitud).toFixed(4)}, {Number(p.longitud).toFixed(4)}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td><strong>{Number(p.peso_kg).toLocaleString('es-PE')} kg</strong></td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.8125rem' }}>
                        <Clock size={12} />
                        <span>{formatDate(p.ventana_inicio)}</span>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                        → {formatDate(p.ventana_fin)}
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${estadoBadge[p.estado] || 'badge-gray'}`}>{p.estado}</span>
                    </td>
                    <td style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                      {formatDate(p.creado_en)}
                    </td>
                    {user?.rol === 'OPERADOR' && (
                      <td style={{ textAlign: 'right' }}>
                        {p.estado !== 'CANCELADO' && p.estado !== 'ENTREGADO' && (
                          <button className="btn btn-ghost btn-sm" onClick={() => handleCancel(p)} style={{ color: 'var(--color-danger)' }}>
                            Cancelar
                          </button>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Modal de registro */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Registrar Pedido</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowModal(false)}>
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                {formError && (
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-md)', background: '#fee2e2', color: '#991b1b', fontSize: '0.8125rem' }}>
                    <AlertCircle size={16} style={{ flexShrink: 0, marginTop: 2 }} /> {formError}
                  </div>
                )}

                <div className="form-group">
                  <label className="form-label" htmlFor="bodega_id">ID de Bodega *</label>
                  <input
                    id="bodega_id"
                    className="form-input"
                    value={form.bodega_id}
                    onChange={(e) => setForm({ ...form, bodega_id: e.target.value })}
                    placeholder="UUID de la bodega"
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="direccion">Dirección de entrega *</label>
                  <input
                    id="direccion"
                    className="form-input"
                    value={form.direccion}
                    onChange={(e) => setForm({ ...form, direccion: e.target.value })}
                    placeholder="Av. Santa Rosa 456, Santa Anita, Lima"
                    required
                  />
                </div>

                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label" htmlFor="lat">Latitud *</label>
                    <input
                      id="lat"
                      className="form-input"
                      type="number"
                      value={form.latitud}
                      onChange={(e) => setForm({ ...form, latitud: Number(e.target.value) })}
                      step="0.0001"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="lng">Longitud *</label>
                    <input
                      id="lng"
                      className="form-input"
                      type="number"
                      value={form.longitud}
                      onChange={(e) => setForm({ ...form, longitud: Number(e.target.value) })}
                      step="0.0001"
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="peso">Peso (kg) *</label>
                  <input
                    id="peso"
                    className="form-input"
                    type="number"
                    value={form.peso_kg || ''}
                    onChange={(e) => setForm({ ...form, peso_kg: Number(e.target.value) })}
                    placeholder="500"
                    required
                    min={0.01}
                    step="0.01"
                  />
                </div>

                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label" htmlFor="v_inicio">Ventana inicio *</label>
                    <input
                      id="v_inicio"
                      className="form-input"
                      type="datetime-local"
                      value={form.ventana_inicio}
                      onChange={(e) => setForm({ ...form, ventana_inicio: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="v_fin">Ventana fin *</label>
                    <input
                      id="v_fin"
                      className="form-input"
                      type="datetime-local"
                      value={form.ventana_fin}
                      onChange={(e) => setForm({ ...form, ventana_fin: e.target.value })}
                      required
                    />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary">
                  Registrar Pedido
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
