import React from 'react';
import {
  LayoutDashboard,
  LineChart,
  Package,
  TrendingUp,
  Bell,
  UserCircle
} from 'lucide-react';

const Sidebar = ({ activeTab, onTabChange }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, category: 'PRINCIPAL' },
    { id: 'predictions', label: 'Predicciones', icon: LineChart, category: 'PRINCIPAL' },
    { id: 'inventory', label: 'Inventario', icon: Package, category: 'PRINCIPAL' },
    { id: 'trends', label: 'Tendencias', icon: TrendingUp, category: 'REPORTES' },
    { id: 'alerts', label: 'Alertas', icon: Bell, category: 'REPORTES' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1>DEMAND-24</h1>
        <p>MiniMarket La 24</p>
      </div>

      <nav className="sidebar-nav">
        {['PRINCIPAL', 'REPORTES'].map(category => (
          <div key={category} className="nav-group">
            <span className="nav-category">{category}</span>
            {navItems.filter(item => item.category === category).map(item => (
              <button
                key={item.id}
                className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => onTabChange(item.id)}
              >
                <item.icon size={20} />
                <span>{item.label}</span>
              </button>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <UserCircle size={32} className="user-icon" />
        <div className="user-info">
          <p className="user-name">Admin. Tienda #1</p>
          <p className="user-role">Sucursal Centro</p>
        </div>
      </div>

      <style jsx>{`
        .sidebar {
          width: 260px;
          background: #fff;
          border-right: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          height: 100vh;
          position: sticky;
          top: 0;
        }

        .sidebar-brand {
          padding: 2rem 1.5rem;
        }

        .sidebar-brand h1 {
          font-size: 1.25rem;
          color: var(--text-main);
          margin-bottom: 0.25rem;
        }

        .sidebar-brand p {
          color: var(--text-muted);
          font-size: 0.875rem;
        }

        .sidebar-nav {
          flex: 1;
          padding: 0 0.75rem;
        }

        .nav-group {
          margin-bottom: 2rem;
        }

        .nav-category {
          font-size: 0.7rem;
          font-weight: 700;
          color: #94a3b8;
          padding: 0 0.75rem;
          margin-bottom: 0.75rem;
          display: block;
          letter-spacing: 0.05em;
        }

        .nav-item {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem;
          border: none;
          background: transparent;
          color: var(--text-muted);
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
          font-size: 0.9rem;
          font-weight: 500;
        }

        .nav-item:hover {
          background: var(--primary-50);
          color: var(--primary-600);
        }

        .nav-item.active {
          background: var(--primary-50);
          color: var(--primary-600);
          font-weight: 600;
        }

        .sidebar-footer {
          padding: 1.5rem;
          border-top: 1px solid var(--border);
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .user-icon {
          color: var(--text-muted);
        }

        .user-name {
          font-weight: 600;
          font-size: 0.875rem;
          color: var(--text-main);
        }

        .user-role {
          font-size: 0.75rem;
          color: var(--text-muted);
        }
      `}</style>
    </aside>
  );
};

export default Sidebar;
