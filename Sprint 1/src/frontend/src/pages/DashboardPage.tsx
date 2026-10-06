/**
 * DashboardPage — Vista principal con estadísticas operativas.
 */

import { useEffect, useState } from 'react';
import { useAuth } from '../AuthContext';
import { vehiculosApi, pedidosApi } from '../api';
import { Truck, Package, Activity, Leaf } from 'lucide-react';

export default function DashboardPage() {
  const { token } = useAuth();
  const [vStats, setVStats] = useState<Record<string, number>>({});
  const [pStats, setPStats] = useState<Record<string, number>>({});

  useEffect(() => {
    if (!token) return;
    vehiculosApi.count(token).then(setVStats).catch(() => {});
    pedidosApi.count(token).then(setPStats).catch(() => {});
  }, [token]);

  return (
    <>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon teal">
            <Truck size={22} />
          </div>
          <div className="stat-info">
            <h4>Vehículos</h4>
            <div className="value">{vStats.TOTAL ?? 0}</div>
            <div className="change positive">
              {vStats.DISPONIBLE ?? 0} disponibles
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon blue">
            <Package size={22} />
          </div>
          <div className="stat-info">
            <h4>Pedidos</h4>
            <div className="value">{pStats.TOTAL ?? 0}</div>
            <div className="change positive">
              {pStats.PENDIENTE ?? 0} pendientes
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon amber">
            <Activity size={22} />
          </div>
          <div className="stat-info">
            <h4>En Mantenimiento</h4>
            <div className="value">{vStats.EN_MANTENIMIENTO ?? 0}</div>
            <div className="change">vehículos</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon green">
            <Leaf size={22} />
          </div>
          <div className="stat-info">
            <h4>Impacto CO₂</h4>
            <div className="value">—</div>
            <div className="change">Sprint 2</div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Resumen del Sprint 1</h3>
        </div>
        <div className="card-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
            <div style={{ padding: '1rem', borderRadius: 'var(--radius-md)', background: 'var(--color-success-bg)', border: '1px solid #bbf7d0' }}>
              <h4 style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#15803d', marginBottom: '0.5rem' }}>✅ US-001 — Gestión de Flota</h4>
              <p style={{ fontSize: '0.8125rem', color: '#166534' }}>
                CRUD de vehículos con validación de placa única, tipos de combustible y estado. 
                Incluye baja lógica (sin eliminación física).
              </p>
            </div>
            <div style={{ padding: '1rem', borderRadius: 'var(--radius-md)', background: 'var(--color-success-bg)', border: '1px solid #bbf7d0' }}>
              <h4 style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#15803d', marginBottom: '0.5rem' }}>✅ US-003 — Registro de Pedidos</h4>
              <p style={{ fontSize: '0.8125rem', color: '#166534' }}>
                Registro de pedidos con dirección, ventana horaria, peso y geolocalización.
                Validación de capacidad vehicular.
              </p>
            </div>
            <div style={{ padding: '1rem', borderRadius: 'var(--radius-md)', background: 'var(--color-success-bg)', border: '1px solid #bbf7d0' }}>
              <h4 style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#15803d', marginBottom: '0.5rem' }}>✅ EN-002 — Autenticación Segura</h4>
              <p style={{ fontSize: '0.8125rem', color: '#166534' }}>
                JWT con bloqueo por intentos fallidos (3 intentos → 15 min lockout).
                RBAC por rol según Documento 08.
              </p>
            </div>
            <div style={{ padding: '1rem', borderRadius: 'var(--radius-md)', background: 'var(--color-success-bg)', border: '1px solid #bbf7d0' }}>
              <h4 style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#15803d', marginBottom: '0.5rem' }}>✅ EN-008 — Cifrado de Datos</h4>
              <p style={{ fontSize: '0.8125rem', color: '#166534' }}>
                Contraseñas hasheadas con bcrypt.
                Datos sensibles cifrados en tránsito (HTTPS/TLS).
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
