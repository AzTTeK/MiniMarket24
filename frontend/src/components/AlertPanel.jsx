import React from 'react';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const AlertPanel = ({ alerts, onAcknowledge }) => {
  if (!alerts) return null;

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
    </div>
  );
};

export default AlertPanel;
