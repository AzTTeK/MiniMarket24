import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import KPICard from './components/KPICard';
import DemandChart from './components/DemandChart';
import AlertPanel from './components/AlertPanel';
import PredictionTable from './components/PredictionTable';
import apiService from './services/api';
import { RefreshCw, Search, Package, AlertTriangle, BarChart3, TrendingUp, Download, Loader2 } from 'lucide-react';
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

  const fetchData = async () => {
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
      
      // Mock data robusta
      const baseData = [
        { name: 'S-7', actual: 28 }, { name: 'S-6', actual: 32 }, { name: 'S-5', actual: 24 },
        { name: 'S-4', actual: 48 }, { name: 'S-3', actual: 42 }, { name: 'S-2', actual: 55 },
        { name: 'S-1', actual: 45 }, { name: 'S0', actual: 42, projected: 42 },
        { name: 'S+1', projected: 52 }, { name: 'S+2', projected: 58 }, { name: 'S+3', projected: 62 }
      ];
      setChartData(baseData.map(d => ({ ...d, range: [ (d.actual || d.projected) * 0.9, (d.actual || d.projected) * 1.1 ] })));
      setTableData([
        { product: 'Leche entera 1L', stock: 48, demand: 62, status: 'Quiebre', confidence: 'Alta' },
        { product: 'Agua 500ml', stock: 120, demand: 95, status: 'Normal', confidence: 'Alta' },
        { product: 'Pan tajado 500g', stock: 30, demand: 34, status: 'Revisar', confidence: 'Media' }
      ]);
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
      await apiService.triggerTraining();
      alert('¡IA Sincronizada con Éxito!');
      await fetchData();
    } catch (error) {
      alert('Error en sincronización: ' + (error.response?.data?.detail || 'El backend no responde.'));
    } finally {
      setTraining(false);
    }
  };

  const exportAlerts = () => {
    const text = alerts.map(a => `[${a.alert_type.toUpperCase()}] ${a.message}`).join('\n');
    const blob = new Blob([`DEMAND-24 REPORT\n${new Date().toLocaleString()}\n\n${text}`], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url; link.download = `reporte_riesgos_${new Date().getTime()}.txt`;
    link.click();
  };

  if (loading) return (
    <div className="loading-screen">
      <Loader2 className="animate-spin" size={48} color="var(--primary-600)" />
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
              <KPICard title="Precisión" value={stats.precision} unit="%" trend="up" trendValue={4} />
              <KPICard title="Quiebres" value={stats.breaks} trend="up" trendValue={1} color="var(--danger)" />
              <KPICard title="Overstock" value={stats.overstock} trend="down" trendValue={2} color="var(--warning)" />
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
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="card view-card">
            <div className="flex-header"><BarChart3 size={24} color="var(--primary-600)" /><h3>Proyecciones Detalladas</h3></div>
            <DemandChart data={chartData} skuName="Consolidado General" />
            <div style={{ marginTop: '2rem' }}><PredictionTable predictions={[...tableData, ...tableData]} /></div>
          </motion.div>
        );
      case 'inventory':
        return (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card view-card">
            <div className="flex-header"><Package size={24} color="var(--primary-600)" /><h3>Catálogo Sincronizado</h3></div>
            <table className="data-table">
              <thead><tr><th>Código</th><th>Descripción</th><th>Sincronización</th></tr></thead>
              <tbody>{skus.map(sku => (<tr key={sku.id}><td><strong>{sku.sku_code}</strong></td><td>{sku.description}</td><td><span className="badge badge-success">OK</span></td></tr>))}</tbody>
            </table>
          </motion.div>
        );
      case 'trends':
        return (
          <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="card view-card">
            <div className="flex-header"><TrendingUp size={24} color="var(--success)" /><h3>Análisis de Tendencias</h3></div>
            <div className="kpi-grid">
              <div className="glass" style={{ padding: '2rem', textAlign: 'center' }}><h4>Crecimiento</h4><p style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--success)' }}>+12.4%</p></div>
              <div className="glass" style={{ padding: '2rem', textAlign: 'center' }}><h4>Confianza</h4><p style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--primary-600)' }}>88%</p></div>
            </div>
            <div style={{ marginTop: '2rem' }}>
              <DemandChart data={chartData.map(d => ({ ...d, actual: d.actual ? d.actual * 0.8 : null, projected: d.projected ? d.projected * 1.2 : null }))} skuName="Tendencia de Mercado" />
            </div>
          </motion.div>
        );
      case 'alerts':
        return (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card view-card">
            <div className="flex-header"><AlertTriangle size={24} color="var(--danger)" /><h3>Centro de Riesgos</h3></div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2rem' }}>
              <AlertPanel alerts={alerts} onAcknowledge={id => apiService.acknowledgeAlert(id).then(fetchData)} />
              <div className="glass" style={{ padding: '1.5rem', borderRadius: '12px', height: 'fit-content' }}>
                <h4>Reportes</h4>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: '1rem 0' }}>Descarga el listado de acciones preventivas.</p>
                <button className="btn-train" style={{ width: '100%' }} onClick={exportAlerts}><Download size={18} /> Exportar (.txt)</button>
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
          <div className="header-title"><h2 style={{ textTransform: 'capitalize' }}>{activeTab} — DEMAND-24</h2></div>
          <div className="header-actions">
            <button className={`btn-train ${training ? 'loading' : ''}`} onClick={handleTrain} disabled={training}>
              {training ? <Loader2 className="animate-spin" size={18} /> : <RefreshCw size={18} />}
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
