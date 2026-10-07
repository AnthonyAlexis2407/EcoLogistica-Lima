/**
 * VehiculosPage — CRUD de vehículos de la flota (US-001) con diseño Light SaaS.
 */

import { useEffect, useState, type FormEvent } from 'react';
import { useAuth } from '../AuthContext';
import { vehiculosApi, ApiError, type Vehiculo, type VehiculoForm } from '../api';
import { Plus, Pencil, Trash2, Truck, X, AlertCircle, Search, Fuel } from 'lucide-react';

const TIPOS = ['DIESEL', 'GASOLINA', 'GLP', 'HIBRIDO', 'ELECTRICO'];
const ESTADOS = ['DISPONIBLE', 'EN_MANTENIMIENTO', 'FUERA_DE_SERVICIO'];

const estadoBadge: Record<string, string> = {
  DISPONIBLE: 'badge-green',
  EN_MANTENIMIENTO: 'badge-amber',
  FUERA_DE_SERVICIO: 'badge-red',
};

const combustibleBadge: Record<string, string> = {
  DIESEL: 'badge-gray',
  GASOLINA: 'badge-blue',
  GLP: 'badge-teal',
  HIBRIDO: 'badge-green',
  ELECTRICO: 'badge-green',
};

const emptyForm: VehiculoForm = {
  placa: '', capacidad_kg: 1500, tipo_combustible: 'DIESEL', factor_emision_co2: 2.68, estado: 'DISPONIBLE',
};

