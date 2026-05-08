import React from 'react';
import {
  LayoutDashboard,
  LineChart,
  Package,
  TrendingUp,
  Bell,
  LogOut,
  User
} from 'lucide-react';

const Sidebar = ({ activeTab, onTabChange }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, category: 'PRINCIPAL' },
    { id: 'predictions', label: 'Predicciones', icon: LineChart, category: 'PRINCIPAL' },
    { id: 'inventory', label: 'Inventario', icon: Package, category: 'PRINCIPAL' },
    { id: 'trends', label: 'Tendencias', icon: TrendingUp, category: 'REPORTES' },
    { id: 'alerts', label: 'Alertas', icon: Bell, category: 'REPORTES' },
    { id: 'profile', label: 'Perfil', icon: User, category: 'SISTEMA' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1>DEMAND‑24</h1>
        <p>MiniMarket La 24 S.A.S.</p>
      </div>

      <nav className="sidebar-nav">
        {['PRINCIPAL', 'REPORTES', 'SISTEMA'].map(category => (
          <div key={category} className="nav-group">
            <span className="nav-category">{category}</span>
            {navItems.filter(item => item.category === category).map(item => (
              <button
                key={item.id}
                className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => onTabChange(item.id)}
              >
                <item.icon size={18} />
                <span>{item.label}</span>
              </button>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-avatar">AT</div>
        <div className="user-info">
          <p className="user-name">Admin. Tienda #1</p>
          <p className="user-role">Sucursal Centro</p>
        </div>
        <span className="sidebar-version">v0.1</span>
      </div>
    </aside>
  );
};

export default Sidebar;
