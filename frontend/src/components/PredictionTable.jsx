import React from 'react';
import { Package } from 'lucide-react';

const PredictionTable = ({ predictions }) => {
  if (!predictions || predictions.length === 0) {
    return (
      <div className="card table-card">
        <div className="table-header">
          <h3>Resumen de Predicciones</h3>
        </div>
        <table className="data-table">
          <tbody>
            <tr><td className="empty-table" colSpan={5}>Sin predicciones disponibles</td></tr>
          </tbody>
        </table>
      </div>
    );
  }

  const getStatusBadge = (status) => {
    const map = {
      'Quiebre': 'danger',
      'Normal': 'success',
      'Revisar': 'warning',
    };
    return map[status] || 'info';
  };

  const getConfColor = (conf) => {
    if (conf === 'Alta') return 'var(--success)';
    if (conf === 'Media') return 'var(--warning)';
    return 'var(--danger)';
  };

  return (
    <div className="card table-card">
      <div className="table-header">
        <h3>Resumen de Predicciones</h3>
      </div>
      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th>Producto</th>
              <th style={{ textAlign: 'right' }}>Stock actual</th>
              <th style={{ textAlign: 'right' }}>Demanda est.</th>
              <th style={{ textAlign: 'center' }}>Estado</th>
              <th>Confianza</th>
            </tr>
          </thead>
          <tbody>
            {predictions.map((p, idx) => (
              <tr key={idx}>
                <td className="product-name">{p.product}</td>
                <td style={{ textAlign: 'right' }}>
                  <span className={`stock-cell ${p.stock < p.demand ? 'stock-low' : 'stock-ok'}`}>
                    {p.stock} uds
                  </span>
                </td>
                <td style={{ textAlign: 'right', fontVariantNumeric: 'tabular-nums', fontWeight: 500 }}>
                  {p.demand} uds
                </td>
                <td style={{ textAlign: 'center' }}>
                  <span className={`status-badge ${getStatusBadge(p.status)}`}>{p.status}</span>
                </td>
                <td>
                  <div className="confidence-cell">
                    <span className="conf-dot" style={{ backgroundColor: getConfColor(p.confidence) }}></span>
                    {p.confidence}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PredictionTable;
