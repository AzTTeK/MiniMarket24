import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  ComposedChart,
  ReferenceLine,
  Legend
} from 'recharts';

const DemandChart = ({ data, skuName }) => {
  // Custom Tooltip for premium feel
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip card glass">
          <p className="tooltip-label">{label}</p>
          {payload.map((entry, index) => (
            <div key={index} className="tooltip-item" style={{ color: entry.color }}>
              <span className="dot" style={{ backgroundColor: entry.color }}></span>
              <span>
                {entry.name}: {
                  Array.isArray(entry.value) 
                    ? `${entry.value[0].toFixed(1)} - ${entry.value[1].toFixed(1)}`
                    : (typeof entry.value === 'number' ? entry.value.toFixed(1) : '0.0')
                } uds
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  if (!data || data.length === 0) {
    return (
      <div className="card chart-card flex-center" style={{ height: '300px' }}>
        <p className="text-muted">No hay datos suficientes para generar la gráfica.</p>
      </div>
    );
  }

  return (
    <div className="card chart-card">
      <div className="chart-header">
        <h3>Demanda histórica vs proyectada</h3>
        <div className="chart-sku-selector glass">
          <span>SKU: </span>
          <span className="sku-selected">{skuName || 'Todos los SKUs'}</span>
        </div>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorArea" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.1} />
                <stop offset="95%" stopColor="#4f46e5" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis
              dataKey="name"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748b', fontSize: 12 }}
              dy={10}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748b', fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />

            {/* Confidence Interval Area */}
            <Area
              type="monotone"
              dataKey="range"
              stroke="none"
              fill="var(--primary-100)"
              fillOpacity={0.4}
              name="Intervalo Confianza 90%"
            />

            {/* Historical Line */}
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#4f46e5"
              strokeWidth={3}
              dot={{ r: 4, fill: '#4f46e5', strokeWidth: 2, stroke: '#fff' }}
              activeDot={{ r: 6 }}
              name="Ventas reales"
            />

            {/* Projection Line (Dashed) */}
            <Line
              type="monotone"
              dataKey="projected"
              stroke="#4f46e5"
              strokeWidth={3}
              strokeDasharray="5 5"
              dot={{ r: 4, fill: '#fff', strokeWidth: 2, stroke: '#4f46e5' }}
              name="Proyección"
            />

            <ReferenceLine x="S0" stroke="#94a3b8" strokeDasharray="3 3" label={{ position: 'top', value: 'Hoy', fill: '#94a3b8', fontSize: 12 }} />
            <Legend verticalAlign="bottom" height={36} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
};

export default DemandChart;
