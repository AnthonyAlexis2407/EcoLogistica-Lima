/**
 * ConductorPage — app móvil del conductor (PWA): ruta del día, entrega con evidencia en pocos toques (RNF-004),
 * reprogramación, mapa con la ubicación y trabajo sin conexión con sincronización posterior (RNF-010).
 *
 * Entregar una parada son tres toques: «Entregar», una firma (un trazo) y «Confirmar». Cada acción se guarda primero en la
 * cola local con su clave única y después se envía; si no hay red, queda pendiente y se sincroniza sola al volver la señal.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useAuth } from '../AuthContext';
import { ApiError, conductorApi, rutasApi, type ParadaRuta, type Ruta } from '../api';
import {
  INTERVALO_SYNC_MS, encolar, guardarRuta, leerCola, nuevaClave, rutaGuardada, sincronizar,
} from '../offline';
import Modal from '../components/Modal';
import { CheckCircle2, CloudOff, Cloud, Flag, MapPin, Navigation, Play, RefreshCw, Undo2 } from 'lucide-react';

const LIMA: [number, number] = [-12.0464, -77.0428];
const MOTIVOS = ['Cliente ausente', 'Dirección no encontrada', 'Local cerrado', 'Rechazó el pedido'];

function hora(valor: string | null | undefined): string {
  return valor ? new Date(valor).toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' }) : '—';
}

function posicionActual(): Promise<{ lat: number; lng: number } | null> {
  return new Promise((resolver) => {
    if (!('geolocation' in navigator)) return resolver(null);
    navigator.geolocation.getCurrentPosition(
      (p) => resolver({ lat: Number(p.coords.latitude.toFixed(6)), lng: Number(p.coords.longitude.toFixed(6)) }),
      () => resolver(null),
      { timeout: 2000, maximumAge: 60_000 },
    );
  });
}

/** Reduce una foto a un máximo de 640 px y la devuelve como JPEG (la cola local tiene poco espacio). */
function reducirFoto(archivo: File): Promise<string> {
  return new Promise((resolver, rechazar) => {
    const lector = new FileReader();
    lector.onerror = () => rechazar(new Error('No se pudo leer la foto'));
    lector.onload = () => {
      const imagen = new Image();
      imagen.onerror = () => rechazar(new Error('Foto inválida'));
      imagen.onload = () => {
        const escala = Math.min(1, 640 / Math.max(imagen.width, imagen.height));
        const lienzo = document.createElement('canvas');
        lienzo.width = Math.max(1, Math.round(imagen.width * escala));
        lienzo.height = Math.max(1, Math.round(imagen.height * escala));
        lienzo.getContext('2d')?.drawImage(imagen, 0, 0, lienzo.width, lienzo.height);
        resolver(lienzo.toDataURL('image/jpeg', 0.6));
      };
      imagen.src = String(lector.result);
    };
    lector.readAsDataURL(archivo);
  });
}

/** Lienzo para firmar con el dedo (o el mouse). Un solo trazo ya cuenta como firma. */
function PadFirma({ onCambio }: { onCambio: (dataUrl: string | null) => void }) {
  const lienzo = useRef<HTMLCanvasElement | null>(null);
  const dibujando = useRef(false);

  const punto = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const caja = e.currentTarget.getBoundingClientRect();
    return { x: ((e.clientX - caja.left) / caja.width) * e.currentTarget.width, y: ((e.clientY - caja.top) / caja.height) * e.currentTarget.height };
  };

  const empezar = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const ctx = e.currentTarget.getContext('2d');
    if (!ctx) return;
    e.currentTarget.setPointerCapture?.(e.pointerId);
    dibujando.current = true;
    const { x, y } = punto(e);
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#111827';
    ctx.beginPath();
    ctx.moveTo(x, y);
  };
  const mover = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!dibujando.current) return;
    const ctx = e.currentTarget.getContext('2d');
    const { x, y } = punto(e);
    ctx?.lineTo(x, y);
    ctx?.stroke();
  };
  const terminar = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!dibujando.current) return;
    dibujando.current = false;
    onCambio(e.currentTarget.toDataURL('image/png'));
  };
  const borrar = () => {
    const c = lienzo.current;
    c?.getContext('2d')?.clearRect(0, 0, c.width, c.height);
    onCambio(null);
  };

  return (
    <div>
      <canvas
        ref={lienzo} width={320} height={140} className="firma-pad" aria-label="Espacio para la firma del receptor"
        onPointerDown={empezar} onPointerMove={mover} onPointerUp={terminar} onPointerLeave={terminar}
      />
      <button type="button" className="btn btn-ghost btn-sm" onClick={borrar}>Borrar firma</button>
    </div>
  );
}

