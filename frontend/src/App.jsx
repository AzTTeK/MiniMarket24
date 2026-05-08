import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import KPICard from './components/KPICard';
import DemandChart from './components/DemandChart';
import AlertPanel from './components/AlertPanel';
import PredictionTable from './components/PredictionTable';
import { getDashboardSummary, getAlerts, acknowledgeAlert, triggerTraining } from './services/api';
import { RefreshCw, Package, AlertTriangle, BarChart3, TrendingUp, Download, Loader2, CheckCircle, XCircle, Shield, Key, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [toast, setToast] = useState(null);

  // --- Datos del backend ---
  const [allProducts, setAllProducts] = useState([]);
  const [chartDataByProduct, setChartDataByProduct] = useState({});
  const [kpis, setKpis] = useState({ total_skus: 0, model_accuracy: 0, breakdowns: 0, under_review: 0 });
  const [chartData, setChartData] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState('all');
  const [backendAlerts, setBackendAlerts] = useState([]);
  const [acknowledgedAlerts, setAcknowledgedAlerts] = useState([]);

  const userData = {
    name: 'Sebastian Valencia',
    email: 'sebastian.valencia@minimarket24.com',
    role: 'Administrador Senior',
    branch: 'Sucursal Centro - La 24',
    lastLogin: 'Hace 2 horas',
    id: 'MM24-USR-001'
  };

  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  }, []);

  // --- Generacion de alertas desde datos de productos ---
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

  // --- Carga de datos reales del backend ---
  const fetchData = async () => {
    try {
      const [dashboardData, alertsData] = await Promise.allSettled([
        getDashboardSummary(),
        getAlerts(),
      ]);

      // Dashboard data
      if (dashboardData.status === 'fulfilled') {
        const data = dashboardData.value;
        setAllProducts(data.products);
        setChartDataByProduct(data.chart_data);
        setKpis(data.kpis);

        // Set chart data for current selection
        const selectedChart = data.chart_data[selectedProduct === 'all' ? 'all' : selectedProduct] || data.chart_data['all'] || [];
        setChartData(selectedChart);
      }

      // Alerts from backend (additional server-side alerts)
      if (alertsData.status === 'fulfilled') {
        const alerts = alertsData.value || [];
        setBackendAlerts(Array.isArray(alerts) ? alerts : []);
      }
    } catch (error) {
      console.error('Error cargando datos:', error);
      showToast('Error al conectar con el servidor', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  useEffect(() => {
    // Actualizar grafico cuando cambia el producto seleccionado
    const key = selectedProduct === 'all' ? 'all' : selectedProduct;
    const selectedChart = chartDataByProduct[key] || chartDataByProduct['all'] || [];
    setChartData(selectedChart);
  }, [selectedProduct, chartDataByProduct]);

  // --- Entrenamiento real via API ---
  const handleTrain = async () => {
    try {
      setTraining(true);
      showToast('Iniciando entrenamiento del modelo...', 'info');
      await triggerTraining();
      showToast('Sincronizacion IA completada. El modelo ha sido re-entrenado con exito.', 'success');
      // Recargar datos del dashboard
      await fetchData();
    } catch (error) {
      const message = error.response?.data?.detail || 'Error en sincronizacion: El backend no esta disponible.';
      showToast(message, 'error');
    } finally {
      setTraining(false);
    }
  };

  const exportAlerts = () => {
    if (!activeAlerts || activeAlerts.length === 0) {
      return showToast('No hay alertas para exportar', 'error');
    }

    const headers = ['Tipo', 'Producto', 'Stock Actual', 'Demanda Estimada', 'Estado', 'Mensaje'];
    const rows = activeAlerts.map(a => {
      const tipo = a.alert_type === 'stock_break' ? 'Quiebre de Stock' : 'Revision';
      const productMatch = allProducts.find(p => a.message && a.message.includes(p.product));
      const producto = productMatch ? productMatch.product : 'N/A';
      const stock = productMatch ? productMatch.stock : 'N/A';
      const demanda = productMatch ? productMatch.demand : 'N/A';
      const estado = productMatch ? productMatch.status : tipo;
      const mensaje = (a.message || '').trim();
      return [tipo, producto, stock, demanda, estado, `"${mensaje}"`].join(';');
    });

    const csvContent = '\uFEFF' + [headers.join(';'), ...rows].join('\r\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `reporte_alertas_${new Date().toISOString().slice(0,10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
    showToast('Reporte CSV exportado correctamente', 'success');
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
    alerts: 'Centro de Alertas',
    settings: 'Configuracion',
  };

  const handleLogin = (e) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setIsLoggedIn(true);
      setLoading(false);
      showToast('Bienvenido de nuevo, Sebastian', 'success');
    }, 1000);
  };

  const ProductSelector = ({ value, onChange }) => (
    <select
      className="product-selector"
      value={value}
      onChange={e => onChange(e.target.value)}
    >
      <option value="all">Todos los productos</option>
      {allProducts.map(p => (
        <option key={p.code} value={p.product}>{p.product}</option>
      ))}
    </select>
  );

  if (loading) return (
    <div className="loading-screen">
      <Loader2 className="animate-spin" size={40} />
      <p>Procesando...</p>
    </div>
  );

  if (!isLoggedIn) return (
    <div className="login-container">
      <motion.div 
        className="login-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1>DEMAND-24</h1>
        <p>Inicie sesion para acceder al sistema</p>
        <form className="login-form" onSubmit={handleLogin}>
          <div className="form-group">
            <label>Correo electronico</label>
            <input type="email" placeholder="usuario@minimarket24.com" required defaultValue="sebastian.valencia@minimarket24.com" />
          </div>
          <div className="form-group">
            <label>Contrasena</label>
            <input type="password" placeholder="••••••••" required defaultValue="password123" />
          </div>
          <button type="submit" className="btn-login">Ingresar al Dashboard</button>
        </form>
      </motion.div>
    </div>
  );

  const renderContent = () => {
    switch(activeTab) {
      case 'dashboard':
        return (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="view-container">
            <section className="kpi-grid">
              <KPICard title="Productos activos" value={kpis.total_skus} unit="SKU" />
              <KPICard title="Precision del modelo" value={kpis.model_accuracy} unit="%" trend="up" trendValue={4} />
              <KPICard title="Quiebres detectados" value={kpis.breakdowns} trend="up" trendValue={1} color="var(--danger)" />
              <KPICard title="En revision" value={kpis.under_review} trend="down" trendValue={2} color="var(--warning)" />
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
                <h3>Catalogo e Inventario</h3>
                <span className="inventory-count">{allProducts.length} productos</span>
              </div>
              <div className="table-responsive">
                <table className="inventory-table">
                  <thead>
                    <tr>
                      <th>Codigo</th>
                      <th>Producto</th>
                      <th style={{ textAlign: 'right' }}>Stock actual</th>
                      <th>Nivel</th>
                      <th style={{ textAlign: 'center' }}>Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allProducts.map((p) => {
                      const { pct, color } = getStockLevel(p.stock, p.demand);
                      const statusClass = p.status === 'Quiebre' ? 'danger' : p.status === 'Revisar' ? 'warning' : 'success';
                      return (
                        <tr key={p.sku_id}>
                          <td><strong>{p.code}</strong></td>
                          <td>{p.product}</td>
                          <td style={{ textAlign: 'right' }}>
                            <span className={`stock-cell ${pct < 30 ? 'stock-low' : pct < 60 ? 'stock-warn' : 'stock-ok'}`}>
                              {p.stock} uds
                            </span>
                          </td>
                          <td>
                            <div className="stock-bar-container">
                              <div className="stock-bar">
                                <div className="stock-bar-fill" style={{ width: `${pct}%`, background: color }}></div>
                              </div>
                              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 500 }}>{Math.round(pct)}%</span>
                            </div>
                          </td>
                          <td style={{ textAlign: 'center' }}>
                            <span className={`status-badge ${statusClass}`}>{p.status}</span>
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
              <div className="flex-header">
                <TrendingUp size={22} color="var(--success)" />
                <h3>Analisis de Tendencias</h3>
              </div>
              <div className="trends-stats">
                <div className="trend-stat-card">
                  <h4>Crecimiento semanal</h4>
                  <p className="trend-stat-value" style={{ color: 'var(--success)' }}>+12.4%</p>
                </div>
                <div className="trend-stat-card">
                  <h4>Confianza promedio</h4>
                  <p className="trend-stat-value" style={{ color: 'var(--primary-600)' }}>{kpis.model_accuracy}%</p>
                </div>
                <div className="trend-stat-card">
                  <h4>SKUs evaluados</h4>
                  <p className="trend-stat-value" style={{ color: 'var(--text-main)' }}>{kpis.total_skus}</p>
                </div>
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
              <div className="flex-header">
                <AlertTriangle size={22} color="var(--danger)" />
                <h3>Centro de Riesgos</h3>
                <span className="inventory-count">{activeAlerts.length} alertas activas</span>
              </div>
              <div className="alerts-page-grid">
                <AlertPanel alerts={activeAlerts} onAcknowledge={handleAcknowledge} />
                <div className="card reports-panel">
                  <h4>Reportes</h4>
                  <p>Descarga el listado de acciones preventivas en formato CSV.</p>
                  <button className="btn-export" onClick={exportAlerts}>
                    <Download size={16} />
                    Exportar reporte
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        );

      case 'settings':
        return (
          <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="view-container">
            <div className="card view-card">
              <div className="flex-header">
                <Shield size={22} color="var(--primary-500)" />
                <h3>Configuracion de Usuario</h3>
              </div>
              
              <div className="settings-grid">
                <div className="settings-profile-card card glass">
                  <div className="profile-avatar-large">SV</div>
                  <div className="profile-info">
                    <h3>{userData.name}</h3>
                    <p>{userData.role}</p>
                    <span className="status-badge success">En Linea</span>
                  </div>
                </div>
                
                <div className="settings-details card">
                  <div className="settings-details-list">
                    <div className="detail-item">
                      <div className="detail-label">ID de Usuario</div>
                      <div className="detail-value">{userData.id}</div>
                    </div>
                    <div className="detail-item">
                      <div className="detail-label">Correo Electronico</div>
                      <div className="detail-value">{userData.email}</div>
                    </div>
                    <div className="detail-item">
                      <div className="detail-label">Sucursal Asignada</div>
                      <div className="detail-value">{userData.branch}</div>
                    </div>
                    <div className="detail-item">
                      <div className="detail-label">Ultimo Acceso</div>
                      <div className="detail-value">{userData.lastLogin}</div>
                    </div>
                    <div className="detail-item">
                      <div className="detail-label">Nivel de Acceso</div>
                      <div className="detail-value">Acceso Total (Root)</div>
                    </div>
                  </div>
                  
                  <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
                    <button className="btn-sync" style={{ flex: 1 }}>
                      <Key size={16} /> Cambiar Contrasena
                    </button>
                    <button className="btn-sync" onClick={() => setIsLoggedIn(false)} style={{ flex: 1, color: 'var(--danger)', borderColor: 'var(--danger)' }}>
                      <LogOut size={16} /> Cerrar Sesion
                    </button>
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
          <div className="header-title">
            <h2>{tabLabels[activeTab] || activeTab}</h2>
            <p className="header-subtitle">DEMAND-24 -- Sistema de Prediccion de Demanda</p>
          </div>
          <div className="header-actions">
            <button
              className={`btn-sync ${training ? 'loading' : ''}`}
              onClick={handleTrain}
              disabled={training}
            >
              {training ? <Loader2 className="animate-spin" size={16} /> : <RefreshCw size={16} />}
              {training ? 'Sincronizando...' : 'Sincronizar IA'}
            </button>
          </div>
        </header>
        <AnimatePresence mode="wait">{renderContent()}</AnimatePresence>
      </main>

      {/* --- Toast Notification --- */}
      <AnimatePresence>
        {toast && (
          <motion.div
            className={`toast-notification ${toast.type}`}
            initial={{ opacity: 0, y: 50, x: '-50%' }}
            animate={{ opacity: 1, y: 0, x: '-50%' }}
            exit={{ opacity: 0, y: 50, x: '-50%' }}
            transition={{ duration: 0.3 }}
          >
            {toast.type === 'success' ? <CheckCircle size={18} /> : (toast.type === 'info' ? <Shield size={18} /> : <XCircle size={18} />)}
            <span>{toast.message}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
