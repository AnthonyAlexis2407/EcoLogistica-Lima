/**
 * PedidosPage — Registro y gestión de pedidos (US-003) con diseño Light SaaS.
 */

import { useEffect, useState, type FormEvent } from 'react';
import { useAuth } from '../AuthContext';
import { pedidosApi, ApiError, type Pedido, type PedidoForm } from '../api';
import { Plus, Package, X, AlertCircle, MapPin, Clock, Search } from 'lucide-react';

const estadoBadge: Record<string, string> = {
  PENDIENTE: 'badge-amber',
  ASIGNADO: 'badge-blue',
  EN_RUTA: 'badge-teal',
  ENTREGADO: 'badge-green',
  CANCELADO: 'badge-red',
};

const emptyForm: PedidoForm = {
  bodega_id: '038bb42a-4a26-4497-ae1f-97837027a346',
  direccion: 'Av. Javier Prado Este 2465, San Borja, Lima',
  latitud: -12.0864,
  longitud: -77.0012,
  peso_kg: 350,
  ventana_inicio: '',
  ventana_fin: '',
};

export default function PedidosPage() {
  const { token, user } = useAuth();
  const canCreate = true;

  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<PedidoForm>(emptyForm);
  const [formError, setFormError] = useState('');
  const [toast, setToast] = useState<{ type: string; msg: string } | null>(null);
  const [filter, setFilter] = useState('');
  const [searchAddress, setSearchAddress] = useState('');

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
    const defaultBodega = pedidos[0]?.bodega_id || '038bb42a-4a26-4497-ae1f-97837027a346';
    const now = new Date();
    const startStr = new Date(now.getTime() + 3600000).toISOString().slice(0, 16);
    const endStr = new Date(now.getTime() + 18000000).toISOString().slice(0, 16);

    setForm({
      bodega_id: defaultBodega,
      direccion: 'Av. Javier Prado Este 2465, San Borja, Lima',
      latitud: -12.0864,
      longitud: -77.0012,
      peso_kg: 350,
      ventana_inicio: startStr,
      ventana_fin: endStr,
    });
    setFormError('');
    setShowModal(true);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setFormError('');

    const payload = {
      ...form,
      bodega_id: form.bodega_id || pedidos[0]?.bodega_id || '038bb42a-4a26-4497-ae1f-97837027a346',
    };

    try {
      await pedidosApi.create(token, payload);
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
    if (!iso) return '—';
    return new Date(iso).toLocaleString('es-PE', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  };

  const filteredPedidos = pedidos.filter((p) =>
    p.direccion.toLowerCase().includes(searchAddress.toLowerCase())
  );

  return (
    <>
      {toast && (
        <div className={`toast toast-${toast.type}`}>
          {toast.type === 'success' ? '✓' : '✕'} {toast.msg}
        </div>
      )}

      {/* Controls Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', width: 260 }}>
            <Search size={16} style={{ position: 'absolute', left: 12, top: 11, color: 'var(--color-text-muted)' }} />
            <input
              className="form-input"
              style={{ paddingLeft: '2.25rem' }}
              placeholder="Buscar por dirección..."
              value={searchAddress}
              onChange={(e) => setSearchAddress(e.target.value)}
            />
          </div>

          <select
            className="form-input form-select"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            style={{ width: 'auto' }}
          >
            <option value="">Todos los estados</option>
            <option value="PENDIENTE">Pendiente</option>
            <option value="ASIGNADO">Asignado</option>
            <option value="EN_RUTA">En Ruta</option>
            <option value="ENTREGADO">Entregado</option>
            <option value="CANCELADO">Cancelado</option>
          </select>
        </div>

        {canCreate && (
          <button className="btn btn-primary" onClick={openCreate} id="btn-add-pedido">
            <Plus size={18} /> Registrar Pedido
          </button>
        )}
      </div>

      {/* Table Card */}
      <div className="card">
        <div className="table-container">
          {loading ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--color-text-secondary)' }}>Cargando cola de pedidos...</div>
          ) : filteredPedidos.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center' }}>
              <Package size={48} style={{ color: 'var(--color-text-muted)', marginBottom: '1rem' }} />
              <h4 style={{ fontSize: '1.125rem', fontWeight: 700 }}>Sin pedidos registrados</h4>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Registre un nuevo pedido para incorporarlo a la cola de distribución.</p>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Dirección de Entrega</th>
                  <th>Peso del Paquete</th>
                  <th>Ventana Horaria</th>
                  <th>Estado del Envío</th>
                  <th>Fecha Registro</th>
                  <th style={{ textAlign: 'right' }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredPedidos.map((p) => (
                  <tr key={p.pedido_id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.65rem' }}>
                        <div style={{ background: 'var(--color-primary-bg)', color: 'var(--color-primary)', width: 34, height: 34, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginTop: 2 }}>
                          <MapPin size={16} />
                        </div>
                        <div>
                          <div style={{ fontWeight: 700, color: 'var(--color-secondary)' }}>{p.direccion}</div>
                          <div style={{ fontSize: '0.725rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
                            {Number(p.latitud).toFixed(4)}, {Number(p.longitud).toFixed(4)}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <strong style={{ fontSize: '0.9375rem', color: 'var(--color-secondary)' }}>
                        {Number(p.peso_kg).toLocaleString('es-PE')} kg
                      </strong>
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                        <Clock size={13} style={{ color: 'var(--color-primary)' }} />
                        <span>{formatDate(p.ventana_inicio)}</span>
                      </div>
                      <div style={{ fontSize: '0.725rem', color: 'var(--color-text-muted)', paddingLeft: '1.2rem' }}>
                        → {formatDate(p.ventana_fin)}
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${estadoBadge[p.estado] || 'badge-gray'}`}>{p.estado}</span>
                    </td>
                    <td style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                      {formatDate(p.creado_en)}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      {p.estado !== 'CANCELADO' && p.estado !== 'ENTREGADO' && (
                        <button className="btn btn-ghost btn-sm" onClick={() => handleCancel(p)} style={{ color: 'var(--color-danger)' }}>
                          Cancelar
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Registrar Nuevo Pedido</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowModal(false)}>
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                {formError && (
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', padding: '0.65rem 0.875rem', borderRadius: 'var(--radius-md)', background: 'var(--color-danger-bg)', color: 'var(--color-danger-text)', fontSize: '0.8125rem' }}>
                    <AlertCircle size={16} /> {formError}
                  </div>
                )}

                <div className="form-group">
                  <label className="form-label" htmlFor="direccion">Dirección de Entrega *</label>
                  <input
                    id="direccion"
                    className="form-input"
                    value={form.direccion}
                    onChange={(e) => setForm({ ...form, direccion: e.target.value })}
                    placeholder="Av. Javier Prado Este 2465, San Borja, Lima"
                    required
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
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
                  <label className="form-label" htmlFor="peso">Peso del Paquete (kg) *</label>
                  <input
                    id="peso"
                    className="form-input"
                    type="number"
                    value={form.peso_kg || ''}
                    onChange={(e) => setForm({ ...form, peso_kg: Number(e.target.value) })}
                    placeholder="350"
                    required
                    min={0.01}
                    step="0.01"
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div className="form-group">
                    <label className="form-label" htmlFor="v_inicio">Ventana Inicio *</label>
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
                    <label className="form-label" htmlFor="v_fin">Ventana Fin *</label>
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
