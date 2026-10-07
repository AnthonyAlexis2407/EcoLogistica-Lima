/**
 * App — Componente raíz con routing y layout (sidebar + topbar).
 */

import { BrowserRouter, Routes, Route, Navigate, NavLink, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import VehiculosPage from './pages/VehiculosPage';
import PedidosPage from './pages/PedidosPage';
import { LayoutDashboard, Truck, Package, LogOut, Leaf, Shield } from 'lucide-react';

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
};

function AppLayout() {
  const { user, logout } = useAuth();
  const location = useLocation();
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
          <div className="sidebar-section-title">Principal</div>
          <NavLink to="/" end className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <LayoutDashboard size={18} /> Dashboard
          </NavLink>

          <div className="sidebar-section-title">Módulos Sprint 2</div>
          <NavLink to="/vehiculos" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <Truck size={18} /> Vehículos
          </NavLink>
          <NavLink to="/pedidos" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <Package size={18} /> Pedidos
          </NavLink>

          <div className="sidebar-section-title">Seguridad</div>
          <div className="sidebar-link" style={{ cursor: 'default', opacity: 0.6 }}>
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
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'rgba(16, 185, 129, 0.12)', padding: '0.25rem 0.75rem', borderRadius: 'var(--radius-full)', border: '1px solid rgba(16, 185, 129, 0.3)', fontSize: '0.75rem', color: '#34d399', fontWeight: 600 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981', boxShadow: '0 0 8px #10b981', display: 'inline-block' }}></span>
              API Online · 100% Operativo
            </div>
            <span className="badge badge-teal">Sprint 2</span>
            <span className="badge badge-green">v2.1.0</span>
          </div>
        </header>

        <main className="page-content">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/vehiculos" element={<VehiculosPage />} />
            <Route path="/pedidos" element={<PedidosPage />} />
          </Routes>
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
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <LoginPage />} />
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
