/**
 * RutasPage — Rutas optimizadas (RF-003), mapa interactivo (RF-004), CO₂ evitado (RF-010) y reportes (RF-006).
 *
 * El mapa usa Leaflet con teselas de OpenStreetMap. Es complementario: la lista de rutas con sus paradas, debajo,
 * es su equivalente accesible (WCAG 1.1.1) y contiene la misma información en texto.
 */

import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useAuth } from '../AuthContext';
import {
  ApiError, adminApi, reportesApi, rutasApi,
  type Conductor, type FormatoReporte, type Optimizacion, type Ruta, type RutasActivas, type TipoIncidencia,
  type TipoReporte,
} from '../api';
import Modal from '../components/Modal';
import {
  Route as RutaIcono, Play, Download, Leaf, Gauge, TreePine, Timer, XCircle, Flag, AlertTriangle, PlayCircle,
} from 'lucide-react';

const COLORES = ['#059669', '#2563eb', '#d97706', '#dc2626', '#7c3aed', '#0891b2', '#be185d', '#4d7c0f'];
const LIMA: [number, number] = [-12.0464, -77.0428];

const REPORTES: { tipo: TipoReporte; etiqueta: string }[] = [
  { tipo: 'pedidos', etiqueta: 'Pedidos' },
  { tipo: 'rutas', etiqueta: 'Rutas' },
  { tipo: 'ambiental', etiqueta: 'Ambiental' },
];

const FORMATOS: { valor: FormatoReporte; etiqueta: string }[] = [
  { valor: 'csv', etiqueta: 'CSV' },
  { valor: 'xlsx', etiqueta: 'Excel' },
  { valor: 'pdf', etiqueta: 'PDF' },
];

const INCIDENCIAS: { valor: TipoIncidencia; etiqueta: string }[] = [
  { valor: 'VIA_CERRADA', etiqueta: 'Vía cerrada' },
  { valor: 'ACCIDENTE', etiqueta: 'Accidente' },
  { valor: 'AVERIA', etiqueta: 'Avería del vehículo' },
  { valor: 'PEDIDO_CANCELADO', etiqueta: 'Pedido cancelado' },
];

const ESTADO_RUTA: Record<string, string> = {
  PLANIFICADA: 'badge-blue', EN_CURSO: 'badge-teal', COMPLETADA: 'badge-green', CANCELADA: 'badge-red',
  INTERRUMPIDA: 'badge-amber',
};

function hora(valor: string | null): string {
  if (!valor) return '—';
  return new Date(valor).toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' });
}

/** Mapa de Leaflet: dibuja el depósito, el recorrido de cada ruta y sus paradas numeradas. */
function Mapa({ datos }: { datos: RutasActivas | null }) {
  const contenedor = useRef<HTMLDivElement | null>(null);
  const mapa = useRef<L.Map | null>(null);
  const capa = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!contenedor.current || mapa.current) return;
    const m = L.map(contenedor.current, { scrollWheelZoom: false }).setView(LIMA, 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, attribution: '© OpenStreetMap',
    }).addTo(m);
    capa.current = L.layerGroup().addTo(m);
    mapa.current = m;
    return () => {
      m.remove();
      mapa.current = null;
      capa.current = null;
    };
  }, []);

  useEffect(() => {
    const m = mapa.current;
    const grupo = capa.current;
    if (!m || !grupo) return;
    grupo.clearLayers();
    if (!datos) return;

    const deposito: [number, number] = [datos.deposito.latitud, datos.deposito.longitud];
    const limites: [number, number][] = [deposito];
    L.circleMarker(deposito, { radius: 9, color: '#111827', fillColor: '#111827', fillOpacity: 1 }).addTo(grupo);

    datos.rutas.forEach((ruta, i) => {
      const color = COLORES[i % COLORES.length];
      const puntos: [number, number][] = ruta.paradas.filter((p) => p.estado !== 'RETIRADA').map((p) => [p.latitud, p.longitud]);
      L.polyline([deposito, ...puntos, deposito], { color, weight: 4, opacity: 0.85 }).addTo(grupo);
      ruta.paradas.filter((p) => p.estado !== 'RETIRADA').forEach((p) => {
        L.marker([p.latitud, p.longitud], {
          title: `${ruta.placa} · parada ${p.orden}: ${p.direccion}`,
          icon: L.divIcon({
            className: 'parada-marcador',
            html: `<span style="background:${color}">${p.orden}</span>`,
            iconSize: [26, 26],
          }),
        }).addTo(grupo);
        limites.push([p.latitud, p.longitud]);
      });
    });

    if (limites.length > 1) m.fitBounds(L.latLngBounds(limites), { padding: [30, 30] });
  }, [datos]);

  return <div ref={contenedor} className="mapa-rutas" role="region" aria-label="Mapa de rutas" />;
}

