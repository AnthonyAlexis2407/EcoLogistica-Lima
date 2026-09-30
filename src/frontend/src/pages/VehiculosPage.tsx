/**
 * VehiculosPage — CRUD de vehículos de la flota (US-001).
 * - Registro con placa única
 * - Edición de campos
 * - Baja lógica (estado FUERA_DE_SERVICIO)
 * - RBAC: ADMIN_FLOTA = CRUD, OPERADOR/AUDITOR = solo lectura
 */

import { useEffect, useState, type FormEvent } from 'react';
import { useAuth } from '../AuthContext';
import { vehiculosApi, ApiError, type Vehiculo, type VehiculoForm } from '../api';
import { Plus, Pencil, Trash2, Truck, X, AlertCircle } from 'lucide-react';

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
  placa: '', capacidad_kg: 0, tipo_combustible: 'DIESEL', factor_emision_co2: undefined, estado: 'DISPONIBLE',
};

export default function VehiculosPage() {
  const { token, user } = useAuth();
  const isAdmin = user?.rol === 'ADMIN_FLOTA';

  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState<VehiculoForm>(emptyForm);
  const [formError, setFormError] = useState('');
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
    setForm(emptyForm);
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
        showToast('success', `Vehículo ${form.placa} actualizado`);
      } else {
        await vehiculosApi.create(token, form);
        showToast('success', `Vehículo ${form.placa} registrado exitosamente`);
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

  return (
    <>
      {/* Toast */}
      {toast && (
        <div className={`toast toast-${toast.type}`}>
          {toast.type === 'success' ? '✓' : '✕'} {toast.msg}
        </div>
      )}

      {/* Header actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
          {vehiculos.length} vehículo{vehiculos.length !== 1 ? 's' : ''} en el catálogo
        </p>
        {isAdmin && (
          <button className="btn btn-primary" onClick={openCreate} id="btn-add-vehiculo">
            <Plus size={16} /> Registrar Vehículo
          </button>
        )}
      </div>

      {/* Table */}
      <div className="card">
        <div className="table-container">
          {loading ? (
            <div className="loading-spinner"><div className="spinner" /></div>
          ) : vehiculos.length === 0 ? (
            <div className="empty-state">
              <Truck size={48} />
              <h4>Sin vehículos registrados</h4>
              <p>Registre el primer vehículo de la flota para comenzar.</p>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Placa</th>
                  <th>Capacidad (kg)</th>
                  <th>Combustible</th>
                  <th>Factor CO₂</th>
                  <th>Estado</th>
                  {isAdmin && <th style={{ textAlign: 'right' }}>Acciones</th>}
                </tr>
              </thead>
              <tbody>
                {vehiculos.map((v) => (
                  <tr key={v.vehiculo_id}>
                    <td>
                      <strong style={{ fontFamily: 'monospace', letterSpacing: '0.05em' }}>{v.placa}</strong>
                    </td>
                    <td>{Number(v.capacidad_kg).toLocaleString('es-PE')} kg</td>
                    <td>
                      <span className={`badge ${combustibleBadge[v.tipo_combustible] || 'badge-gray'}`}>
                        {v.tipo_combustible}
                      </span>
                    </td>
                    <td>{v.factor_emision_co2 ? `${v.factor_emision_co2} kg/L` : '—'}</td>
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
              <h3>{editId ? 'Editar Vehículo' : 'Registrar Vehículo'}</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowModal(false)}>
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                {formError && (
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-md)', background: '#fee2e2', color: '#991b1b', fontSize: '0.8125rem' }}>
                    <AlertCircle size={16} /> {formError}
                  </div>
                )}

                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label" htmlFor="placa">Placa *</label>
                    <input
                      id="placa"
                      className="form-input"
                      value={form.placa}
                      onChange={(e) => setForm({ ...form, placa: e.target.value.toUpperCase() })}
                      placeholder="ABC-123"
                      required
                      maxLength={10}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label" htmlFor="capacidad">Capacidad (kg) *</label>
                    <input
                      id="capacidad"
                      className="form-input"
                      type="number"
                      value={form.capacidad_kg || ''}
                      onChange={(e) => setForm({ ...form, capacidad_kg: Number(e.target.value) })}
                      placeholder="1500"
                      required
                      min={1}
                      step="0.01"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label" htmlFor="combustible">Combustible *</label>
                    <select
                      id="combustible"
                      className="form-input form-select"
                      value={form.tipo_combustible}
                      onChange={(e) => setForm({ ...form, tipo_combustible: e.target.value })}
                    >
                      {TIPOS.map((t) => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label" htmlFor="factor">Factor CO₂ (kg/L)</label>
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
                      <label className="form-label" htmlFor="estado">Estado</label>
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
                  {editId ? 'Guardar Cambios' : 'Registrar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
