import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { motion } from 'framer-motion';

const KPICard = ({ title, value, unit, trend, trendValue, color }) => {
  const isPositive = trend === 'up';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card kpi-card"
    >
      <p className="kpi-title">{title}</p>
      <div className="kpi-value-container">
        <span className="kpi-value">{value}</span>
        {unit && <span className="kpi-unit">{unit}</span>}
      </div>

      {trendValue && (
        <div className={`kpi-trend ${isPositive ? 'positive' : 'negative'}`}>
          {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
          <span>{isPositive ? '+' : ''}{trendValue}% vs sem. ant</span>
        </div>
      )}

    </motion.div>
  );
};

export default KPICard;