function MapaConductor({ ruta, posicion }: { ruta: Ruta | null; posicion: [number, number] | null }) {
  const contenedor = useRef<HTMLDivElement | null>(null);
  const mapa = useRef<L.Map | null>(null);
  const capa = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!contenedor.current || mapa.current) return;
    const m = L.map(contenedor.current, { scrollWheelZoom: false }).setView(LIMA, 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© OpenStreetMap' }).addTo(m);
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
    const limites: [number, number][] = [];
    ruta?.paradas.filter((p) => p.estado !== 'RETIRADA').forEach((p) => {
      const hecha = p.estado === 'ENTREGADA' || p.estado === 'REPROGRAMADA';
      L.marker([p.latitud, p.longitud], {
        title: `Parada ${p.orden}: ${p.direccion}`,
        icon: L.divIcon({
          className: 'parada-marcador', iconSize: [26, 26],
          html: `<span style="background:${hecha ? '#6b7280' : '#059669'}">${p.orden}</span>`,
        }),
      }).addTo(grupo);
      limites.push([p.latitud, p.longitud]);
    });
    if (posicion) {
      L.circleMarker(posicion, { radius: 8, color: '#1d4ed8', fillColor: '#3b82f6', fillOpacity: 1 }).addTo(grupo);
      limites.push(posicion);
    }
    if (limites.length > 0) m.fitBounds(L.latLngBounds(limites), { padding: [24, 24], maxZoom: 15 });
  }, [ruta, posicion]);

  return <div ref={contenedor} className="mapa-rutas mapa-conductor" role="region" aria-label="Mapa de mis paradas" />;
}

function EntregaModal({
  parada, onConfirmar, onCerrar,
}: {
  parada: ParadaRuta;
  onConfirmar: (tipo: 'FOTO' | 'FIRMA', evidencia: string) => void;
  onCerrar: () => void;
}) {
  const [firma, setFirma] = useState<string | null>(null);
  const [foto, setFoto] = useState<string | null>(null);
  const [error, setError] = useState('');

  const alElegirFoto = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const archivo = e.target.files?.[0];
    if (!archivo) return;
    try {
      setFoto(await reducirFoto(archivo));
      setError('');
    } catch {
      setError('No se pudo procesar la foto. Intente de nuevo o use la firma.');
    }
  };

  const evidencia = foto ?? firma;
  return (
    <Modal
      titulo="Confirmar entrega" onCerrar={onCerrar} ancho={380}
      pie={(
        <>
          <button type="button" className="btn btn-secondary" onClick={onCerrar}>Volver</button>
          <button
            type="button" className="btn btn-primary conductor-boton" disabled={!evidencia}
            onClick={() => evidencia && onConfirmar(foto ? 'FOTO' : 'FIRMA', evidencia)}
          >
            <CheckCircle2 size={18} /> Confirmar
          </button>
        </>
      )}
    >
      <div className="modal-body">
        <p style={{ fontWeight: 700 }}>{parada.direccion}</p>
        <p className="form-hint">Pida la firma del receptor o tome una foto del paquete entregado.</p>
        {error && <div role="alert" className="form-hint" style={{ color: 'var(--color-danger-text)' }}>{error}</div>}
        <PadFirma onCambio={setFirma} />
        <label className="btn btn-secondary btn-sm" style={{ marginTop: '0.75rem', cursor: 'pointer' }}>
          Tomar foto
          <input type="file" accept="image/*" capture="environment" onChange={alElegirFoto} style={{ display: 'none' }} aria-label="Tomar foto del paquete" />
        </label>
        {foto && <p className="form-hint" role="status">Foto lista como evidencia.</p>}
      </div>
    </Modal>
  );
}