export default function VehiculosPage() {
  const { token, user } = useAuth();
  const isAdmin = true; // Habilitado para demostración fluida

  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState<VehiculoForm>(emptyForm);
  const [formError, setFormError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [toast, setToast] = useState<{ type: string; msg: string } | null>(null);

  const load = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await vehiculosApi.list(token);
      setVehiculos(data);
    } catch { /* ignore */ }
    setLoading(false);
  };

  useEffect(() => { load(); }, [token]);

  const showToast = (type: string, msg: string) => {
    setToast({ type, msg });
    setTimeout(() => setToast(null), 4500);
  };

  const openCreate = () => {
    setEditId(null);
    setForm({
      placa: '',
      capacidad_kg: 1500,
      tipo_combustible: 'DIESEL',
      factor_emision_co2: 2.68,
      estado: 'DISPONIBLE',
    });
    setFormError('');
    setShowModal(true);
  };

  const openEdit = (v: Vehiculo) => {
    setEditId(v.vehiculo_id);
    setForm({
      placa: v.placa,
      capacidad_kg: v.capacidad_kg,
      tipo_combustible: v.tipo_combustible,
      factor_emision_co2: v.factor_emision_co2 ?? undefined,
      estado: v.estado,
    });
    setFormError('');
    setShowModal(true);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setFormError('');

    try {
      if (editId) {
        await vehiculosApi.update(token, editId, form);
        showToast('success', `Vehículo ${form.placa} actualizado exitosamente`);
      } else {
        await vehiculosApi.create(token, form);
        showToast('success', `Vehículo ${form.placa} registrado en la flota`);
      }
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

  const handleDelete = async (v: Vehiculo) => {
    if (!token) return;
    if (!confirm(`¿Desea dar de baja el vehículo ${v.placa}?`)) return;
    try {
      await vehiculosApi.delete(token, v.vehiculo_id);
      showToast('success', `Vehículo ${v.placa} dado de baja`);
      load();
    } catch (err) {
      if (err instanceof ApiError) showToast('error', err.detail);
    }
  };

  const filtered = vehiculos.filter((v) => {
    const matchSearch = v.placa.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        v.tipo_combustible.toLowerCase().includes(searchTerm.toLowerCase());
    const matchStatus = !statusFilter || v.estado === statusFilter;
    return matchSearch && matchStatus;
  });

  return (
    <>
      {toast && (
        <div className={`toast toast-${toast.type}`}>
          {toast.type === 'success' ? '✓' : '✕'} {toast.msg}
        </div>
      )}

      {/* Header & Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', width: 240 }}>
            <Search size={16} style={{ position: 'absolute', left: 12, top: 11, color: 'var(--color-text-muted)' }} />
            <input
              className="form-input"
              style={{ paddingLeft: '2.25rem' }}
              placeholder="Buscar por placa..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <select
            className="form-input form-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ width: 'auto' }}
          >
            <option value="">Todos los estados</option>
            <option value="DISPONIBLE">Disponible</option>
            <option value="EN_MANTENIMIENTO">En Mantenimiento</option>
            <option value="FUERA_DE_SERVICIO">Fuera de Servicio</option>
          </select>
        </div>

        {isAdmin && (
          <button className="btn btn-primary" onClick={openCreate} id="btn-add-vehiculo">
            <Plus size={18} /> Registrar Vehículo
          </button>
        )}
      </div>

      {/* Table Card */}
      <div className="card">
        <div className="table-container">
          {loading ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--color-text-secondary)' }}>Cargando catálogo de flota...</div>
          ) : filtered.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center' }}>
              <Truck size={48} style={{ color: 'var(--color-text-muted)', marginBottom: '1rem' }} />
              <h4 style={{ fontSize: '1.125rem', fontWeight: 700 }}>Sin vehículos que coincidan</h4>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Intente ajustar el filtro o registre una nueva unidad.</p>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Placa / Identificador</th>
                  <th>Capacidad de Carga</th>
                  <th>Tipo de Combustible</th>
                  <th>Factor CO₂</th>
                  <th>Estado Operativo</th>
                  {isAdmin && <th style={{ textAlign: 'right' }}>Acciones</th>}
                </tr>
              </thead>
              <tbody>
                {filtered.map((v) => (
                  <tr key={v.vehiculo_id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <div style={{ background: 'var(--color-primary-bg)', color: 'var(--color-primary)', width: 36, height: 36, borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800 }}>
                          <Truck size={18} />
                        </div>
                        <div>
                          <strong style={{ fontFamily: 'var(--font-mono)', fontSize: '0.9375rem', letterSpacing: '0.05em' }}>{v.placa}</strong>
                          <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>Flota Activa</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div style={{ fontWeight: 800, fontSize: '0.9375rem', color: 'var(--color-secondary)' }}>
                        {Number(v.capacidad_kg).toLocaleString('es-PE')} kg
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${combustibleBadge[v.tipo_combustible] || 'badge-gray'}`}>
                        <Fuel size={12} /> {v.tipo_combustible}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                        {v.factor_emision_co2 ? `${v.factor_emision_co2} kg/L` : '—'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${estadoBadge[v.estado] || 'badge-gray'}`}>{v.estado}</span>
                    </td>
                    {isAdmin && (
                      <td style={{ textAlign: 'right' }}>
                        <button className="btn btn-ghost btn-sm" onClick={() => openEdit(v)} title="Editar">
                          <Pencil size={14} />
                        </button>
                        {v.estado !== 'FUERA_DE_SERVICIO' && (
                          <button className="btn btn-ghost btn-sm" onClick={() => handleDelete(v)} title="Dar de baja" style={{ color: 'var(--color-danger)' }}>
                            <Trash2 size={14} />
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

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editId ? 'Editar Vehículo' : 'Registrar Nuevo Vehículo'}</h3>
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
                  <label className="form-label" htmlFor="placa">Placa del Vehículo *</label>
                  <input
                    id="placa"
                    className="form-input"
                    value={form.placa}
                    onChange={(e) => setForm({ ...form, placa: e.target.value.toUpperCase() })}
                    placeholder="Ej. ABC-123"
                    required
                    maxLength={10}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div className="form-group">
                    <label className="form-label" htmlFor="capacidad">Capacidad de Carga (kg) *</label>
                    <input
                      id="capacidad"
                      className="form-input"
                      type="number"
                      value={form.capacidad_kg || ''}
                      onChange={(e) => setForm({ ...form, capacidad_kg: Number(e.target.value) })}
                      placeholder="1500"
                      required
                      min={1}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label" htmlFor="combustible">Tipo de Combustible *</label>
                    <select
                      id="combustible"
                      className="form-input form-select"
                      value={form.tipo_combustible}
                      onChange={(e) => setForm({ ...form, tipo_combustible: e.target.value })}
                    >
                      {TIPOS.map((t) => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div className="form-group">
                    <label className="form-label" htmlFor="factor">Factor Emisión CO₂ (kg/L)</label>
                    <input
                      id="factor"
                      className="form-input"
                      type="number"
                      value={form.factor_emision_co2 ?? ''}
                      onChange={(e) => setForm({ ...form, factor_emision_co2: e.target.value ? Number(e.target.value) : undefined })}
                      placeholder="2.68"
                      step="0.01"
                    />
                  </div>

                  {editId && (
                    <div className="form-group">
                      <label className="form-label" htmlFor="estado">Estado Operativo</label>
                      <select
                        id="estado"
                        className="form-input form-select"
                        value={form.estado}
                        onChange={(e) => setForm({ ...form, estado: e.target.value })}
                      >
                        {ESTADOS.map((e) => <option key={e} value={e}>{e}</option>)}
                      </select>
                    </div>
                  )}
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary">
                  {editId ? 'Guardar Cambios' : 'Registrar Vehículo'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
