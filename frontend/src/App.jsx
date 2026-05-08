import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import KPICard from './components/KPICard';
import DemandChart from './components/DemandChart';
import AlertPanel from './components/AlertPanel';
import PredictionTable from './components/PredictionTable';
import apiService from './services/api';
import { RefreshCw, Package, AlertTriangle, BarChart3, TrendingUp, Download, Loader2, CheckCircle, XCircle, User, Mail, Shield, MapPin, Key, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [skus, setSkus] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [tableData, setTableData] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState('all');
  const [toast, setToast] = useState(null);

  // --- Productos completos del inventario ---
  const [allProducts, setAllProducts] = useState([
    { product: 'Leche entera 1L', code: 'DAIRY-1', stock: 48, demand: 62, status: 'Quiebre', confidence: 'Alta' },
    { product: 'Agua 500ml', code: 'BEVERAGES-1', stock: 120, demand: 95, status: 'Normal', confidence: 'Alta' },
    { product: 'Pan tajado 500g', code: 'BREAD-1', stock: 30, demand: 34, status: 'Revisar', confidence: 'Media' },
    { product: 'Huevos x30', code: 'EGGS-1', stock: 42, demand: 38, status: 'Normal', confidence: 'Alta' },
    { product: 'Jabon liquido 1L', code: 'CLEAN-1', stock: 18, demand: 25, status: 'Quiebre', confidence: 'Media' },
    { product: 'Arroz 1kg', code: 'GROCERY-1', stock: 230, demand: 180, status: 'Normal', confidence: 'Alta' },
    { product: 'Yogurt natural 200g', code: 'DAIRY-2', stock: 35, demand: 50, status: 'Quiebre', confidence: 'Alta' },
    { product: 'Detergente 500ml', code: 'HOME-1', stock: 78, demand: 60, status: 'Normal', confidence: 'Alta' },
    { product: 'Shampoo 400ml', code: 'PERSONAL-1', stock: 110, demand: 70, status: 'Normal', confidence: 'Alta' },
    { product: 'Tomates 1kg', code: 'PRODUCE-1', stock: 22, demand: 45, status: 'Quiebre', confidence: 'Media' },
    { product: 'Carne molida 500g', code: 'MEATS-1', stock: 34, demand: 30, status: 'Normal', confidence: 'Media' },
    { product: 'Aceite vegetal 1L', code: 'GROCERY-2', stock: 55, demand: 52, status: 'Revisar', confidence: 'Alta' },
    { product: 'Galletas surtidas', code: 'SNACKS-1', stock: 88, demand: 65, status: 'Normal', confidence: 'Alta' },
    { product: 'Queso crema 250g', code: 'DAIRY-3', stock: 15, demand: 28, status: 'Quiebre', confidence: 'Alta' },
    { product: 'Papel higienico x4', code: 'HOME-2', stock: 60, demand: 55, status: 'Normal', confidence: 'Alta' },
    { product: 'Pasta 500g', code: 'GROCERY-3', stock: 150, demand: 140, status: 'Normal', confidence: 'Alta' },
    { product: 'Cafe 250g', code: 'GROCERY-4', stock: 45, demand: 50, status: 'Revisar', confidence: 'Media' },
    { product: 'Azucar 1kg', code: 'GROCERY-5', stock: 90, demand: 85, status: 'Normal', confidence: 'Alta' },
    { product: 'Sal 1kg', code: 'GROCERY-6', stock: 70, demand: 65, status: 'Normal', confidence: 'Alta' },
    { product: 'Atun en lata', code: 'GROCERY-7', stock: 110, demand: 90, status: 'Normal', confidence: 'Alta' },
    { product: 'Mayonesa 200g', code: 'GROCERY-8', stock: 35, demand: 40, status: 'Revisar', confidence: 'Baja' },
    { product: 'Salsa de tomate 200g', code: 'GROCERY-9', stock: 40, demand: 35, status: 'Normal', confidence: 'Alta' },
    { product: 'Detergente liquido 1L', code: 'HOME-3', stock: 25, demand: 35, status: 'Quiebre', confidence: 'Media' },
    { product: 'Jabon de tocador', code: 'PERSONAL-2', stock: 85, demand: 80, status: 'Normal', confidence: 'Alta' },
    { product: 'Desodorante', code: 'PERSONAL-3', stock: 50, demand: 45, status: 'Normal', confidence: 'Alta' },
    { product: 'Cereal de maiz 500g', code: 'GROCERY-10', stock: 65, demand: 70, status: 'Revisar', confidence: 'Alta' },
    { product: 'Mermelada de fresa', code: 'GROCERY-11', stock: 40, demand: 30, status: 'Normal', confidence: 'Alta' },
    { product: 'Atun en aceite', code: 'GROCERY-12', stock: 120, demand: 110, status: 'Normal', confidence: 'Alta' },
    { product: 'Lentejas 500g', code: 'GROCERY-13', stock: 95, demand: 85, status: 'Normal', confidence: 'Alta' },
    { product: 'Frijoles 500g', code: 'GROCERY-14', stock: 110, demand: 100, status: 'Normal', confidence: 'Alta' },
  ]);

  const userData = {
    name: 'Sebastian Valencia',
    email: 'sebastian.valencia@minimarket24.com',
    role: 'Administrador Senior',
    branch: 'Sucursal Centro - La 24',
    lastLogin: 'Hace 2 horas',
    id: 'MM24-USR-001'
  };

  // --- Datos de grafica por producto ---
  const chartDataByProduct = {
    'all': [
      { name: 'S-7', actual: 280 }, { name: 'S-6', actual: 320 }, { name: 'S-5', actual: 240 },
      { name: 'S-4', actual: 480 }, { name: 'S-3', actual: 420 }, { name: 'S-2', actual: 550 },
      { name: 'S-1', actual: 450 }, { name: 'S0', actual: 420, projected: 420 },
      { name: 'S+1', projected: 520 }, { name: 'S+2', projected: 580 }, { name: 'S+3', projected: 620 },
    ],
    'Leche entera 1L': [
      { name: 'S-7', actual: 58 }, { name: 'S-6', actual: 62 }, { name: 'S-5', actual: 55 },
      { name: 'S-4', actual: 70 }, { name: 'S-3', actual: 65 }, { name: 'S-2', actual: 48 },
      { name: 'S-1', actual: 60 }, { name: 'S0', actual: 62, projected: 62 },
      { name: 'S+1', projected: 68 }, { name: 'S+2', projected: 72 }, { name: 'S+3', projected: 75 },
    ],
    // Mock data for others...
  };

  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  }, []);

  const productosActivos = allProducts.length;
  const quiebresDetectados = allProducts.filter(p => p.status === 'Quiebre').length;
  const enRevision = allProducts.filter(p => p.status === 'Revisar').length;

  const generatedAlerts = allProducts
    .filter(p => p.status === 'Quiebre' || p.status === 'Revisar')
    .map((p, idx) => ({
      id: `mock-alert-${idx}`,
      alert_type: p.status === 'Quiebre' ? 'stock_break' : 'low_confidence',
      message: p.status === 'Quiebre'
        ? `Quiebre de stock: ${p.product} -- Stock: ${p.stock} uds vs Demanda estimada: ${p.demand} uds`
        : `Revisar: ${p.product} -- Stock: ${p.stock} uds, Demanda estimada: ${p.demand} uds`,
      is_acknowledged: false,
    }));

  const [acknowledgedAlerts, setAcknowledgedAlerts] = useState([]);
  const activeAlerts = [...generatedAlerts.filter(a => !acknowledgedAlerts.includes(a.id)), ...alerts];

  const handleAcknowledge = async (alertId) => {
    if (alertId.startsWith('mock-alert-')) {
      setAcknowledgedAlerts(prev => [...prev, alertId]);
      showToast('Alerta marcada como atendida', 'success');
    } else {
      try {
        await apiService.acknowledgeAlert(alertId);
        fetchData();
        showToast('Alerta marcada como atendida', 'success');
      } catch {
        showToast('Error al atender la alerta', 'error');
      }
    }
  };

  const fetchData = async () => {
    const selectedData = chartDataByProduct[selectedProduct] || chartDataByProduct['all'];
    setChartData(selectedData.map(d => ({
      ...d,
      range: [(d.actual || d.projected) * 0.9, (d.actual || d.projected) * 1.1]
    })));
    setTableData(allProducts);

    try {
      const [skusRes, alertsRes] = await Promise.all([
        apiService.getSkus(),
        apiService.getAlerts()
      ]);
      setSkus(skusRes.data || []);
      const backendAlerts = (alertsRes.data || []).filter(a => !a.is_acknowledged);
      setAlerts(backendAlerts);
    } catch (error) {
      console.error('Error sincronizando datos:', error);
      if (skus.length === 0) {
        setSkus(allProducts.map((p, i) => ({
          id: i + 1,
          sku_code: p.code,
          description: p.product,
        })));
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  useEffect(() => {
    const selectedData = chartDataByProduct[selectedProduct] || chartDataByProduct['all'];
    setChartData(selectedData.map(d => ({
      ...d,
      range: [(d.actual || d.projected) * 0.9, (d.actual || d.projected) * 1.1]
    })));
  }, [selectedProduct]);

  const handleTrain = async () => {
    try {
      setTraining(true);
      // Simular delay y deteccion de cambios
      await new Promise(r => setTimeout(r, 2000));
      const hasChanges = Math.random() > 0.3; // 70% de probabilidad de cambios
      
      if (hasChanges) {
        showToast('Sincronizacion IA completada. Se detectaron cambios en las tendencias de demanda.', 'success');
      } else {
        showToast('Sincronizacion IA completada. No se detectaron cambios significativos en el modelo.', 'info');
      }
    } catch (error) {
      showToast('Error en sincronizacion: El backend no esta disponible.', 'error');
    } finally {
      setTraining(false);
    }
  };

  const exportAlerts = () => {
    if (!activeAlerts || activeAlerts.length === 0) {
      return showToast('No hay alertas para exportar', 'error');
    }
    
    // Generar CSV organizado con ";" como separador para compatibilidad
    const headers = ['Tipo', 'Producto', 'Stock Actual', 'Demanda Estimada', 'Estado', 'Mensaje'];
    const rows = activeAlerts.map(a => {
      const tipo = a.alert_type === 'stock_break' ? 'Quiebre de Stock' : 'Revision';
      const productMatch = allProducts.find(p => a.message && a.message.includes(p.product));
      const producto = productMatch ? productMatch.product : 'N/A';
      const stock = productMatch ? productMatch.stock : 'N/A';
      const demanda = productMatch ? productMatch.demand : 'N/A';
      const estado = productMatch ? productMatch.status : tipo;
      const mensaje = (a.message || '').replace(/[⚠️🔍]/g, '').trim();
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

  const getStockLevel = (stock) => {
    const maxStock = 150;
    const pct = Math.min((stock / maxStock) * 100, 100);
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
            <label>Contraseña</label>
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
              <KPICard title="Productos activos" value={productosActivos} unit="SKU" />
              <KPICard title="Precision del modelo" value={83} unit="%" trend="up" trendValue={4} />
              <KPICard title="Quiebres detectados" value={quiebresDetectados} trend="up" trendValue={1} color="var(--danger)" />
              <KPICard title="En revision" value={enRevision} trend="down" trendValue={2} color="var(--warning)" />
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
                <PredictionTable predictions={tableData} />
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
                    {allProducts.map((p, idx) => {
                      const { pct, color } = getStockLevel(p.stock);
                      const statusClass = p.status === 'Quiebre' ? 'danger' : p.status === 'Revisar' ? 'warning' : 'success';
                      return (
                        <tr key={idx}>
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
                  <p className="trend-stat-value" style={{ color: 'var(--primary-600)' }}>88%</p>
                </div>
                <div className="trend-stat-card">
                  <h4>SKUs evaluados</h4>
                  <p className="trend-stat-value" style={{ color: 'var(--text-main)' }}>{productosActivos}</p>
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
                      <Key size={16} /> Cambiar Contraseña
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
