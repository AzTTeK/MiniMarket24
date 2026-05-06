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

      <style jsx>{`
        .kpi-card {
          flex: 1;
          min-width: 200px;
        }

        .kpi-title {
          font-size: 0.8rem;
          color: var(--text-muted);
          font-weight: 500;
          margin-bottom: 0.5rem;
        }

        .kpi-value-container {
          display: flex;
          align-items: baseline;
          gap: 0.25rem;
          margin-bottom: 0.75rem;
        }

        .kpi-value {
          font-size: 2rem;
          font-weight: 700;
          color: var(--text-main);
        }

        .kpi-unit {
          font-size: 0.875rem;
          color: var(--text-muted);
          font-weight: 500;
        }

        .kpi-trend {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.75rem;
          font-weight: 600;
        }

        .kpi-trend.positive {
          color: var(--success);
        }

        .kpi-trend.negative {
          color: var(--danger);
        }
      `}</style>
    </motion.div>
  );
};

export default KPICard;