function IncidenciaModal({
  ruta, onEnviar, onCerrar,
}: {
  ruta: Ruta;
  onEnviar: (datos: { tipo: TipoIncidencia; descripcion?: string; latitud?: number; longitud?: number; radio_km?: number; pedido_id?: string }) => void;
  onCerrar: () => void;
}) {
  const pendientes = ruta.paradas.filter((p) => (p.estado ?? 'PENDIENTE') === 'PENDIENTE');
  const [tipo, setTipo] = useState<TipoIncidencia>('VIA_CERRADA');
  const [descripcion, setDescripcion] = useState('');
  const [paradaId, setParadaId] = useState(pendientes[0]?.pedido_id ?? '');
  const [radio, setRadio] = useState(0.5);
  const parada = pendientes.find((p) => p.pedido_id === paradaId);
  const necesitaUbicacion = tipo === 'VIA_CERRADA' || tipo === 'ACCIDENTE';
  const necesitaPedido = tipo === 'PEDIDO_CANCELADO';

  const enviar = (e: React.FormEvent) => {
    e.preventDefault();
    onEnviar({
      tipo, descripcion: descripcion || undefined,
      ...(necesitaUbicacion && parada ? { latitud: parada.latitud, longitud: parada.longitud, radio_km: radio } : {}),
      ...(necesitaPedido ? { pedido_id: paradaId } : {}),
    });
  };

  return (
    <Modal titulo="Registrar incidencia" onCerrar={onCerrar} ancho={460}>
      <form onSubmit={enviar}>
        <div className="modal-body">
          <p className="form-hint">
            La ruta se recalcula en menos de 45 s. Una avería redistribuye los pedidos pendientes en otros vehículos.
          </p>
          <div className="form-group">
            <label className="form-label" htmlFor="inc-tipo">Tipo de incidencia</label>
            <select id="inc-tipo" className="form-input form-select" value={tipo} onChange={(e) => setTipo(e.target.value as TipoIncidencia)}>
              {INCIDENCIAS.map((i) => <option key={i.valor} value={i.valor}>{i.etiqueta}</option>)}
            </select>
          </div>
          {(necesitaUbicacion || necesitaPedido) && (
            <div className="form-group">
              <label className="form-label" htmlFor="inc-parada">{necesitaPedido ? 'Pedido cancelado' : 'Ocurre cerca de la parada'}</label>
              <select id="inc-parada" className="form-input form-select" value={paradaId} onChange={(e) => setParadaId(e.target.value)} required>
                {pendientes.map((p) => <option key={p.pedido_id} value={p.pedido_id}>{p.orden}. {p.direccion}</option>)}
              </select>
            </div>
          )}
          {necesitaUbicacion && (
            <div className="form-group">
              <label className="form-label" htmlFor="inc-radio">Radio afectado (km)</label>
              <input id="inc-radio" className="form-input" type="number" min={0.1} max={10} step="0.1" value={radio}
                onChange={(e) => setRadio(Number(e.target.value))} />
            </div>
          )}
          <div className="form-group">
            <label className="form-label" htmlFor="inc-desc">Descripción (opcional)</label>
            <input id="inc-desc" className="form-input" maxLength={300} value={descripcion} onChange={(e) => setDescripcion(e.target.value)} />
          </div>
        </div>
        <div className="modal-footer">
          <button type="button" className="btn btn-secondary" onClick={onCerrar}>Cancelar</button>
          <button type="submit" className="btn btn-primary" disabled={(necesitaUbicacion || necesitaPedido) && pendientes.length === 0}>
            Re-optimizar
          </button>
        </div>
      </form>
    </Modal>
  );
}

