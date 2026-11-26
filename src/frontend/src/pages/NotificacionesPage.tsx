/**
 * NotificacionesPage — portal de avisos para clientes (RF-009). Cada usuario ve solo los avisos de su cuenta (RN-010).
 * Operadores y administradores ven además los avisos pendientes de contacto (clientes sin canal de notificación).
 */

import { useEffect, useState } from 'react';
import { useAuth } from '../AuthContext';
import { notificacionesApi, privacidadApi, ApiError, type Notificacion } from '../api';
import { Bell, BellRing, PhoneCall, ShieldCheck } from 'lucide-react';

const ETIQUETAS: Record<string, string> = {
  ASIGNACION: 'Pedido asignado',
  EN_RUTA: 'En camino',
  RETRASO: 'Retraso',
  ENTREGA: 'Entregado',
  REPROGRAMACION: 'Reprogramado',
  INCIDENCIA: 'Incidencia',
};

const COLORES: Record<string, string> = {
  ASIGNACION: 'badge-blue', EN_RUTA: 'badge-teal', RETRASO: 'badge-amber', ENTREGA: 'badge-green',
  REPROGRAMACION: 'badge-amber', INCIDENCIA: 'badge-red',
};

function fechaHora(valor: string): string {
  return new Date(valor).toLocaleString('es-PE', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
}

export default function NotificacionesPage() {
  const { token, user } = useAuth();
  const esPersonal = user?.rol === 'ADMIN_FLOTA' || user?.rol === 'OPERADOR';
  const [items, setItems] = useState<Notificacion[] | null>(null);
  const [noLeidas, setNoLeidas] = useState(0);
  const [sinCanal, setSinCanal] = useState<Notificacion[]>([]);
  const [version, setVersion] = useState(0);
  const [mensaje, setMensaje] = useState('');

  useEffect(() => {
    if (!token) return;
    let activo = true;
    notificacionesApi.mias(token)
      .then((r) => { if (activo) { setItems(r.items); setNoLeidas(r.noLeidas); } })
      .catch(() => { if (activo) setItems([]); });
    if (esPersonal) {
      notificacionesApi.pendientesDeContacto(token).then((r) => { if (activo) setSinCanal(r); }).catch(() => {});
    }
    return () => { activo = false; };
  }, [token, esPersonal, version]);

  const marcar = async (n: Notificacion) => {
    if (!token || n.leida) return;
    await notificacionesApi.marcarLeida(token, n.notificacion_id).catch(() => {});
    setVersion((v) => v + 1);
  };

  const solicitarBaja = async () => {
    if (!token) return;
    if (!confirm('¿Solicitar la eliminación o anonimización de sus datos personales? Se atenderá en un máximo de 5 días hábiles.')) return;
    try {
      const s = await privacidadApi.solicitarBaja(token);
      setMensaje(`Solicitud registrada. Se atenderá antes del ${new Date(s.plazo_limite).toLocaleDateString('es-PE')}.`);
    } catch (err) {
      setMensaje(err instanceof ApiError ? err.detail : 'No se pudo registrar la solicitud');
    }
  };

  return (
    <>
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div className="card-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            {noLeidas > 0 ? <BellRing size={22} style={{ color: 'var(--color-primary)' }} /> : <Bell size={22} />}
            <h3>Mis notificaciones</h3>
          </div>
          <span className="badge badge-teal" aria-live="polite">{noLeidas} sin leer</span>
        </div>
        <div className="card-body">
          {items === null ? (
            <p>Cargando avisos…</p>
          ) : items.length === 0 ? (
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
              Aún no tiene avisos. Recibirá uno cuando su pedido sea asignado, salga en ruta, se retrase o se entregue.
            </p>
          ) : (
            <ul className="lista-avisos" aria-label="Avisos recibidos">
              {items.map((n) => (
                <li key={n.notificacion_id} className={n.leida ? 'leida' : 'nueva'}>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
                    <span className={`badge ${COLORES[n.tipo] ?? 'badge-gray'}`}>{ETIQUETAS[n.tipo] ?? n.tipo}</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{fechaHora(n.creado_en)} · {n.canal}</span>
                    {n.estado_envio === 'NO_ENTREGADA' && <span className="badge badge-red">No enviada</span>}
                  </div>
                  <p style={{ margin: '0.35rem 0', fontSize: '0.9375rem' }}>{n.mensaje}</p>
                  {n.hora_estimada && (
                    <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                      Hora estimada: {new Date(n.hora_estimada).toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  )}
                  {!n.leida && (
                    <button className="btn btn-ghost btn-sm" onClick={() => marcar(n)}>Marcar como leída</button>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {esPersonal && (
        <div className="card" style={{ marginBottom: '1.25rem' }}>
          <div className="card-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <PhoneCall size={20} /> <h3>Clientes pendientes de contacto</h3>
            </div>
            <span className="badge badge-amber">{sinCanal.length}</span>
          </div>
          <div className="card-body">
            {sinCanal.length === 0 ? (
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Todos los avisos pudieron enviarse.</p>
            ) : (
              <ul style={{ paddingLeft: '1.25rem', fontSize: '0.875rem' }}>
                {sinCanal.map((n) => <li key={n.notificacion_id}>{fechaHora(n.creado_en)}: {n.mensaje}</li>)}
              </ul>
            )}
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-header"><div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center' }}><ShieldCheck size={20} /><h3>Mis datos personales</h3></div></div>
        <div className="card-body">
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
            Sus datos se guardan cifrados. Conforme a la Ley N.° 29733 puede pedir su eliminación o anonimización; la
            atendemos en un máximo de 5 días hábiles.
          </p>
          <button className="btn btn-secondary btn-sm" onClick={solicitarBaja} id="btn-solicitar-baja">Solicitar eliminación de mis datos</button>
          {mensaje && <p role="status" style={{ marginTop: '0.75rem', fontSize: '0.875rem' }}>{mensaje}</p>}
        </div>
      </div>
    </>
  );
}
