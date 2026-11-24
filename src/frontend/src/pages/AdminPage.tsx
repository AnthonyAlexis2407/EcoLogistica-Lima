/**
 * AdminPage — administración (solo ADMIN_FLOTA): usuarios, conductores, parámetros del algoritmo, zonas protegidas
 * (RN-003) y solicitudes de privacidad (RN-008). La eliminación física y la anonimización piden confirmación.
 */

import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { useAuth } from '../AuthContext';
import {
  adminApi, authApi, ApiError,
  type Conductor, type Parametros, type SolicitudPrivacidad, type Usuario, type Zona,
} from '../api';

type Pestana = 'usuarios' | 'conductores' | 'parametros' | 'zonas' | 'privacidad';

const PESTANAS: { id: Pestana; etiqueta: string }[] = [
  { id: 'usuarios', etiqueta: 'Usuarios' },
  { id: 'conductores', etiqueta: 'Conductores' },
  { id: 'parametros', etiqueta: 'Parámetros del algoritmo' },
  { id: 'zonas', etiqueta: 'Zonas protegidas' },
  { id: 'privacidad', etiqueta: 'Privacidad' },
];

const ROLES = ['ADMIN_FLOTA', 'OPERADOR', 'CONDUCTOR', 'BODEGA', 'AUDITOR'];
const CANALES = ['PORTAL', 'EMAIL', 'SMS', 'NINGUNO'];

function mensajeDe(err: unknown): string {
  return err instanceof ApiError ? err.detail : 'Error de conexión';
}