function TarjetaRuta({
  ruta, color, puedeOperar, conductores, onCancelar, onAsignar, onIniciar, onCompletar, onIncidencia,
}: {
  ruta: Ruta; color: string; puedeOperar: boolean; conductores: Conductor[];
  onCancelar: (r: Ruta) => void; onAsignar: (r: Ruta, conductorId: string) => void;
  onIniciar: (r: Ruta) => void; onCompletar: (r: Ruta) => void; onIncidencia: (r: Ruta) => void;
}) {
  const abierta = ruta.estado === 'PLANIFICADA' || ruta.estado === 'EN_CURSO';
  const resuelta = (e?: string) => e === 'ENTREGADA' || e === 'REPROGRAMADA' || e === 'RETIRADA';
  return (
    <div className="card" style={{ marginBottom: '1rem' }}>
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
          <span style={{ width: 14, height: 14, borderRadius: '50%', background: color, display: 'inline-block' }} aria-hidden="true" />
          <h3 style={{ fontSize: '1rem' }}>Vehículo {ruta.placa}</h3>
          <span className="badge badge-teal">{ruta.tipo_combustible}</span>
          <span className={`badge ${ESTADO_RUTA[ruta.estado] ?? 'badge-gray'}`}>{ruta.estado.replace('_', ' ')}</span>
          <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
            {ruta.carga_kg.toLocaleString('es-PE')} de {ruta.capacidad_kg.toLocaleString('es-PE')} kg ·
            {' '}{ruta.distancia_km.toFixed(1)} km · {ruta.co2_kg.toFixed(1)} kg CO₂ · {Math.round(ruta.duracion_min)} min
          </span>
          {ruta.conductor_nombre && <span className="badge badge-gray">Conductor: {ruta.conductor_nombre}</span>}
        </div>
        {puedeOperar && abierta && (
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
            {ruta.estado === 'PLANIFICADA' && (
              <select
                className="form-input form-select" style={{ width: 'auto' }} aria-label={`Conductor de la ruta ${ruta.placa}`}
                value={ruta.conductor_id ?? ''} onChange={(e) => e.target.value && onAsignar(ruta, e.target.value)}
              >
                <option value="">Asignar conductor…</option>
                {conductores.filter((c) => c.activo).map((c) => <option key={c.conductor_id} value={c.conductor_id}>{c.nombre}</option>)}
              </select>
            )}
            {ruta.estado === 'PLANIFICADA' && ruta.conductor_id && (
              <button className="btn btn-secondary btn-sm" onClick={() => onIniciar(ruta)} aria-label={`Iniciar la ruta del vehículo ${ruta.placa}`}>
                <PlayCircle size={16} /> Iniciar
              </button>
            )}
            {ruta.estado === 'EN_CURSO' && ruta.paradas.every((p) => resuelta(p.estado)) && (
              <button className="btn btn-primary btn-sm" onClick={() => onCompletar(ruta)} aria-label={`Completar la ruta del vehículo ${ruta.placa}`}>
                <Flag size={16} /> Completar
              </button>
            )}
            <button className="btn btn-ghost btn-sm" onClick={() => onIncidencia(ruta)} aria-label={`Registrar incidencia en la ruta ${ruta.placa}`}>
              <AlertTriangle size={16} /> Incidencia
            </button>
            <button className="btn btn-ghost btn-sm" onClick={() => onCancelar(ruta)} aria-label={`Cancelar la ruta del vehículo ${ruta.placa}`}>
              <XCircle size={16} /> Cancelar ruta
            </button>
          </div>
        )}
      </div>
      <div className="table-container">
        <table>
          <thead>
            <tr><th>Parada</th><th>Dirección</th><th>Peso</th><th>Distancia</th><th>Llegada</th><th>Ventana horaria</th><th>Estado</th></tr>
          </thead>
          <tbody>
            {ruta.paradas.map((p) => (
              <tr key={p.pedido_id}>
                <td>{p.orden}</td>
                <td>{p.direccion}</td>
                <td>{p.peso_kg.toLocaleString('es-PE')} kg</td>
                <td>{p.distancia_desde_anterior_km.toFixed(1)} km</td>
                <td>{hora(p.llegada_estimada)}{p.espera_min > 0 ? ` (espera ${Math.round(p.espera_min)} min)` : ''}</td>
                <td>
                  {p.en_ventana === null
                    ? '—'
                    : <span className={`badge ${p.en_ventana ? 'badge-green' : 'badge-red'}`}>{p.en_ventana ? 'En ventana' : 'Fuera de ventana'}</span>}
                </td>
                <td>{(p.estado ?? 'PENDIENTE').toLowerCase()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function RutasPage() {
  const { token, user } = useAuth();
  // RBAC (Documento 08): ADMIN_FLOTA y OPERADOR planifican; el AUDITOR solo consulta.
  const puedeOperar = user?.rol === 'ADMIN_FLOTA' || user?.rol === 'OPERADOR';

  const [datos, setDatos] = useState<RutasActivas | null>(null);
  const [cargado, setCargado] = useState(false);
  const [ultima, setUltima] = useState<Optimizacion | null>(null);
  const [version, setVersion] = useState(0);
  const [calculando, setCalculando] = useState(false);
  const [toast, setToast] = useState<{ type: string; msg: string } | null>(null);
  const [conductores, setConductores] = useState<Conductor[]>([]);
  const [formato, setFormato] = useState<FormatoReporte>('csv');
  const [enIncidencia, setEnIncidencia] = useState<Ruta | null>(null);

  useEffect(() => {
    if (!token) return;
    let activo = true;
    rutasApi.activas(token)
      .then((d) => { if (activo) { setDatos(d); setCargado(true); } })
      .catch(() => { if (activo) { setDatos(null); setCargado(true); } });
    return () => { activo = false; };
  }, [token, version]);

  useEffect(() => {
    if (!token || !puedeOperar) return;
    adminApi.conductores(token).then(setConductores).catch(() => {});
  }, [token, puedeOperar]);

  const mostrar = (type: string, msg: string) => {
    setToast({ type, msg });
    setTimeout(() => setToast(null), 4500);
  };

  const optimizar = async () => {
    if (!token) return;
    setCalculando(true);
    try {
      const r = await rutasApi.optimizar(token);
      setUltima(r);
      mostrar('success', `${r.pedidos_planificados} pedidos planificados en ${r.rutas.length} rutas (${Math.round(r.tiempo_ms)} ms)`);
      setVersion((v) => v + 1);
    } catch (err) {
      mostrar('error', err instanceof ApiError ? err.detail : 'Error de conexión');
    } finally {
      setCalculando(false);
    }
  };

  const cancelar = async (ruta: Ruta) => {
    if (!token) return;
    if (!confirm(`¿Desea cancelar la ruta del vehículo ${ruta.placa}? Sus pedidos volverán a PENDIENTE.`)) return;
    try {
      await rutasApi.cancelar(token, ruta.ruta_id);
      mostrar('success', `Ruta del vehículo ${ruta.placa} cancelada`);
      setUltima(null);
      setVersion((v) => v + 1);
    } catch (err) {
      mostrar('error', err instanceof ApiError ? err.detail : 'Error de conexión');
    }
  };

  const accion = async (promesa: Promise<unknown>, exito: string) => {
    try {
      await promesa;
      mostrar('success', exito);
      setVersion((v) => v + 1);
    } catch (err) {
      mostrar('error', err instanceof ApiError ? err.detail : 'Error de conexión');
    }
  };

  const asignar = (r: Ruta, conductorId: string) =>
    token && accion(rutasApi.asignarConductor(token, r.ruta_id, conductorId), `Conductor asignado a la ruta ${r.placa}`);
  const iniciar = (r: Ruta) => token && accion(rutasApi.iniciar(token, r.ruta_id), `Ruta ${r.placa} iniciada`);
  const completar = async (r: Ruta) => {
    if (!token) return;
    try {
      const res = await rutasApi.completar(token, r.ruta_id);
      mostrar('success', res.mensaje);
      setVersion((v) => v + 1);
    } catch (err) {
      mostrar('error', err instanceof ApiError ? err.detail : 'Error de conexión');
    }
  };

  const enviarIncidencia = async (datos: Parameters<typeof rutasApi.incidencia>[2]) => {
    if (!token || !enIncidencia) return;
    try {
      const r = await rutasApi.incidencia(token, enIncidencia.ruta_id, datos);
      mostrar(r.dentro_del_sla ? 'success' : 'error', `${r.sugerencia} (${Math.round(r.tiempo_ms)} ms)`);
      setEnIncidencia(null);
      setVersion((v) => v + 1);
    } catch (err) {
      mostrar('error', err instanceof ApiError ? err.detail : 'Error de conexión');
    }
  };

  const descargar = async (tipo: TipoReporte) => {
    if (!token) return;
    try {
      const blob = await reportesApi.descargar(token, tipo, formato);
      const url = URL.createObjectURL(blob);
      const enlace = document.createElement('a');
      enlace.href = url;
      enlace.download = `${tipo}.${formato}`;
      enlace.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      mostrar('error', err instanceof ApiError ? err.detail : 'No se pudo descargar el reporte');
    }
  };

  const rutas = datos?.rutas ?? [];

  return (
    <>
      {toast && (
        <div className={`toast toast-${toast.type}`} role="status">
          {toast.type === 'success' ? '✓' : '✕'} {toast.msg}
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }} role="group" aria-label="Reportes exportables">
          <select
            className="form-input form-select" style={{ width: 'auto' }} aria-label="Formato del reporte" value={formato}
            onChange={(e) => setFormato(e.target.value as FormatoReporte)}
          >
            {FORMATOS.map((f) => <option key={f.valor} value={f.valor}>{f.etiqueta}</option>)}
          </select>
          {REPORTES.map((r) => (
            <button key={r.tipo} className="btn btn-secondary btn-sm" onClick={() => descargar(r.tipo)}>
              <Download size={14} /> {r.etiqueta} ({FORMATOS.find((f) => f.valor === formato)?.etiqueta})
            </button>
          ))}
        </div>
        {puedeOperar && (
          <button className="btn btn-primary" onClick={optimizar} disabled={calculando} id="btn-optimizar">
            <Play size={18} /> {calculando ? 'Calculando…' : 'Optimizar rutas'}
          </button>
        )}
      </div>

      {ultima && (
        <div className="stats-grid" aria-label="Resultado de la última optimización">
          <div className="stat-card">
            <div className="stat-icon green"><RutaIcono size={24} /></div>
            <div className="stat-info">
              <h4>Rutas planificadas</h4>
              <div className="value">{ultima.rutas.length}</div>
              <div className="change positive">{ultima.pedidos_planificados} pedidos · {ultima.distancia_km.toFixed(1)} km</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon teal"><Leaf size={24} /></div>
            <div className="stat-info">
              <h4>CO₂ evitado</h4>
              <div className="value">{ultima.co2_evitado_kg.toFixed(1)} <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>kg</span></div>
              <div className="change positive">{ultima.ahorro_co2_pct}% menos que sin optimizar</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon green"><TreePine size={24} /></div>
            <div className="stat-info">
              <h4>Compensación equivalente</h4>
              <div className="value">{ultima.arboles_equivalentes}</div>
              <div className="change positive">árboles absorbiendo CO₂ durante un año</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon amber"><Timer size={24} /></div>
            <div className="stat-info">
              <h4>Tiempo de cálculo</h4>
              <div className="value">{Math.round(ultima.tiempo_ms)} <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>ms</span></div>
              <div className="change positive"><Gauge size={12} /> SLA: 45 000 ms · {ultima.algoritmo}</div>
            </div>
          </div>
        </div>
      )}

      {ultima && ultima.sin_asignar.length > 0 && (
        <div className="card" style={{ marginBottom: '1rem' }} role="alert">
          <div className="card-body">
            <h4 style={{ fontWeight: 800, marginBottom: '0.5rem' }}>{ultima.sin_asignar.length} pedido(s) sin asignar</h4>
            <ul style={{ paddingLeft: '1.25rem', fontSize: '0.875rem' }}>
              {ultima.sin_asignar.map((s) => <li key={s.pedido_id}>{s.pedido_id.slice(0, 8)}: {s.motivo}</li>)}
            </ul>
          </div>
        </div>
      )}

      {ultima && ultima.vehiculos_excluidos.length > 0 && (
        <div className="card" style={{ marginBottom: '1rem' }} role="status">
          <div className="card-body">
            <h4 style={{ fontWeight: 800, marginBottom: '0.5rem' }}>{ultima.vehiculos_excluidos.length} vehículo(s) excluido(s) del cálculo</h4>
            <ul style={{ paddingLeft: '1.25rem', fontSize: '0.875rem' }}>
              {ultima.vehiculos_excluidos.map((v) => <li key={v.placa}>{v.placa}: {v.motivo}</li>)}
            </ul>
          </div>
        </div>
      )}

      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div className="card-header"><h3>Mapa de rutas</h3></div>
        <div className="card-body">
          <Mapa datos={datos} />
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '0.5rem' }}>
            El punto negro es el depósito. Cada color es una ruta y los números indican el orden de las paradas; la tabla
            de cada ruta, debajo, contiene la misma información en texto.
          </p>
        </div>
      </div>

      {!cargado ? (
        <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-text-secondary)' }}>Cargando rutas…</div>
      ) : rutas.length === 0 ? (
        <div className="card">
          <div style={{ padding: '3rem', textAlign: 'center' }}>
            <RutaIcono size={48} style={{ color: 'var(--color-text-muted)', marginBottom: '1rem' }} />
            <h4 style={{ fontSize: '1.125rem', fontWeight: 700 }}>Sin rutas planificadas</h4>
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
              {puedeOperar
                ? 'Registre pedidos y pulse «Optimizar rutas» para generar el plan del día.'
                : 'Aún no hay rutas planificadas.'}
            </p>
          </div>
        </div>
      ) : (
        rutas.map((r, i) => (
          <TarjetaRuta
            key={r.ruta_id} ruta={r} color={COLORES[i % COLORES.length]} puedeOperar={puedeOperar} conductores={conductores}
            onCancelar={cancelar} onAsignar={asignar} onIniciar={iniciar} onCompletar={completar} onIncidencia={setEnIncidencia}
          />
        ))
      )}

      {enIncidencia && <IncidenciaModal ruta={enIncidencia} onEnviar={enviarIncidencia} onCerrar={() => setEnIncidencia(null)} />}
    </>
  );
}
