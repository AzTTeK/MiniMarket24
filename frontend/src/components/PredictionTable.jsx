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

      <style jsx>{`
        .table-card {
          margin-top: var(--space-lg);
          padding: 0;
          overflow: hidden;
        }

        .table-header {
          padding: var(--space-lg);
          border-bottom: 1px solid var(--border);
        }

        .table-responsive {
          overflow-x: auto;
        }

        .data-table {
          width: 100%;
          border-collapse: collapse;
          text-align: left;
        }

        .data-table th {
          background: #f8fafc;
          padding: 1rem 1.5rem;
          font-size: 0.75rem;
          font-weight: 700;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.025em;
        }

        .data-table td {
          padding: 1rem 1.5rem;
          font-size: 0.875rem;
          border-bottom: 1px solid var(--border);
        }

        .data-table tr:last-child td {
          border-bottom: none;
        }

        .product-name {
          font-weight: 600;
          color: var(--text-main);
        }

        .confidence-cell {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-weight: 500;
        }

        .conf-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
        }

        .empty-table {
          text-align: center;
          padding: 3rem !important;
          color: var(--text-muted);
        }
      `}</style>
    </div>
  );
};

export default PredictionTable;
