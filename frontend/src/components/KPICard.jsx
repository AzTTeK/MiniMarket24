import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const KPICard = ({ title, value, unit, trend, trendValue, color }) => {
  const isPositive = trend === 'up';

  return (
    <div className="kpi-card">
      <p className="kpi-label">{title}</p>
      <div className="kpi-value-row">
        <span className="kpi-value" style={color ? { color } : {}}>
          {value}
        </span>
        {unit && <span className="kpi-unit">{unit}</span>}
      </div>
      {trend && trendValue !== undefined && (
        <span className={`kpi-trend ${isPositive ? 'positive' : 'negative'}`}>
          {isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
          {isPositive ? '+' : '-'}{trendValue} vs sem. anterior
        </span>
      )}
    </div>
  );
};

export default KPICard;
