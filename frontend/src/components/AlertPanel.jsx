import React from 'react';
import { Bell, CheckCircle, ShieldAlert } from 'lucide-react';

const AlertPanel = ({ alerts, onAcknowledge }) => {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="card alert-panel-card">
        <div className="panel-header">
          <h3>Alertas</h3>
        </div>
        <div className="empty-alerts">
          <ShieldAlert size={36} strokeWidth={1.5} />
          <p>Sin alertas activas</p>
          <p style={{ fontSize: '0.75rem' }}>El sistema está operando con normalidad</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card alert-panel-card">
      <div className="panel-header">
        <h3>Alertas</h3>
        <span className="alert-count">{alerts.length}</span>
      </div>
      <div className="alert-list">
        {alerts.map((alert) => (
          <div key={alert.id} className={`alert-item ${alert.alert_type || ''}`}>
            <div className="alert-content">
              <div className="alert-main">
                <span className="status-dot"></span>
                <p className="alert-message">{alert.message || 'Alerta sin detalle'}</p>
              </div>
              {onAcknowledge && (
                <button
                  className="ack-button"
                  onClick={() => onAcknowledge(alert.id)}
                  title="Marcar como atendida"
                >
                  <CheckCircle size={16} />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AlertPanel;
