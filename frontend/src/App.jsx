import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import KPICard from './components/KPICard';
import DemandChart from './components/DemandChart';
import AlertPanel from './components/AlertPanel';
import PredictionTable from './components/PredictionTable';
import { 
  getDashboardSummary, 
  getAlerts, 
  acknowledgeAlert, 
  triggerTraining, 
  login, 
  register, 
  logout 
} from './services/api';
import { supabase } from './services/supabaseClient';
import { 
  RefreshCw, Package, AlertTriangle, BarChart3, TrendingUp, 
  Download, Loader2, CheckCircle, XCircle, Shield, Key, 
  LogOut, User, Mail, MapPin, Calendar, Fingerprint 
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [training, setTraining] = useState(false);
  const [toast, setToast] = useState(null);
  const [isRegisterMode, setIsRegisterMode] = useState(false);

  // --- Datos de Usuario ---
  const [user, setUser] = useState(null);

  // --- Datos del backend ---
  const [allProducts, setAllProducts] = useState([]);
  const [chartDataByProduct, setChartDataByProduct] = useState({});
  const [kpis, setKpis] = useState({ total_skus: 0, model_accuracy: 0, breakdowns: 0, under_review: 0 });
  const [chartData, setChartData] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState('all');
  const [backendAlerts, setBackendAlerts] = useState([]);
  const [acknowledgedAlerts, setAcknowledgedAlerts] = useState([]);

  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  }, []);

  // --- Manejo de Sesión Real ---
  useEffect(() => {
    // 1. Verificar sesión actual al cargar
    const checkSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (session) {
        setUser(session.user);
        setIsLoggedIn(true);
        fetchData();
      }
      setAuthLoading(false);
    };

    checkSession();

    // 2. Escuchar cambios de estado (Login/Logout)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        setUser(session.user);
        setIsLoggedIn(true);
      } else {
        setUser(null);
        setIsLoggedIn(false);
        setAllProducts([]); // Limpiar datos al salir
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  // --- Generación de alertas ---
  const generatedAlerts = allProducts
    .filter(p => p.status === 'Quiebre' || p.status === 'Revisar')
    .map((p, idx) => ({
      id: `alert-${p.sku_id}-${idx}`,
      alert_type: p.status === 'Quiebre' ? 'stock_break' : 'low_confidence',
      message: p.status === 'Quiebre'
        ? `Quiebre de stock: ${p.product} -- Stock: ${p.stock} uds vs Demanda estimada: ${p.demand} uds`
        : `Revisar: ${p.product} -- Stock: ${p.stock} uds, Demanda estimada: ${p.demand} uds`,
      is_acknowledged: false,
    }));

  const activeAlerts = [
    ...generatedAlerts.filter(a => !acknowledgedAlerts.includes(a.id)),
    ...backendAlerts.filter(a => !a.is_acknowledged),
  ];

  const handleAcknowledge = async (alertId) => {
    if (alertId.startsWith('alert-')) {
      setAcknowledgedAlerts(prev => [...prev, alertId]);
      showToast('Alerta marcada como atendida', 'success');
    } else {
      try {
        await acknowledgeAlert(alertId);
        fetchData();
        showToast('Alerta marcada como atendida', 'success');
      } catch {
        showToast('Error al atender la alerta', 'error');
      }
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const [dashboardData, alertsData] = await Promise.allSettled([
        getDashboardSummary(),
        getAlerts(),
      ]);

      if (dashboardData.status === 'fulfilled') {
        const data = dashboardData.value;
        setAllProducts(data.products);
        setChartDataByProduct(data.chart_data);
        setKpis(data.kpis);
        const key = selectedProduct === 'all' ? 'all' : selectedProduct;
        setChartData(data.chart_data[key] || data.chart_data['all'] || []);
      }

      if (alertsData.status === 'fulfilled') {
        const alerts = alertsData.value || [];
        setBackendAlerts(Array.isArray(alerts) ? alerts : []);
      }
    } catch (error) {
      console.error('Error cargando datos:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isLoggedIn) {
      const key = selectedProduct === 'all' ? 'all' : selectedProduct;
      const selectedChart = chartDataByProduct[key] || chartDataByProduct['all'] || [];
      setChartData(selectedChart);
    }
  }, [selectedProduct, chartDataByProduct, isLoggedIn]);

  const handleTrain = async () => {
    try {
      setTraining(true);
      showToast('Iniciando entrenamiento del modelo...', 'info');
      await triggerTraining();
      showToast('Sincronización IA completada con éxito.', 'success');
      await fetchData();
    } catch (error) {
      const message = error.response?.data?.detail || 'Error en sincronización.';
      showToast(message, 'error');
    } finally {
      setTraining(false);
    }
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    const email = e.target.email.value;
    const password = e.target.password.value;
    const fullName = isRegisterMode ? e.target.fullName.value : null;

    // Validación estricta de contraseña solo en modo registro
    if (isRegisterMode) {
      const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&.])[A-Za-z\d@$!%*?&.]{8,}$/;
      if (!passwordRegex.test(password)) {
        showToast(
          'La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas, un número y un carácter especial.', 
          'error'
        );
        return;
      }
    }

    setLoading(true);
    try {
      if (isRegisterMode) {
        await register(email, password, fullName);
        showToast('¡Cuenta creada! Ya puedes iniciar sesión.', 'success');
        setIsRegisterMode(false);
      } else {
        await login(email, password);
        showToast(`Sesión iniciada con éxito`, 'success');
      }
    } catch (error) {
      console.error('Error de Auth:', error);
      let errorMsg = 'Error en la operación';
      
      if (error.status === 429) {
        errorMsg = 'Demasiados intentos. Por favor, espera unos minutos antes de intentar de nuevo.';
      } else if (error.message.includes('Email not confirmed')) {
        errorMsg = 'Debes confirmar tu correo electrónico (revisa tu bandeja de entrada o desactiva la confirmación en Supabase).';
      } else if (error.status === 400) {
        errorMsg = 'Credenciales inválidas o datos incorrectos.';
      } else {
        errorMsg = error.message || errorMsg;
      }
      
      showToast(errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      showToast('Sesión cerrada correctamente', 'info');
    } catch (error) {
      showToast('Error al cerrar sesión', 'error');
    }
  };

  const exportAlerts = () => {
    if (!activeAlerts.length) return showToast('No hay alertas para exportar', 'error');
    const headers = ['Tipo', 'Producto', 'Stock Actual', 'Demanda Estimada', 'Estado', 'Mensaje'];
    const rows = activeAlerts.map(a => {
      const p = allProducts.find(p => a.message.includes(p.product)) || {};
      return [a.alert_type, p.product || 'N/A', p.stock || 'N/A', p.demand || 'N/A', p.status || 'N/A', `"${a.message}"`].join(';');
    });
    const csvContent = '\uFEFF' + [headers.join(';'), ...rows].join('\r\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `alertas_${new Date().toISOString().slice(0,10)}.csv`;
    link.click();
  };

  const getStockLevel = (stock, demand) => {
    const maxRef = Math.max(demand * 1.5, 150);
    const pct = Math.min((stock / maxRef) * 100, 100);
    let color = 'var(--success)';
    if (pct < 30) color = 'var(--danger)';
    else if (pct < 60) color = 'var(--warning)';
    return { pct, color };
  };

  const tabLabels = {
    dashboard: 'Dashboard',
    predictions: 'Predicciones',
    inventory: 'Inventario',
    trends: 'Tendencias',
    alerts: 'Centro de Riesgos',
    profile: 'Perfil',
  };

  const ProductSelector = ({ value, onChange }) => (
    <select className="product-selector" value={value} onChange={e => onChange(e.target.value)}>
      <option value="all">Todos los productos</option>
      {allProducts.map(p => (
        <option key={p.sku_id} value={p.product}>{p.product}</option>
      ))}
    </select>
  );

  if (authLoading) return (
    <div className="loading-screen">
      <Loader2 className="animate-spin" size={40} />
      <p>Iniciando sesión...</p>
    </div>
  );

  if (!isLoggedIn) return (
    <>
      <div className="login-container">
        <motion.div className="login-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1>DEMAND-24</h1>
          <p>{isRegisterMode ? 'Crea una nueva cuenta' : 'Inicia sesión para acceder'}</p>
          <form className="login-form" onSubmit={handleAuth}>
            {isRegisterMode && (
              <div className="form-group">
                <label>Nombre Completo</label>
                <input name="fullName" type="text" placeholder="Ej: Sebastian Valencia" required />
              </div>
            )}
            <div className="form-group">
              <label>Correo electrónico</label>
              <input name="email" type="email" placeholder="usuario@minimarket24.com" required />
            </div>
            <div className="form-group">
              <label>Contraseña</label>
              <input name="password" type="password" placeholder="••••••••" required />
            </div>
            <button type="submit" className="btn-login" disabled={loading}>
              {loading ? <Loader2 className="animate-spin" size={18} /> : (isRegisterMode ? 'Registrarse' : 'Ingresar')}
            </button>
          </form>
          <button className="btn-text" onClick={() => setIsRegisterMode(!isRegisterMode)}>
            {isRegisterMode ? '¿Ya tienes cuenta? Inicia sesión' : '¿No tienes cuenta? Regístrate'}
          </button>
        </motion.div>
      </div>

      {/* Renderizar notificaciones en la pantalla de Login */}
      <AnimatePresence>
        {toast && (
          <motion.div className={`toast-notification ${toast.type}`} initial={{ opacity: 0, y: 50, x: '-50%' }} animate={{ opacity: 1, y: 0, x: '-50%' }} exit={{ opacity: 0, y: 50, x: '-50%' }}>
            {toast.type === 'success' ? <CheckCircle size={18} /> : (toast.type === 'info' ? <Shield size={18} /> : <XCircle size={18} />)}
            <span>{toast.message}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );

  const renderContent = () => {
    switch(activeTab) {
      case 'dashboard':
        return (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="view-container">
            <section className="kpi-grid">
              <KPICard title="Productos activos" value={kpis.total_skus} unit="SKU" />
              <KPICard title="Precisión del modelo" value={kpis.model_accuracy} unit="%" trend="up" trendValue={4} />
              <KPICard title="Quiebres detectados" value={kpis.breakdowns} trend="up" trendValue={1} color="var(--danger)" />
              <KPICard title="En revisión" value={kpis.under_review} trend="down" trendValue={2} color="var(--warning)" />
            </section>
            <div className="dashboard-grid">
              <div className="grid-main">
                <DemandChart
                  data={chartData}
                  skuName={selectedProduct === 'all' ? 'Todos los productos' : selectedProduct}
                  productSelector={<ProductSelector value={selectedProduct} onChange={setSelectedProduct} />}
                />
              </div>
              <div className="grid-side">
                <AlertPanel alerts={activeAlerts} onAcknowledge={handleAcknowledge} />
              </div>
            </div>
          </motion.div>
        );

      case 'predictions':
        return (
          <motion.div initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} className="view-container">
            <div className="card view-card">
              <div className="flex-header">
                <BarChart3 size={22} color="var(--primary-500)" />
                <h3>Proyecciones Detalladas</h3>
              </div>
              <DemandChart
                data={chartData}
                skuName={selectedProduct === 'all' ? 'Consolidado General' : selectedProduct}
                productSelector={<ProductSelector value={selectedProduct} onChange={setSelectedProduct} />}
              />
              <div style={{ marginTop: '1.75rem' }}>
                <PredictionTable predictions={allProducts} />
              </div>
            </div>
          </motion.div>
        );

      case 'inventory':
        return (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="view-container">
            <div className="card view-card">
              <div className="flex-header">
                <Package size={22} color="var(--primary-500)" />
                <h3>Catálogo e Inventario</h3>
                <span className="inventory-count">{allProducts.length} productos</span>
              </div>
              <div className="table-responsive">
                <table className="inventory-table">
                  <thead>
                    <tr><th>Código</th><th>Producto</th><th style={{ textAlign: 'right' }}>Stock actual</th><th>Nivel</th><th style={{ textAlign: 'center' }}>Estado</th></tr>
                  </thead>
                  <tbody>
                    {allProducts.map((p) => {
                      const { pct, color } = getStockLevel(p.stock, p.demand);
                      return (
                        <tr key={p.sku_id}>
                          <td><strong>{p.code}</strong></td>
                          <td>{p.product}</td>
                          <td style={{ textAlign: 'right' }}>
                            <span className={`stock-cell ${pct < 30 ? 'stock-low' : pct < 60 ? 'stock-warn' : 'stock-ok'}`}>{p.stock} uds</span>
                          </td>
                          <td>
                            <div className="stock-bar-container">
                              <div className="stock-bar"><div className="stock-bar-fill" style={{ width: `${pct}%`, background: color }}></div></div>
                              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 500 }}>{Math.round(pct)}%</span>
                            </div>
                          </td>
                          <td style={{ textAlign: 'center' }}>
                            <span className={`status-badge ${p.status === 'Quiebre' ? 'danger' : p.status === 'Revisar' ? 'warning' : 'success'}`}>{p.status}</span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </motion.div>
        );

      case 'trends':
        return (
          <motion.div initial={{ opacity: 0, scale: 0.99 }} animate={{ opacity: 1, scale: 1 }} className="view-container">
            <div className="card view-card">
              <div className="flex-header"><TrendingUp size={22} color="var(--success)" /><h3>Análisis de Tendencias</h3></div>
              <div className="trends-stats">
                <div className="trend-stat-card"><h4>Crecimiento semanal</h4><p className="trend-stat-value" style={{ color: 'var(--success)' }}>+12.4%</p></div>
                <div className="trend-stat-card"><h4>Confianza promedio</h4><p className="trend-stat-value" style={{ color: 'var(--primary-600)' }}>{kpis.model_accuracy}%</p></div>
                <div className="trend-stat-card"><h4>SKUs evaluados</h4><p className="trend-stat-value" style={{ color: 'var(--text-main)' }}>{kpis.total_skus}</p></div>
              </div>
              <DemandChart
                data={chartData.map(d => ({
                  ...d,
                  actual: d.actual ? Math.round(d.actual * 0.8) : null,
                  projected: d.projected ? Math.round(d.projected * 1.2) : null,
                  range: d.range ? [d.range[0] * 0.75, d.range[1] * 1.25] : undefined,
                }))}
                skuName="Tendencia de Mercado"
              />
            </div>
          </motion.div>
        );

      case 'alerts':
        return (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="view-container">
            <div className="card view-card">
              <div className="flex-header"><AlertTriangle size={22} color="var(--danger)" /><h3>Centro de Riesgos</h3><span className="inventory-count">{activeAlerts.length} alertas</span></div>
              <div className="alerts-page-grid">
                <AlertPanel alerts={activeAlerts} onAcknowledge={handleAcknowledge} />
                <div className="card reports-panel"><h4>Reportes</h4><p>Descarga el listado en CSV.</p><button className="btn-export" onClick={exportAlerts}><Download size={16} />Exportar reporte</button></div>
              </div>
            </div>
          </motion.div>
        );

      case 'profile':
        return (
          <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="view-container">
            <div className="card view-card">
              <div className="flex-header"><User size={22} color="var(--primary-500)" /><h3>Perfil de Usuario</h3></div>
              <div className="settings-grid">
                <div className="settings-profile-card card glass">
                  <div className="profile-avatar-large">{user?.email?.[0].toUpperCase()}</div>
                  <div className="profile-info">
                    <h3>{user?.user_metadata?.full_name || 'Usuario DEMAND-24'}</h3>
                    <p>{user?.email}</p>
                    <span className="status-badge success">Sesión Activa</span>
                  </div>
                </div>
                <div className="settings-details card">
                  <div className="settings-details-list">
                    <div className="detail-item"><div className="detail-label"><Fingerprint size={14} /> ID de Usuario</div><div className="detail-value">{user?.id}</div></div>
                    <div className="detail-item"><div className="detail-label"><Mail size={14} /> Correo Electrónico</div><div className="detail-value">{user?.email}</div></div>
                    <div className="detail-item"><div className="detail-label"><MapPin size={14} /> Sucursal</div><div className="detail-value">Sucursal Centro - La 24</div></div>
                    <div className="detail-item"><div className="detail-label"><Calendar size={14} /> Último Acceso</div><div className="detail-value">{new Date(user?.last_sign_in_at).toLocaleString()}</div></div>
                    <div className="detail-item"><div className="detail-label"><Shield size={14} /> Nivel de Acceso</div><div className="detail-value">Administrador</div></div>
                  </div>
                  <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
                    <button className="btn-sync" onClick={handleLogout} style={{ flex: 1, color: 'var(--danger)', borderColor: 'var(--danger)' }}><LogOut size={16} /> Cerrar Sesión</button>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        );

      default: return null;
    }
  };

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="main-content">
        <header className="main-header">
          <div className="header-title"><h2>{tabLabels[activeTab] || activeTab}</h2><p className="header-subtitle">DEMAND-24 -- Sistema Inteligente</p></div>
          <div className="header-actions">
            <button className={`btn-sync ${training ? 'loading' : ''}`} onClick={handleTrain} disabled={training}>
              {training ? <Loader2 className="animate-spin" size={16} /> : <RefreshCw size={16} />}
              {training ? 'Sincronizando...' : 'Sincronizar IA'}
            </button>
          </div>
        </header>
        <AnimatePresence mode="wait">{renderContent()}</AnimatePresence>
      </main>
      <AnimatePresence>
        {toast && (
          <motion.div className={`toast-notification ${toast.type}`} initial={{ opacity: 0, y: 50, x: '-50%' }} animate={{ opacity: 1, y: 0, x: '-50%' }} exit={{ opacity: 0, y: 50, x: '-50%' }}>
            {toast.type === 'success' ? <CheckCircle size={18} /> : (toast.type === 'info' ? <Shield size={18} /> : <XCircle size={18} />)}
            <span>{toast.message}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
