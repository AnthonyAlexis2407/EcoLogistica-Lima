/**
 * DashboardPage — Vista principal: indicadores operativos y ambientales reales (RF-005, RF-010).
 */

import { useEffect, useState } from 'react';
import { useAuth } from '../AuthContext';
import {
  vehiculosApi, pedidosApi, indicadoresApi, reportesApi,
  type FormatoReporte, type Vehiculo, type Pedido, type Indicadores, type TipoReporte,
} from '../api';
import { Truck, Package, Activity, Leaf, ArrowRight, Sparkles, Route as RutaIcono, TreePine, Clock, Fuel, Download } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function DashboardPage() {
  const { token, user } = useAuth();
  const [vStats, setVStats] = useState<Record<string, number>>({});
  const [pStats, setPStats] = useState<Record<string, number>>({});
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([]);
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [indicadores, setIndicadores] = useState<Indicadores | null>(null);
  const [distritos, setDistritos] = useState<string[]>([]);
  const [distrito, setDistrito] = useState('');
  const [desde, setDesde] = useState('');
  const [hasta, setHasta] = useState('');
  const [formato, setFormato] = useState<FormatoReporte>('xlsx');
  // El auditor consulta indicadores y reportes; no ve la gestión de flota ni de pedidos (Documento 08).
  const esAuditor = user?.rol === 'AUDITOR';

  useEffect(() => {
    if (!token) return;
    if (!esAuditor) {
      vehiculosApi.count(token).then(setVStats).catch(() => {});
      pedidosApi.count(token).then(setPStats).catch(() => {});
      vehiculosApi.list(token).then(setVehiculos).catch(() => {});
      pedidosApi.list(token).then(setPedidos).catch(() => {});
    }
    indicadoresApi.distritos(token).then(setDistritos).catch(() => {});
  }, [token, esAuditor]);

  // Los indicadores se recalculan al cambiar el filtro de distrito o de fechas (RF-005).
  useEffect(() => {
    if (!token) return;
    let activo = true;
    indicadoresApi.resumen(token, {
      distrito: distrito || undefined,
      desde: desde ? `${desde}T00:00:00` : undefined,
      hasta: hasta ? `${hasta}T23:59:59` : undefined,
    }).then((r) => { if (activo) setIndicadores(r); }).catch(() => {});
    return () => { activo = false; };
  }, [token, distrito, desde, hasta]);

  const exportar = async (tipo: TipoReporte) => {
    if (!token) return;
    try {
      const blob = await reportesApi.descargar(token, tipo, formato, {
        distrito: distrito || undefined, desde: desde ? `${desde}T00:00:00` : undefined, hasta: hasta ? `${hasta}T23:59:59` : undefined,
      });
      const url = URL.createObjectURL(blob);
      const enlace = document.createElement('a');
      enlace.href = url;
      enlace.download = `${tipo}.${formato}`;
      enlace.click();
      URL.revokeObjectURL(url);
    } catch { /* el detalle del error se ve en la pantalla de rutas */ }
  };

  const capacidadTotalKg = vehiculos.reduce((acc, v) => acc + (Number(v.capacidad_kg) || 0), 0);
  const factorEmisionPromedio = vehiculos.length > 0
    ? (vehiculos.reduce((acc, v) => acc + (Number(v.factor_emision_co2) || 0), 0) / vehiculos.length).toFixed(2)
    : '—';

  const pedidosPendientes = pStats.PENDIENTE ?? 0;
  const pedidosEnRuta = pStats.EN_RUTA ?? 0;
  const pedidosEntregados = pStats.ENTREGADO ?? 0;

  return (
    <>
      {/* Banner Hero Principal — Sprint 2 */}
      <div className="hero-banner">
        <div className="hero-text">
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', background: 'rgba(16, 185, 129, 0.2)', padding: '0.25rem 0.75rem', borderRadius: 'var(--radius-full)', fontSize: '0.75rem', fontWeight: 700, color: '#6ee7b7', marginBottom: '0.75rem' }}>
            <Sparkles size={14} /> Versión final 4.0.0 · Rutas optimizadas y CO₂ evitado
          </div>
          <h3>Bienvenido, {user?.nombre || 'Usuario'}</h3>
          <p>Plataforma de optimización de logística verde y gestión de transporte de última milla para DistriRápido S.A.C.</p>
        </div>
        {/* Ilustración decorativa: AVIF y WebP adaptativos con respaldo PNG (Informe Green IT, optimización 3) */}
        <picture className="hero-ilustracion">
          <source type="image/avif" srcSet="/img/hero-rutas-280.avif 280w, /img/hero-rutas-560.avif 560w" sizes="280px" />
          <source type="image/webp" srcSet="/img/hero-rutas-280.webp 280w, /img/hero-rutas-560.webp 560w" sizes="280px" />
          <img src="/img/hero-rutas-560.png" width="280" height="160" alt="" loading="lazy" decoding="async" />
        </picture>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <Link to="/pedidos" className="btn btn-primary" style={{ background: '#10b981', border: 'none' }}>
            <Package size={16} /> Ver Pedidos
          </Link>
          <Link to="/rutas" className="btn btn-secondary" style={{ background: 'rgba(255,255,255,0.1)', color: 'white', border: '1px solid rgba(255,255,255,0.2)' }}>
            <RutaIcono size={16} /> Ver Rutas
          </Link>
          {/* /docs solo existe en desarrollo: con ENVIRONMENT=production la API lo oculta */}
          {import.meta.env.DEV && (
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="btn btn-secondary" style={{ background: 'rgba(255,255,255,0.1)', color: 'white', border: '1px solid rgba(255,255,255,0.2)' }}>
              Swagger API
            </a>
          )}
        </div>
      </div>

      {/* Métricas KPI */}
      {!esAuditor && (<>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon green">
            <Truck size={24} />
          </div>
          <div className="stat-info">
            <h4>Flota Total</h4>
            <div className="value">{vStats.TOTAL ?? vehiculos.length}</div>
            <div className="change positive">
              ✓ {vStats.DISPONIBLE ?? vehiculos.filter(v => v.estado === 'DISPONIBLE').length} unidades operativas ({capacidadTotalKg.toLocaleString('es-PE')} kg)
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon blue">
            <Package size={24} />
          </div>
          <div className="stat-info">
            <h4>Pedidos Activos</h4>
            <div className="value">{pStats.TOTAL ?? pedidos.length}</div>
            <div className="change positive">
              {pedidosPendientes} pendientes · {pedidosEnRuta} en ruta
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon amber">
            <Activity size={24} />
          </div>
          <div className="stat-info">
            <h4>Entregados / Éxito</h4>
            <div className="value">{pedidosEntregados}</div>
            <div className="change positive">
              {pStats.TOTAL ? `${pedidosEntregados} de ${pStats.TOTAL} pedidos entregados` : 'Sin pedidos registrados'}
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon teal">
            <Leaf size={24} />
          </div>
          <div className="stat-info">
            <h4>Eficiencia CO₂</h4>
            <div className="value">{factorEmisionPromedio} <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>kg/L</span></div>
            <div className="change positive">
              🍃 Promedio de los {vehiculos.length} vehículos registrados
            </div>
          </div>
        </div>
      </div>

      {/* Accesos Rápidos */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
        <Link to="/vehiculos" className="card" style={{ padding: '1.25rem', textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
            <div className="stat-icon green" style={{ width: 44, height: 44, borderRadius: 12 }}>
              <Truck size={20} />
            </div>
            <div>
              <h4 style={{ fontSize: '0.9375rem', fontWeight: 800, color: 'var(--color-secondary)' }}>Gestión de Flota</h4>
              <p style={{ fontSize: '0.775rem', color: 'var(--color-text-secondary)' }}>Catálogo de vehículos y estados</p>
            </div>
          </div>
          <ArrowRight size={18} style={{ color: 'var(--color-text-muted)' }} />
        </Link>

        <Link to="/pedidos" className="card" style={{ padding: '1.25rem', textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
            <div className="stat-icon blue" style={{ width: 44, height: 44, borderRadius: 12 }}>
              <Package size={20} />
            </div>
            <div>
              <h4 style={{ fontSize: '0.9375rem', fontWeight: 800, color: 'var(--color-secondary)' }}>Gestión de Pedidos</h4>
              <p style={{ fontSize: '0.775rem', color: 'var(--color-text-secondary)' }}>Registrar envíos y coordenadas</p>
            </div>
          </div>
          <ArrowRight size={18} style={{ color: 'var(--color-text-muted)' }} />
        </Link>

        <Link to="/rutas" className="card" style={{ padding: '1.25rem', textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
            <div className="stat-icon teal" style={{ width: 44, height: 44, borderRadius: 12 }}>
              <RutaIcono size={20} />
            </div>
            <div>
              <h4 style={{ fontSize: '0.9375rem', fontWeight: 800, color: 'var(--color-secondary)' }}>Rutas Optimizadas</h4>
              <p style={{ fontSize: '0.775rem', color: 'var(--color-text-secondary)' }}>Plan del día, mapa y reportes</p>
            </div>
          </div>
          <ArrowRight size={18} style={{ color: 'var(--color-text-muted)' }} />
        </Link>
      </div>

      </>)}

      {/* Indicadores de rutas y compensación de carbono (RF-005, RF-010): todos salen de la base de datos */}
      <div className="card">
        <div className="card-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <TreePine size={22} style={{ color: 'var(--color-primary)' }} />
            <h3>Rutas y compensación de carbono</h3>
          </div>
          <span className="badge badge-teal">{indicadores?.optimizaciones ?? 0} optimizaciones</span>
        </div>
        <div className="card-body">
          <div className="form-fila" role="group" aria-label="Filtros del dashboard" style={{ marginBottom: '1rem' }}>
            <select className="form-input form-select" aria-label="Filtrar por distrito" value={distrito} onChange={(e) => setDistrito(e.target.value)}>
              <option value="">Todos los distritos</option>
              {distritos.map((d) => <option key={d}>{d}</option>)}
            </select>
            <label style={{ fontSize: '0.8125rem' }}>Desde{' '}
              <input type="date" className="form-input" aria-label="Fecha desde" value={desde} onChange={(e) => setDesde(e.target.value)} />
            </label>
            <label style={{ fontSize: '0.8125rem' }}>Hasta{' '}
              <input type="date" className="form-input" aria-label="Fecha hasta" value={hasta} onChange={(e) => setHasta(e.target.value)} />
            </label>
            <select className="form-input form-select" aria-label="Formato de exportación" value={formato} onChange={(e) => setFormato(e.target.value as FormatoReporte)}>
              <option value="xlsx">Excel</option><option value="pdf">PDF</option><option value="csv">CSV</option>
            </select>
            {(['pedidos', 'rutas', 'ambiental'] as TipoReporte[]).map((tipo) => (
              <button key={tipo} className="btn btn-secondary btn-sm" onClick={() => exportar(tipo)} aria-label={`Exportar reporte de ${tipo}`}>
                <Download size={14} /> {tipo}
              </button>
            ))}
          </div>
          {esAuditor && (
            <p className="form-hint">Los reportes del auditor no incluyen direcciones ni coordenadas (datos personales).</p>
          )}
          {!indicadores || indicadores.optimizaciones === 0 ? (
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
              Aún no hay rutas optimizadas. Registre pedidos y genere el plan del día en <Link to="/rutas">Rutas</Link> para ver el
              CO₂ evitado.
            </p>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
              <div style={{ padding: '1.25rem', borderRadius: 'var(--radius-lg)', background: 'var(--color-primary-bg)', border: '1px solid var(--color-primary-border)' }}>
                <h4 style={{ fontSize: '0.8125rem', fontWeight: 800, marginBottom: '0.35rem' }}>Rutas activas</h4>
                <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>{indicadores.rutas_activas}</div>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                  {indicadores.distancia_planificada_km.toLocaleString('es-PE')} km · {indicadores.co2_planificado_kg.toLocaleString('es-PE')} kg CO₂
                </p>
              </div>
              <div style={{ padding: '1.25rem', borderRadius: 'var(--radius-lg)', background: 'var(--color-teal-bg)', border: '1px solid #99f6e4' }}>
                <h4 style={{ fontSize: '0.8125rem', fontWeight: 800, marginBottom: '0.35rem' }}>CO₂ evitado (acumulado)</h4>
                <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>{indicadores.co2_evitado_kg.toLocaleString('es-PE')} kg</div>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                  {indicadores.ahorro_co2_pct}% menos CO₂ y {indicadores.ahorro_km_pct}% menos km que sin optimizar
                </p>
              </div>
              <div style={{ padding: '1.25rem', borderRadius: 'var(--radius-lg)', background: 'var(--color-blue-bg)', border: '1px solid #bfdbfe' }}>
                <h4 style={{ fontSize: '0.8125rem', fontWeight: 800, marginBottom: '0.35rem' }}>Compensación equivalente</h4>
                <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>{indicadores.arboles_equivalentes.toLocaleString('es-PE')} árboles</div>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>absorbiendo CO₂ durante un año</p>
              </div>
              <div style={{ padding: '1.25rem', borderRadius: 'var(--radius-lg)', background: 'var(--color-primary-bg)', border: '1px solid var(--color-primary-border)' }}>
                <h4 style={{ fontSize: '0.8125rem', fontWeight: 800, marginBottom: '0.35rem' }}>
                  <Fuel size={14} style={{ verticalAlign: 'text-bottom' }} /> Combustible ahorrado
                </h4>
                <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>{(indicadores.combustible_ahorrado_litros ?? 0).toLocaleString('es-PE')} L</div>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>frente a un viaje por pedido</p>
              </div>
              <div style={{ padding: '1.25rem', borderRadius: 'var(--radius-lg)', background: 'var(--color-teal-bg)', border: '1px solid #99f6e4' }}>
                <h4 style={{ fontSize: '0.8125rem', fontWeight: 800, marginBottom: '0.35rem' }}>Compensación confirmada</h4>
                <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>{(indicadores.arboles_compensados ?? 0).toLocaleString('es-PE')} árboles</div>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                  {indicadores.rutas_completadas ?? 0} ruta(s) completada(s) · {(indicadores.co2_compensado_kg ?? 0).toLocaleString('es-PE')} kg CO₂
                </p>
              </div>
              <div style={{ padding: '1.25rem', borderRadius: 'var(--radius-lg)', background: 'var(--color-amber-bg)', border: '1px solid #fde68a' }}>
                <h4 style={{ fontSize: '0.8125rem', fontWeight: 800, marginBottom: '0.35rem' }}>
                  <Clock size={14} style={{ verticalAlign: 'text-bottom' }} /> Entregas dentro de su ventana
                </h4>
                <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>
                  {indicadores.pedidos_en_ventana_pct === null ? '—' : `${indicadores.pedidos_en_ventana_pct}%`}
                </div>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>de las paradas de las rutas activas</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
