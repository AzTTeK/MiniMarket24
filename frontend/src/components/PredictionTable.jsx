import React from 'react';

const PredictionTable = ({ predictions }) => {
  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'quiebre': return <span className="badge badge-danger">Quiebre</span>;
      case 'normal': return <span className="badge badge-success">Normal</span>;
      case 'revisar': return <span className="badge badge-warning">Revisar</span>;
      default: return <span className="badge">{status}</span>;
    }
  };

  const getConfidenceColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'alta': return 'var(--success)';
      case 'media': return 'var(--warning)';
      case 'baja': return 'var(--danger)';
      default: return 'var(--text-muted)';
    }
  };

  if (!predictions) return null;

  return (
    <div className="card table-card">
      <div className="table-header">
        <h3>Predicciones por producto — próxima semana</h3>
      </div>

      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th>Producto</th>
              <th>Stock actual</th>
              <th>Demanda proyectada</th>
              <th>Estado</th>
              <th>Confianza</th>
            </tr>
          </thead>
          <tbody>
            {predictions.length === 0 ? (
              <tr>
                <td colSpan="5" className="empty-table">No hay datos disponibles</td>
              </tr>
            ) : (
              predictions.map((item, index) => (
                <tr key={index}>
                  <td className="product-name">{item.product}</td>
                  <td>{item.stock} uds</td>
                  <td>{item.demand} uds</td>
                  <td>{getStatusBadge(item.status)}</td>
                  <td>
                    <div className="confidence-cell">
                      <span className="conf-dot" style={{ background: getConfidenceColor(item.confidence) }}></span>
                      {item.confidence}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PredictionTable;