export default function ConductorPage() {
  const { token } = useAuth();
  const [ruta, setRuta] = useState<Ruta | null>(() => rutaGuardada());
  const [cargada, setCargada] = useState(false);
  const [enLinea, setEnLinea] = useState(() => navigator.onLine);
  const [pendientes, setPendientes] = useState(() => leerCola().length);
  const [posicion, setPosicion] = useState<[number, number] | null>(null);
  const [entregando, setEntregando] = useState<ParadaRuta | null>(null);
  const [reprogramando, setReprogramando] = useState<ParadaRuta | null>(null);
  const [motivo, setMotivo] = useState(MOTIVOS[0]);
  const [toast, setToast] = useState<{ type: string; msg: string } | null>(null);
  const sincronizando = useRef(false);

  const mostrar = useCallback((type: string, msg: string) => {
    setToast({ type, msg });
    setTimeout(() => setToast(null), 5000);
  }, []);

  const recargar = useCallback(async () => {
    if (!token) return;
    try {
      const r = await conductorApi.miRuta(token);
      setRuta(r);
      guardarRuta(r);
    } catch (err) {
      // 404: no tiene ruta asignada. Otro error (sin red): se conserva la última ruta descargada.
      if (err instanceof ApiError && err.status === 404) {
        setRuta(null);
        guardarRuta(null);
      }
    } finally {
      setCargada(true);
    }
  }, [token]);

  const sincronizarAhora = useCallback(async () => {
    if (!token || sincronizando.current || leerCola().length === 0) return;
    sincronizando.current = true;
    try {
      const resumen = await sincronizar(token);
      setPendientes(leerCola().length);
      if (resumen.rechazadas.length > 0) {
        mostrar('error', `${resumen.rechazadas.length} acción(es) no se pudieron aplicar: ${resumen.rechazadas[0].detalle}`);
      } else if (resumen.enviadas > 0) {
        mostrar('success', `${resumen.enviadas} acción(es) sincronizada(s)`);
      }
      if (resumen.enviadas > 0 || resumen.rechazadas.length > 0) await recargar();
    } catch {
      /* sin red: la cola se conserva y se reintenta */
    } finally {
      sincronizando.current = false;
    }
  }, [token, recargar, mostrar]);

  useEffect(() => {
    if (!token) return;
    conductorApi.miRuta(token)
      .then((r) => { setRuta(r); guardarRuta(r); })
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) { setRuta(null); guardarRuta(null); }
      })
      .finally(() => setCargada(true));
  }, [token]);

  // Sincronización automática: al volver la red y cada 30 s mientras haya acciones pendientes.
  useEffect(() => {
    const alVolver = () => { setEnLinea(true); void sincronizarAhora(); };
    const alPerder = () => setEnLinea(false);
    window.addEventListener('online', alVolver);
    window.addEventListener('offline', alPerder);
    const id = setInterval(() => void sincronizarAhora(), INTERVALO_SYNC_MS);
    const inicial = setTimeout(() => void sincronizarAhora(), 500);
    return () => {
      window.removeEventListener('online', alVolver);
      window.removeEventListener('offline', alPerder);
      clearInterval(id);
      clearTimeout(inicial);
    };
  }, [sincronizarAhora]);

  // Seguimiento de ubicación (RF-004): cada minuto se compara con el trazado; un desvío de más de 500 m recalcula la ruta.
  const enCurso = ruta?.estado === 'EN_CURSO';
  useEffect(() => {
    if (!token || !enCurso) return;
    const medir = async () => {
      const p = await posicionActual();
      if (!p) return;
      setPosicion([p.lat, p.lng]);
      if (!navigator.onLine) return;
      try {
        const r = await conductorApi.ubicacion(token, p.lat, p.lng);
        if (r.desviado) {
          mostrar('error', r.mensaje);
          await recargar();
        }
      } catch {
        /* sin red: se mide de nuevo en el siguiente intervalo */
      }
    };
    void medir();
    const id = setInterval(() => void medir(), 60_000);
    return () => clearInterval(id);
  }, [token, enCurso, mostrar, recargar]);

  const aplicarLocal = (paradaId: string, estado: string, extra: Partial<ParadaRuta> = {}) => {
    setRuta((actual) => {
      if (!actual) return actual;
      const nueva = {
        ...actual,
        paradas: actual.paradas.map((p) => (p.parada_id === paradaId ? { ...p, estado, ...extra } : p)),
      };
      guardarRuta(nueva);
      return nueva;
    });
  };

  const confirmarEntrega = async (tipo: 'FOTO' | 'FIRMA', evidencia: string) => {
    const parada = entregando;
    if (!parada?.parada_id) return;
    setEntregando(null);
    // Se usa la última posición medida; si todavía no hay ninguna, se pide una con un plazo corto para no demorar la entrega.
    const p = posicion ? { lat: posicion[0], lng: posicion[1] } : await posicionActual();
    const ok = encolar({
      tipo: 'ENTREGA', parada_id: parada.parada_id, clave_sync: nuevaClave(), evidencia_tipo: tipo, evidencia,
      latitud: p?.lat, longitud: p?.lng, momento: new Date().toISOString(),
    });
    if (!ok) {
      mostrar('error', 'No hay espacio para guardar la entrega en el dispositivo. Libere espacio e intente de nuevo.');
      return;
    }
    aplicarLocal(parada.parada_id, 'ENTREGADA', { entregada_en: new Date().toISOString() });
    setPendientes(leerCola().length);
    mostrar('success', navigator.onLine ? 'Entrega registrada' : 'Entrega guardada: se enviará al recuperar la señal');
    void sincronizarAhora();
  };

  const confirmarReprogramacion = () => {
    const parada = reprogramando;
    if (!parada?.parada_id) return;
    setReprogramando(null);
    encolar({
      tipo: 'REPROGRAMACION', parada_id: parada.parada_id, clave_sync: nuevaClave(), motivo, momento: new Date().toISOString(),
    });
    aplicarLocal(parada.parada_id, 'REPROGRAMADA', { motivo });
    setPendientes(leerCola().length);
    mostrar('success', 'Parada reprogramada');
    void sincronizarAhora();
  };

  const iniciar = async () => {
    if (!token || !ruta) return;
    try {
      const r = await rutasApi.iniciar(token, ruta.ruta_id);
      setRuta(r);
      guardarRuta(r);
      mostrar('success', 'Ruta iniciada. ¡Buen viaje!');
    } catch (err) {
      mostrar('error', err instanceof ApiError ? err.detail : 'No se pudo iniciar: revise su conexión');
    }
  };

  const completar = async () => {
    if (!token || !ruta) return;
    try {
      await sincronizarAhora();
      const r = await rutasApi.completar(token, ruta.ruta_id);
      mostrar('success', r.mensaje);
      setRuta(null);
      guardarRuta(null);
    } catch (err) {
      mostrar('error', err instanceof ApiError ? err.detail : 'No se pudo cerrar: revise su conexión');
    }
  };

  const paradas = (ruta?.paradas ?? []).filter((p) => p.estado !== 'RETIRADA');
  const resueltas = paradas.filter((p) => p.estado === 'ENTREGADA' || p.estado === 'REPROGRAMADA').length;
  const todoResuelto = paradas.length > 0 && resueltas === paradas.length;

  return (
    <div className="conductor-pagina">
      {toast && <div className={`toast toast-${toast.type}`} role="status">{toast.type === 'success' ? '✓' : '✕'} {toast.msg}</div>}

      <div className="conductor-estado" role="status">
        <span className={`badge ${enLinea ? 'badge-green' : 'badge-amber'}`}>
          {enLinea ? <><Cloud size={12} /> En línea</> : <><CloudOff size={12} /> Sin conexión</>}
        </span>
        {pendientes > 0 && (
          <span className="badge badge-blue" id="pendientes-sync">
            {pendientes} acción(es) pendiente(s) de sincronizar
          </span>
        )}
        {pendientes > 0 && enLinea && (
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => void sincronizarAhora()}>
            <RefreshCw size={14} /> Sincronizar ahora
          </button>
        )}
      </div>

      {!cargada && !ruta ? (
        <div className="loading-spinner"><div className="spinner" /></div>
      ) : !ruta ? (
        <div className="card"><div style={{ padding: '2rem', textAlign: 'center' }}>
          <Navigation size={44} style={{ color: 'var(--color-text-muted)' }} />
          <h4 style={{ fontSize: '1.125rem', fontWeight: 700, marginTop: '0.75rem' }}>Sin ruta asignada</h4>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Cuando el operador le asigne una ruta aparecerá aquí.</p>
        </div></div>
      ) : (
        <>
          <div className="card" style={{ marginBottom: '1rem' }}>
            <div className="card-body">
              <h3 style={{ fontSize: '1.0625rem' }}>Vehículo {ruta.placa}</h3>
              <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                {ruta.estado === 'EN_CURSO' ? 'En curso' : 'Lista para salir'} · {resueltas} de {paradas.length} paradas ·{' '}
                {ruta.distancia_km.toFixed(1)} km
              </p>
              {ruta.estado === 'PLANIFICADA' && (
                <button className="btn btn-primary conductor-boton" onClick={iniciar} disabled={!enLinea} id="btn-iniciar-ruta">
                  <Play size={20} /> Iniciar ruta
                </button>
              )}
              {ruta.estado === 'EN_CURSO' && todoResuelto && (
                <button className="btn btn-primary conductor-boton" onClick={completar} disabled={!enLinea} id="btn-completar-ruta">
                  <Flag size={20} /> Terminar ruta
                </button>
              )}
            </div>
          </div>

          <MapaConductor ruta={ruta} posicion={posicion} />

          <ol className="conductor-paradas" aria-label="Paradas de la ruta">
            {paradas.map((p) => (
              <li key={p.parada_id ?? p.pedido_id} className={`card conductor-parada ${p.estado !== 'PENDIENTE' ? 'hecha' : ''}`}>
                <div className="card-body">
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: '0.5rem' }}>
                    <strong><MapPin size={14} /> {p.orden}. {p.direccion}</strong>
                    <span className={`badge ${p.estado === 'ENTREGADA' ? 'badge-green' : p.estado === 'REPROGRAMADA' ? 'badge-amber' : 'badge-blue'}`}>
                      {p.estado === 'ENTREGADA' ? 'Entregada' : p.estado === 'REPROGRAMADA' ? 'Reprogramada' : 'Pendiente'}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                    Llegada estimada {hora(p.llegada_estimada)} · {p.peso_kg.toLocaleString('es-PE')} kg
                    {p.ventana_fin ? ` · hasta las ${hora(p.ventana_fin)}` : ''}
                  </p>
                  {ruta.estado === 'EN_CURSO' && p.estado === 'PENDIENTE' && (
                    <div className="conductor-acciones">
                      <button className="btn btn-primary conductor-boton" onClick={() => setEntregando(p)} aria-label={`Entregar parada ${p.orden}`}>
                        <CheckCircle2 size={20} /> Entregar
                      </button>
                      <button className="btn btn-secondary" onClick={() => setReprogramando(p)} aria-label={`No pude entregar la parada ${p.orden}`}>
                        <Undo2 size={16} /> No pude entregar
                      </button>
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ol>
        </>
      )}

      {entregando && <EntregaModal parada={entregando} onConfirmar={confirmarEntrega} onCerrar={() => setEntregando(null)} />}

      {reprogramando && (
        <Modal
          titulo="Reprogramar parada" onCerrar={() => setReprogramando(null)} ancho={380}
          pie={(
            <>
              <button type="button" className="btn btn-secondary" onClick={() => setReprogramando(null)}>Volver</button>
              <button type="button" className="btn btn-primary" onClick={confirmarReprogramacion}>Reprogramar</button>
            </>
          )}
        >
          <div className="modal-body">
            <p style={{ fontWeight: 700 }}>{reprogramando.direccion}</p>
            <div className="form-group">
              <label className="form-label" htmlFor="motivo-reprogramacion">Motivo</label>
              <select id="motivo-reprogramacion" className="form-input form-select" value={motivo} onChange={(e) => setMotivo(e.target.value)}>
                {MOTIVOS.map((m) => <option key={m}>{m}</option>)}
              </select>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
