import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import KPICard from './components/KPICard';
import DemandChart from './components/DemandChart';
import AlertPanel from './components/AlertPanel';
import PredictionTable from './components/PredictionTable';
import apiService from './services/api';
import { RefreshCw, Package, AlertTriangle, BarChart3, TrendingUp, Download, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [skus, setSkus] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [tableData, setTableData] = useState([]);
  const [stats, setStats] = useState({ skuCount: 0, precision: 83, breaks: 0, overstock: 2 });

  // Stock demo data for inventory view
  const [inventoryStock] = useState({
    'BEVERAGES': 120,
    'DAIRY': 48,
    'GROCERY I': 230,
    'PRODUCE': 65,
    'MEATS': 34,
    'BREAD/BAKERY': 55,
    'CLEANING': 90,
    'HOME CARE': 78,
    'PERSONAL CARE': 110,
    'EGGS': 42,
  });

  const fetchData = async () => {
    // Mock data siempre disponible (independiente del backend)
    const baseData = [
      { name: 'S-7', actual: 28 }, { name: 'S-6', actual: 32 }, { name: 'S-5', actual: 24 },
      { name: 'S-4', actual: 48 }, { name: 'S-3', actual: 42 }, { name: 'S-2', actual: 55 },
      { name: 'S-1', actual: 45 }, { name: 'S0', actual: 42, projected: 42 },
      { name: 'S+1', projected: 52 }, { name: 'S+2', projected: 58 }, { name: 'S+3', projected: 62 }
    ];
    setChartData(baseData.map(d => ({ ...d, range: [(d.actual || d.projected) * 0.9, (d.actual || d.projected) * 1.1] })));
    setTableData([
      { product: 'Leche entera 1L', stock: 48, demand: 62, status: 'Quiebre', confidence: 'Alta' },
      { product: 'Agua 500ml', stock: 120, demand: 95, status: 'Normal', confidence: 'Alta' },
      { product: 'Pan tajado 500g', stock: 30, demand: 34, status: 'Revisar', confidence: 'Media' },
      { product: 'Huevos x30', stock: 42, demand: 38, status: 'Normal', confidence: 'Alta' },
      { product: 'Jabón líquido 1L', stock: 18, demand: 25, status: 'Quiebre', confidence: 'Media' },
    ]);

    try {
      const [skusRes, alertsRes] = await Promise.all([
        apiService.getSkus(),
        apiService.getAlerts()
      ]);
      setSkus(skusRes.data || []);
      const activeAlerts = (alertsRes.data || []).filter(a => !a.is_acknowledged);
      setAlerts(activeAlerts);
      setStats(prev => ({
        ...prev,
        skuCount: (skusRes.data || []).length,
        breaks: activeAlerts.filter(a => a.alert_type === 'stock_break').length
      }));
    } catch (error) {
      console.error('Error sincronizando datos:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleTrain = async () => {
    try {
      setTraining(true);
      const res = await apiService.triggerTraining();
      alert(res.data?.message || 'Sincronización iniciada en segundo plano.');
    } catch (error) {
      alert('Error en sincronización: ' + (error.response?.data?.detail || 'El backend no responde.'));
    } finally {
      setTraining(false);
    }
  };

  const exportAlerts = () => {
    if (!alerts || alerts.length === 0) return alert("No hay alertas para exportar");
    const text = alerts.map(a => `[${(a.alert_type || 'INFO').toUpperCase()}] ${a.message || ''}`).join('\n');
    const blob = new Blob([`DEMAND-24 REPORT\n${new Date().toLocaleString()}\n\n${text}`], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url; link.download = `reporte_riesgos_${new Date().getTime()}.txt`;
    link.click();
  };

  const getStockLevel = (stock, code) => {
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
  };

  if (loading) return (
    <div className="loading-screen">
      <Loader2 className="animate-spin" size={40} />
      <p>Iniciando DEMAND-24...</p>
    </div>
  );

  const renderContent = () => {
    switch(activeTab) {
      case 'dashboard':
        return (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="view-container">
            <section className="kpi-grid">
              <KPICard title="Productos activos" value={stats.skuCount} unit="SKU" />
              <KPICard title="Precisión del modelo" value={stats.precision} unit="%" trend="up" trendValue={4} />
              <KPICard title="Quiebres detectados" value={stats.breaks} trend="up" trendValue={1} color="var(--danger)" />
              <KPICard title="Sobrestock" value={stats.overstock} trend="down" trendValue={2} color="var(--warning)" />
            </section>
            <div className="dashboard-grid">
              <div className="grid-main">
                <DemandChart data={chartData} skuName="Leche entera 1L" />
                <PredictionTable predictions={tableData} />
              </div>
              <div className="grid-side">
                <AlertPanel alerts={alerts} onAcknowledge={id => apiService.acknowledgeAlert(id).then(fetchData)} />
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
              <DemandChart data={chartData} skuName="Consolidado General" />
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
                <h3>Catálogo e Inventario</h3>
              </div>
              <div className="table-responsive">
                <table className="inventory-table">
                  <thead>
                    <tr>
                      <th>Código</th>
                      <th>Descripción</th>
                      <th style={{ textAlign: 'right' }}>Stock actual</th>
                      <th>Nivel</th>
                      <th style={{ textAlign: 'center' }}>Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {skus.length > 0 ? skus.map(sku => {
                      const stock = inventoryStock[sku.sku_code] || Math.floor(Math.random() * 120 + 10);
                      const { pct, color } = getStockLevel(stock, sku.sku_code);
                      const statusLabel = pct < 30 ? 'Bajo' : pct < 60 ? 'Medio' : 'Óptimo';
                      const statusClass = pct < 30 ? 'danger' : pct < 60 ? 'warning' : 'success';
                      return (
                        <tr key={sku.id}>
                          <td><strong>{sku.sku_code}</strong></td>
                          <td>{sku.description || '—'}</td>
                          <td style={{ textAlign: 'right' }}>
                            <span className={`stock-cell ${pct < 30 ? 'stock-low' : pct < 60 ? 'stock-warn' : 'stock-ok'}`}>
                              {stock} uds
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
                            <span className={`status-badge ${statusClass}`}>{statusLabel}</span>
                          </td>
                        </tr>
                      );
                    }) : (
                      <tr><td colSpan={5} className="empty-table">No hay SKUs sincronizados</td></tr>
                    )}
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
                <h3>Análisis de Tendencias</h3>
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
                  <p className="trend-stat-value" style={{ color: 'var(--text-main)' }}>{stats.skuCount || 10}</p>
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
              </div>
              <div className="alerts-page-grid">
                <AlertPanel alerts={alerts} onAcknowledge={id => apiService.acknowledgeAlert(id).then(fetchData)} />
                <div className="card reports-panel">
                  <h4>Reportes</h4>
                  <p>Descarga el listado de acciones preventivas en formato texto.</p>
                  <button className="btn-export" onClick={exportAlerts}>
                    <Download size={16} />
                    Exportar reporte
                  </button>
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
            <p className="header-subtitle">DEMAND-24 — Sistema de Predicción de Demanda</p>
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
    </div>
  );
}

export default App;