export default function AdminPage() {
  const { token, user } = useAuth();
  const [pestana, setPestana] = useState<Pestana>('usuarios');
  const [aviso, setAviso] = useState<{ tipo: 'ok' | 'error'; texto: string } | null>(null);

  const avisar = useCallback((tipo: 'ok' | 'error', texto: string) => {
    setAviso({ tipo, texto });
    setTimeout(() => setAviso(null), 5000);
  }, []);

  if (!token) return null;
  return (
    <>
      {aviso && (
        <div className={`toast toast-${aviso.tipo === 'ok' ? 'success' : 'error'}`} role="status">
          {aviso.tipo === 'ok' ? '✓' : '✕'} {aviso.texto}
        </div>
      )}
      <div role="tablist" aria-label="Secciones de administración" className="pestanas">
        {PESTANAS.map((p) => (
          <button
            key={p.id} role="tab" id={`tab-${p.id}`} aria-selected={pestana === p.id} aria-controls={`panel-${p.id}`}
            className={`btn btn-sm ${pestana === p.id ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setPestana(p.id)}
          >
            {p.etiqueta}
          </button>
        ))}
      </div>
      <div role="tabpanel" id={`panel-${pestana}`} aria-labelledby={`tab-${pestana}`} className="card" style={{ marginTop: '1rem' }}>
        <div className="card-body">
          {pestana === 'usuarios' && <SeccionUsuarios token={token} yo={user?.usuario_id ?? ''} avisar={avisar} />}
          {pestana === 'conductores' && <SeccionConductores token={token} avisar={avisar} />}
          {pestana === 'parametros' && <SeccionParametros token={token} avisar={avisar} />}
          {pestana === 'zonas' && <SeccionZonas token={token} avisar={avisar} />}
          {pestana === 'privacidad' && <SeccionPrivacidad token={token} yo={user?.usuario_id ?? ''} avisar={avisar} />}
        </div>
      </div>
    </>
  );
}

type Props = { token: string; avisar: (t: 'ok' | 'error', s: string) => void };

function SeccionUsuarios({ token, yo, avisar }: Props & { yo: string }) {
  const [lista, setLista] = useState<Usuario[]>([]);
  const [version, setVersion] = useState(0);
  const [nuevo, setNuevo] = useState({ nombre: '', email: '', password: '', rol: 'OPERADOR' });

  useEffect(() => {
    let activo = true;
    adminApi.usuarios(token).then((u) => { if (activo) setLista(u); }).catch(() => {});
    return () => { activo = false; };
  }, [token, version]);

  const crear = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await authApi.register(nuevo);
      avisar('ok', 'Usuario creado');
      setNuevo({ nombre: '', email: '', password: '', rol: 'OPERADOR' });
      setVersion((v) => v + 1);
    } catch (err) { avisar('error', mensajeDe(err)); }
  };

  const cambiar = async (u: Usuario, datos: Partial<{ rol: string; canal_notificacion: string }>) => {
    try {
      await adminApi.actualizarUsuario(token, u.usuario_id, datos);
      setVersion((v) => v + 1);
    } catch (err) { avisar('error', mensajeDe(err)); }
  };

  const eliminar = async (u: Usuario) => {
    if (!confirm(`¿Eliminar definitivamente la cuenta ${u.email}? No se puede deshacer.`)) return;
    try {
      await adminApi.eliminarUsuario(token, u.usuario_id);
      avisar('ok', 'Usuario eliminado');
      setVersion((v) => v + 1);
    } catch (err) { avisar('error', mensajeDe(err)); }
  };

  return (
    <>
      <form onSubmit={crear} className="form-fila" aria-label="Crear usuario">
        <input className="form-input" aria-label="Nombre" placeholder="Nombre" value={nuevo.nombre} required minLength={2}
          onChange={(e) => setNuevo({ ...nuevo, nombre: e.target.value })} />
        <input className="form-input" aria-label="Correo" type="email" placeholder="Correo" value={nuevo.email} required
          onChange={(e) => setNuevo({ ...nuevo, email: e.target.value })} />
        <input className="form-input" aria-label="Contraseña" type="password" placeholder="Contraseña (8+)" value={nuevo.password}
          required minLength={8} onChange={(e) => setNuevo({ ...nuevo, password: e.target.value })} />
        <select className="form-input form-select" aria-label="Rol del nuevo usuario" value={nuevo.rol}
          onChange={(e) => setNuevo({ ...nuevo, rol: e.target.value })}>
          {ROLES.map((r) => <option key={r}>{r}</option>)}
        </select>
        <button className="btn btn-primary btn-sm" type="submit">Crear usuario</button>
      </form>
      <div className="table-container">
        <table>
          <thead><tr><th>Nombre</th><th>Correo</th><th>Rol</th><th>Canal de aviso</th><th>Estado</th><th>Acciones</th></tr></thead>
          <tbody>
            {lista.map((u) => (
              <tr key={u.usuario_id}>
                <td>{u.nombre}</td>
                <td>{u.email}</td>
                <td>
                  <select className="form-input form-select" aria-label={`Rol de ${u.email}`} value={u.rol} disabled={u.usuario_id === yo}
                    onChange={(e) => cambiar(u, { rol: e.target.value })}>
                    {ROLES.map((r) => <option key={r}>{r}</option>)}
                  </select>
                </td>
                <td>
                  <select className="form-input form-select" aria-label={`Canal de ${u.email}`} value={u.canal_notificacion ?? 'PORTAL'}
                    onChange={(e) => cambiar(u, { canal_notificacion: e.target.value })}>
                    {CANALES.map((c) => <option key={c}>{c}</option>)}
                  </select>
                </td>
                <td><span className={`badge ${u.estado === 'ACTIVO' ? 'badge-green' : 'badge-gray'}`}>{u.estado}</span></td>
                <td>
                  {u.usuario_id !== yo && u.estado === 'ACTIVO' && (
                    <button className="btn btn-ghost btn-sm" style={{ color: 'var(--color-danger)' }} onClick={() => eliminar(u)}
                      aria-label={`Eliminar a ${u.email}`}>Eliminar</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

function SeccionConductores({ token, avisar }: Props) {
  const [lista, setLista] = useState<Conductor[]>([]);
  const [version, setVersion] = useState(0);
  const [nuevo, setNuevo] = useState({ nombre: '', email: '', password: '', licencia: '', telefono: '' });

  useEffect(() => {
    let activo = true;
    adminApi.conductores(token).then((c) => { if (activo) setLista(c); }).catch(() => {});
    return () => { activo = false; };
  }, [token, version]);

  const crear = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await adminApi.crearConductor(token, { ...nuevo, telefono: nuevo.telefono || undefined });
      avisar('ok', 'Conductor registrado');
      setNuevo({ nombre: '', email: '', password: '', licencia: '', telefono: '' });
      setVersion((v) => v + 1);
    } catch (err) { avisar('error', mensajeDe(err)); }
  };

  const alternar = async (c: Conductor) => {
    try {
      await adminApi.actualizarConductor(token, c.conductor_id, { activo: !c.activo });
      setVersion((v) => v + 1);
    } catch (err) { avisar('error', mensajeDe(err)); }
  };

  return (
    <>
      <form onSubmit={crear} className="form-fila" aria-label="Registrar conductor">
        <input className="form-input" aria-label="Nombre del conductor" placeholder="Nombre" value={nuevo.nombre} required minLength={2}
          onChange={(e) => setNuevo({ ...nuevo, nombre: e.target.value })} />
        <input className="form-input" aria-label="Correo del conductor" type="email" placeholder="Correo" value={nuevo.email} required
          onChange={(e) => setNuevo({ ...nuevo, email: e.target.value })} />
        <input className="form-input" aria-label="Contraseña del conductor" type="password" placeholder="Contraseña (8+)" value={nuevo.password}
          required minLength={8} onChange={(e) => setNuevo({ ...nuevo, password: e.target.value })} />
        <input className="form-input" aria-label="Licencia" placeholder="Licencia" value={nuevo.licencia} required minLength={5}
          onChange={(e) => setNuevo({ ...nuevo, licencia: e.target.value })} />
        <input className="form-input" aria-label="Teléfono" placeholder="Teléfono" value={nuevo.telefono}
          onChange={(e) => setNuevo({ ...nuevo, telefono: e.target.value })} />
        <button className="btn btn-primary btn-sm" type="submit">Registrar conductor</button>
      </form>
      <div className="table-container">
        <table>
          <thead><tr><th>Nombre</th><th>Correo</th><th>Licencia</th><th>Teléfono</th><th>Estado</th><th>Acciones</th></tr></thead>
          <tbody>
            {lista.map((c) => (
              <tr key={c.conductor_id}>
                <td>{c.nombre}</td><td>{c.email}</td><td>{c.licencia}</td><td>{c.telefono ?? '—'}</td>
                <td><span className={`badge ${c.activo ? 'badge-green' : 'badge-gray'}`}>{c.activo ? 'Activo' : 'Inactivo'}</span></td>
                <td>
                  <button className="btn btn-ghost btn-sm" onClick={() => alternar(c)} aria-label={`${c.activo ? 'Desactivar' : 'Activar'} a ${c.nombre}`}>
                    {c.activo ? 'Desactivar' : 'Activar'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

function SeccionParametros({ token, avisar }: Props) {
  const [valores, setValores] = useState<Parametros | null>(null);

  useEffect(() => {
    let activo = true;
    adminApi.parametros(token).then((p) => { if (activo) setValores(p); }).catch(() => {});
    return () => { activo = false; };
  }, [token]);

  if (!valores) return <p>Cargando parámetros…</p>;

  const guardar = async (e: FormEvent) => {
    e.preventDefault();
    try {
      setValores(await adminApi.guardarParametros(token, valores));
      avisar('ok', 'Parámetros guardados; se aplican desde la próxima optimización');
    } catch (err) { avisar('error', mensajeDe(err)); }
  };

  const campo = (clave: keyof Parametros, etiqueta: string, ayuda: string, min: number, max: number) => (
    <div className="form-group">
      <label className="form-label" htmlFor={`p-${clave}`}>{etiqueta}</label>
      <input id={`p-${clave}`} className="form-input" type="number" min={min} max={max} step="0.5" value={valores[clave]} required
        onChange={(e) => setValores({ ...valores, [clave]: Number(e.target.value) })} aria-describedby={`ayuda-${clave}`} />
      <p id={`ayuda-${clave}`} className="form-hint">{ayuda}</p>
    </div>
  );

  return (
    <form onSubmit={guardar} style={{ maxWidth: 460 }}>
      {campo('velocidad_kmh', 'Velocidad media (km/h)', 'Velocidad urbana supuesta para estimar los tiempos de viaje (5 a 80).', 5, 80)}
      {campo('servicio_min', 'Tiempo de descarga por parada (min)', 'Minutos que se reservan en cada entrega (0 a 60).', 0, 60)}
      {campo('limite_segundos', 'Límite de cálculo (s)', 'Tiempo máximo del optimizador; el acuerdo de servicio es de 45 s (1 a 45).', 1, 45)}
      <button className="btn btn-primary" type="submit">Guardar parámetros</button>
    </form>
  );
}

function SeccionZonas({ token, avisar }: Props) {
  const [lista, setLista] = useState<Zona[]>([]);
  const [version, setVersion] = useState(0);
  const [nueva, setNueva] = useState({ nombre: '', latitud: -12.0464, longitud: -77.0428, radio_km: 1 });

  useEffect(() => {
    let activo = true;
    adminApi.zonas(token).then((z) => { if (activo) setLista(z); }).catch(() => {});
    return () => { activo = false; };
  }, [token, version]);

  const crear = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await adminApi.crearZona(token, nueva);
      avisar('ok', 'Zona protegida registrada');
      setVersion((v) => v + 1);
    } catch (err) { avisar('error', mensajeDe(err)); }
  };

  const eliminar = async (z: Zona) => {
    if (!confirm(`¿Eliminar la zona «${z.nombre}»?`)) return;
    try {
      await adminApi.eliminarZona(token, z.zona_id);
      setVersion((v) => v + 1);
    } catch (err) { avisar('error', mensajeDe(err)); }
  };

  return (
    <>
      <p className="form-hint">
        Ninguna ruta atraviesa una zona protegida: el optimizador la rodea y no asigna destinos dentro de ella (RN-003).
      </p>
      <form onSubmit={crear} className="form-fila" aria-label="Registrar zona protegida">
        <input className="form-input" aria-label="Nombre de la zona" placeholder="Nombre" value={nueva.nombre} required minLength={3}
          onChange={(e) => setNueva({ ...nueva, nombre: e.target.value })} />
        <input className="form-input" aria-label="Latitud de la zona" type="number" step="0.0001" value={nueva.latitud} required
          onChange={(e) => setNueva({ ...nueva, latitud: Number(e.target.value) })} />
        <input className="form-input" aria-label="Longitud de la zona" type="number" step="0.0001" value={nueva.longitud} required
          onChange={(e) => setNueva({ ...nueva, longitud: Number(e.target.value) })} />
        <input className="form-input" aria-label="Radio en kilómetros" type="number" step="0.1" min={0.1} max={30} value={nueva.radio_km} required
          onChange={(e) => setNueva({ ...nueva, radio_km: Number(e.target.value) })} />
        <button className="btn btn-primary btn-sm" type="submit">Registrar zona</button>
      </form>
      <div className="table-container">
        <table>
          <thead><tr><th>Nombre</th><th>Centro</th><th>Radio</th><th>Acciones</th></tr></thead>
          <tbody>
            {lista.map((z) => (
              <tr key={z.zona_id}>
                <td>{z.nombre}</td><td>{Number(z.latitud).toFixed(4)}, {Number(z.longitud).toFixed(4)}</td><td>{z.radio_km} km</td>
                <td><button className="btn btn-ghost btn-sm" style={{ color: 'var(--color-danger)' }} onClick={() => eliminar(z)}
                  aria-label={`Eliminar la zona ${z.nombre}`}>Eliminar</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

function SeccionPrivacidad({ token, yo, avisar }: Props & { yo: string }) {
  const [lista, setLista] = useState<SolicitudPrivacidad[]>([]);
  const [version, setVersion] = useState(0);

  useEffect(() => {
    let activo = true;
    adminApi.solicitudes(token).then((s) => { if (activo) setLista(s); }).catch(() => {});
    return () => { activo = false; };
  }, [token, version]);

  const atender = async (s: SolicitudPrivacidad) => {
    if (!confirm('Se anonimizarán los datos personales del titular y su cuenta quedará cerrada. ¿Continuar?')) return;
    try {
      await adminApi.atenderSolicitud(token, s.solicitud_id);
      avisar('ok', 'Solicitud atendida: datos anonimizados');
      setVersion((v) => v + 1);
    } catch (err) { avisar('error', mensajeDe(err)); }
  };

  return (
    <>
      <p className="form-hint">Las solicitudes deben atenderse en un máximo de 5 días hábiles (Ley N.° 29733).</p>
      <div className="table-container">
        <table>
          <thead><tr><th>Solicitada</th><th>Plazo límite</th><th>Estado</th><th>Acciones</th></tr></thead>
          <tbody>
            {lista.length === 0 && <tr><td colSpan={4}>No hay solicitudes.</td></tr>}
            {lista.map((s) => (
              <tr key={s.solicitud_id}>
                <td>{new Date(s.solicitada_en).toLocaleDateString('es-PE')}</td>
                <td>{new Date(s.plazo_limite).toLocaleDateString('es-PE')}</td>
                <td><span className={`badge ${s.estado === 'ATENDIDA' ? 'badge-green' : 'badge-amber'}`}>{s.estado}</span></td>
                <td>
                  {s.estado === 'PENDIENTE' && s.usuario_id !== yo && (
                    <button className="btn btn-secondary btn-sm" onClick={() => atender(s)}>Anonimizar datos</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
