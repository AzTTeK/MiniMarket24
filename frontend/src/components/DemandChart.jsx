import React from 'react';
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

const DemandChart = ({ data, skuName }) => {
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{label}</p>
          {payload.map((entry, index) => {
            if (entry.dataKey === 'range') return null;
            return (
              <div key={index} className="tooltip-item" style={{ color: entry.color }}>
                <span className="dot" style={{ backgroundColor: entry.color }}></span>
                <span>
                  {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(1) : '—'} uds
                </span>
              </div>
            );
          })}
        </div>
      );
    }
    return null;
  };

  if (!data || data.length === 0) {
    return (
      <div className="card chart-card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '280px' }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Sin datos para graficar</p>
      </div>
    );
  }

  return (
    <div className="card chart-card">
      <div className="chart-header">
        <h3>Demanda — Histórica vs Proyectada</h3>
        <div className="chart-sku-selector">
          SKU: <span className="sku-selected">{skuName || 'Todos'}</span>
        </div>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height={260}>
          <ComposedChart data={data} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="ciGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#6366f1" stopOpacity={0.12} />
                <stop offset="100%" stopColor="#6366f1" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis
              dataKey="name"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#94a3b8', fontSize: 11, fontWeight: 500 }}
              dy={8}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              width={40}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine
              x="S0"
              stroke="#cbd5e1"
              strokeDasharray="4 4"
              label={{ position: 'top', value: 'Hoy', fill: '#94a3b8', fontSize: 11, fontWeight: 600 }}
            />
            <Area
              type="monotone"
              dataKey="range"
              stroke="none"
              fill="url(#ciGradient)"
              name="IC 90%"
            />
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#6366f1"
              strokeWidth={2.5}
              dot={{ r: 3.5, fill: '#6366f1', strokeWidth: 2, stroke: '#fff' }}
              activeDot={{ r: 5, stroke: '#6366f1', strokeWidth: 2 }}
              name="Ventas reales"
              connectNulls={false}
            />
            <Line
              type="monotone"
              dataKey="projected"
              stroke="#6366f1"
              strokeWidth={2.5}
              strokeDasharray="6 4"
              dot={{ r: 3.5, fill: '#fff', strokeWidth: 2, stroke: '#6366f1' }}
              name="Proyección"
              connectNulls={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-legend">
        <div className="chart-legend-item">
          <span className="chart-legend-line" style={{ background: '#6366f1' }}></span>
          Ventas reales
        </div>
        <div className="chart-legend-item">
          <span className="chart-legend-line dashed"></span>
          Proyección IA
        </div>
        <div className="chart-legend-item">
          <span className="chart-legend-line" style={{ background: 'rgba(99,102,241,0.15)', height: '8px' }}></span>
          Intervalo confianza 90%
        </div>
      </div>
    </div>
  );
};

export default DemandChart;
