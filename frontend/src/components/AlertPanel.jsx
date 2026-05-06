import React from 'react';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const AlertPanel = ({ alerts, onAcknowledge }) => {
  return (
    <div className="card alert-panel">
      <div className="panel-header">
        <h3>Alertas activas</h3>
        <span className="alert-count">{alerts.length}</span>
      </div>

      <div className="alert-list">
        <AnimatePresence>
          {alerts.length === 0 ? (
            <div className="empty-alerts">
              <CheckCircle2 size={48} color="var(--success)" />
              <p>No hay alertas activas</p>
            </div>
          ) : (
            alerts.map((alert) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className={`alert-item ${alert.alert_type}`}
              >
                <div className="alert-content">
                  <div className="alert-main">
                    <div className="status-dot"></div>
                    <p className="alert-message">{alert.message}</p>
                  </div>
                  <button
                    className="ack-button"
                    onClick={() => onAcknowledge(alert.id)}
                    title="Marcar como leída"
                  >
                    <CheckCircle2 size={18} />
                  </button>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      <style jsx>{`
        .alert-panel {
          height: 100%;
          display: flex;
          flex-direction: column;
        }

        .panel-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--space-lg);
        }

        .alert-count {
          background: var(--danger-bg);
          color: var(--danger);
          padding: 0.1rem 0.6rem;
          border-radius: 999px;
          font-size: 0.75rem;
          font-weight: 700;
        }

        .alert-list {
          display: flex;
          flex-direction: column;
          gap: var(--space-md);
          overflow-y: auto;
          flex: 1;
        }

        .alert-item {
          padding: 1rem;
          border-radius: 10px;
          border-left: 4px solid transparent;
          transition: all 0.2s;
        }

        .alert-item.stock_break {
          background: #fff5f5;
          border-left-color: var(--danger);
        }

        .alert-item.low_confidence {
          background: #fffbeb;
          border-left-color: var(--warning);
        }

        .alert-content {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 0.75rem;
        }

        .alert-main {
          display: flex;
          gap: 0.75rem;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          margin-top: 0.4rem;
          flex-shrink: 0;
        }

        .stock_break .status-dot { background: var(--danger); }
        .low_confidence .status-dot { background: var(--warning); }

        .alert-message {
          font-size: 0.85rem;
          font-weight: 500;
          line-height: 1.4;
          color: var(--text-main);
        }

        .ack-button {
          background: transparent;
          border: none;
          color: #cbd5e1;
          cursor: pointer;
          transition: color 0.2s;
          padding: 0;
        }

        .ack-button:hover {
          color: var(--success);
        }

        .empty-alerts {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          gap: 1rem;
          color: var(--text-muted);
          font-size: 0.875rem;
          padding: 2rem 0;
        }
      `}</style>
    </div>
  );
};

export default AlertPanel;
