/**
 * App — Componente raíz con routing y layout (sidebar + topbar).
 */

import { lazy, Suspense, useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, NavLink, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import { healthApi, notificacionesApi } from './api';
import LoginPage from './pages/LoginPage';
import {
  LayoutDashboard, Truck, Package, LogOut, Leaf, Shield, Route as RutaIcono, Bell, Settings, Navigation,
} from 'lucide-react';

// Code splitting (Informe Green IT, optimización 4): las pantallas autenticadas se descargan bajo demanda.
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const VehiculosPage = lazy(() => import('./pages/VehiculosPage'));
const PedidosPage = lazy(() => import('./pages/PedidosPage'));
const RutasPage = lazy(() => import('./pages/RutasPage'));
const ConductorPage = lazy(() => import('./pages/ConductorPage'));
const NotificacionesPage = lazy(() => import('./pages/NotificacionesPage'));
const AdminPage = lazy(() => import('./pages/AdminPage'));

// Qué puede ver cada rol (Documento 08): el menú y las rutas se limitan igual que el servidor lo hace con la API.
const ACCESO: Record<string, string[]> = {
  '/': ['ADMIN_FLOTA', 'OPERADOR', 'AUDITOR'],
  '/vehiculos': ['ADMIN_FLOTA', 'OPERADOR'],
  '/pedidos': ['ADMIN_FLOTA', 'OPERADOR', 'BODEGA'],
  '/rutas': ['ADMIN_FLOTA', 'OPERADOR', 'AUDITOR'],
  '/conductor': ['CONDUCTOR'],
  '/notificaciones': ['ADMIN_FLOTA', 'OPERADOR', 'BODEGA', 'CONDUCTOR', 'AUDITOR'],
  '/administracion': ['ADMIN_FLOTA'],
};

function inicioDe(rol: string | undefined): string {
  if (rol === 'CONDUCTOR') return '/conductor';
  if (rol === 'BODEGA') return '/pedidos';
  return '/';
}

function Permitida({ ruta, children }: { ruta: string; children: React.ReactNode }) {
  const { user } = useAuth();
  if (!user || !ACCESO[ruta].includes(user.rol)) return <Navigate to={inicioDe(user?.rol)} replace />;
  return <>{children}</>;
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  if (isLoading) {
    return <div className="loading-spinner" style={{ height: '100vh', width: '100%' }}><div className="spinner" /></div>;
  }
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/vehiculos': 'Gestión de Flota Vehicular',
  '/pedidos': 'Gestión de Pedidos',
  '/rutas': 'Rutas Optimizadas',
  '/conductor': 'Mi ruta',
  '/notificaciones': 'Notificaciones',
  '/administracion': 'Administración',
};

function AppLayout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [noLeidas, setNoLeidas] = useState(0);
  const { token } = useAuth();

  useEffect(() => {
    healthApi.check().then(() => setApiOnline(true)).catch(() => setApiOnline(false));
  }, []);

  // Avisos sin leer (RF-009): se consultan al cambiar de pantalla.
  useEffect(() => {
    if (!token) return;
    notificacionesApi.mias(token).then((r) => setNoLeidas(r.noLeidas)).catch(() => {});
  }, [token, location.pathname]);

  const veRuta = (ruta: string) => !!user && ACCESO[ruta].includes(user.rol);
  const title = pageTitles[location.pathname] || 'EcoLogística Lima';

  const initials = user?.nombre
    .split(' ')
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  const rolLabel: Record<string, string> = {
    ADMIN_FLOTA: 'Administrador de Flota',
    OPERADOR: 'Operador Logístico',
    CONDUCTOR: 'Conductor',
    BODEGA: 'Dueño de Bodega',
    AUDITOR: 'Auditor Externo',
  };

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">
              <Leaf size={20} />
            </div>
            <div className="sidebar-logo-text">
              <h1>EcoLogística</h1>
              <span>Lima · DistriRápido</span>
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {veRuta('/') && (
            <>
              <div className="sidebar-section-title">Principal</div>
              <NavLink to="/" end className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
                <LayoutDashboard size={18} /> Dashboard
              </NavLink>
            </>
          )}

          <div className="sidebar-section-title">Operación</div>
          {veRuta('/conductor') && (
            <NavLink to="/conductor" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <Navigation size={18} /> Mi ruta
            </NavLink>
          )}
          {veRuta('/vehiculos') && (
            <NavLink to="/vehiculos" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <Truck size={18} /> Vehículos
            </NavLink>
          )}
          {veRuta('/pedidos') && (
            <NavLink to="/pedidos" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <Package size={18} /> Pedidos
            </NavLink>
          )}
          {veRuta('/rutas') && (
            <NavLink to="/rutas" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <RutaIcono size={18} /> Rutas
            </NavLink>
          )}
          <NavLink to="/notificaciones" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <Bell size={18} /> Notificaciones
            {noLeidas > 0 && (
              <span className="badge badge-amber" style={{ marginLeft: 'auto', fontSize: '0.65rem' }} aria-label={`${noLeidas} sin leer`}>
                {noLeidas}
              </span>
            )}
          </NavLink>
          {veRuta('/administracion') && (
            <NavLink to="/administracion" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <Settings size={18} /> Administración
            </NavLink>
          )}

          <div className="sidebar-section-title">Seguridad</div>
          <div className="sidebar-link" style={{ cursor: 'default' }}>
            <Shield size={18} /> JWT + RBAC
            <span className="badge badge-green" style={{ marginLeft: 'auto', fontSize: '0.6rem' }}>Activo</span>
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="sidebar-avatar">{initials}</div>
            <div className="sidebar-user-info">
              <div className="name">{user?.nombre}</div>
              <div className="role">{rolLabel[user?.rol || ''] || user?.rol}</div>
            </div>
            <button className="btn btn-ghost btn-sm" onClick={logout} title="Cerrar sesión" style={{ color: '#94a3b8' }}>
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="main-content">
        <header className="topbar">
          <h2>{title}</h2>
          <div className="topbar-actions">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'rgba(16, 185, 129, 0.12)', padding: '0.25rem 0.75rem', borderRadius: 'var(--radius-full)', border: '1px solid rgba(16, 185, 129, 0.3)', fontSize: '0.75rem', color: apiOnline === false ? '#b91c1c' : '#047857', fontWeight: 600 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981', boxShadow: '0 0 8px #10b981', display: 'inline-block' }}></span>
              {apiOnline === null ? 'Verificando API…' : apiOnline ? 'API conectada' : 'API sin conexión'}
            </div>
            <span className="badge badge-teal">Versión final</span>
            <span className="badge badge-green">v4.0.0</span>
          </div>
        </header>

        <main className="page-content">
          <Suspense fallback={<div className="loading-spinner"><div className="spinner" /></div>}>
            <Routes>
              <Route path="/" element={<Permitida ruta="/"><DashboardPage /></Permitida>} />
              <Route path="/vehiculos" element={<Permitida ruta="/vehiculos"><VehiculosPage /></Permitida>} />
              <Route path="/pedidos" element={<Permitida ruta="/pedidos"><PedidosPage /></Permitida>} />
              <Route path="/rutas" element={<Permitida ruta="/rutas"><RutasPage /></Permitida>} />
              <Route path="/conductor" element={<Permitida ruta="/conductor"><ConductorPage /></Permitida>} />
              <Route path="/notificaciones" element={<Permitida ruta="/notificaciones"><NotificacionesPage /></Permitida>} />
              <Route path="/administracion" element={<Permitida ruta="/administracion"><AdminPage /></Permitida>} />
              <Route path="*" element={<Navigate to={inicioDe(user?.rol)} replace />} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

function AppRoutes() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div className="loading-spinner" style={{ height: '100vh', width: '100%' }}><div className="spinner" /></div>;
  }

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to={inicioDe(user.rol)} replace /> : <LoginPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
