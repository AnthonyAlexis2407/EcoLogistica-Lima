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
  ApiError, reportesApi, rutasApi,
  type Optimizacion, type Ruta, type RutasActivas, type TipoReporte,
} from '../api';
import { Route as RutaIcono, Play, Download, Leaf, Gauge, TreePine, Timer, XCircle } from 'lucide-react';

const COLORES = ['#059669', '#2563eb', '#d97706', '#dc2626', '#7c3aed', '#0891b2', '#be185d', '#4d7c0f'];
const LIMA: [number, number] = [-12.0464, -77.0428];

const REPORTES: { tipo: TipoReporte; etiqueta: string }[] = [
  { tipo: 'pedidos', etiqueta: 'Pedidos (CSV)' },
  { tipo: 'rutas', etiqueta: 'Rutas (CSV)' },
  { tipo: 'ambiental', etiqueta: 'Ambiental (CSV)' },
];

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
      const puntos: [number, number][] = ruta.paradas.map((p) => [p.latitud, p.longitud]);
      L.polyline([deposito, ...puntos, deposito], { color, weight: 4, opacity: 0.85 }).addTo(grupo);
      ruta.paradas.forEach((p) => {
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

function TarjetaRuta({
  ruta, color, puedeCancelar, onCancelar,
}: { ruta: Ruta; color: string; puedeCancelar: boolean; onCancelar: (r: Ruta) => void }) {
  return (
    <div className="card" style={{ marginBottom: '1rem' }}>
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
          <span style={{ width: 14, height: 14, borderRadius: '50%', background: color, display: 'inline-block' }} aria-hidden="true" />
          <h3 style={{ fontSize: '1rem' }}>Vehículo {ruta.placa}</h3>
          <span className="badge badge-teal">{ruta.tipo_combustible}</span>
          <span style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
            {ruta.carga_kg.toLocaleString('es-PE')} de {ruta.capacidad_kg.toLocaleString('es-PE')} kg ·
            {' '}{ruta.distancia_km.toFixed(1)} km · {ruta.co2_kg.toFixed(1)} kg CO₂ · {Math.round(ruta.duracion_min)} min
          </span>
        </div>
        {puedeCancelar && (
          <button className="btn btn-ghost btn-sm" onClick={() => onCancelar(ruta)} aria-label={`Cancelar la ruta del vehículo ${ruta.placa}`}>
            <XCircle size={16} /> Cancelar ruta
          </button>
        )}
      </div>
      <div className="table-container">
        <table>
          <thead>
            <tr><th>Parada</th><th>Dirección</th><th>Peso</th><th>Distancia</th><th>Llegada</th><th>Ventana horaria</th></tr>
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

  useEffect(() => {
    if (!token) return;
    let activo = true;
    rutasApi.activas(token)
      .then((d) => { if (activo) { setDatos(d); setCargado(true); } })
      .catch(() => { if (activo) { setDatos(null); setCargado(true); } });
    return () => { activo = false; };
  }, [token, version]);

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

  const descargar = async (tipo: TipoReporte) => {
    if (!token) return;
    try {
      const blob = await reportesApi.descargar(token, tipo);
      const url = URL.createObjectURL(blob);
      const enlace = document.createElement('a');
      enlace.href = url;
      enlace.download = `${tipo}.csv`;
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
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }} role="group" aria-label="Reportes exportables">
          {REPORTES.map((r) => (
            <button key={r.tipo} className="btn btn-secondary btn-sm" onClick={() => descargar(r.tipo)}>
              <Download size={14} /> {r.etiqueta}
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
          <TarjetaRuta key={r.ruta_id} ruta={r} color={COLORES[i % COLORES.length]} puedeCancelar={puedeOperar} onCancelar={cancelar} />
        ))
      )}
    </>
  );
}
