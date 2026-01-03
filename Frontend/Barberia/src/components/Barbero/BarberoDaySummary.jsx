

const BarberoDaySummary = ({ turnos, fecha, onChangeFecha }) => {
  const turnosValidos = turnos.filter(
    (t) => t.estado !== "cancelado"
  );

  const total = turnosValidos.reduce(
    (acc, t) => acc + (t.precio || 0),
    0
  );

  return (
    <div className="barbero-summary">
      <div className="barbero-summary-info">
        <div className="summary-item">
          <span className="summary-label">Turnos</span>
          <span className="summary-value">
            {turnosValidos.length}
          </span>
        </div>

        <div className="summary-item">
          <span className="summary-label">
            Total estimado
          </span>
          <span className="summary-value highlight">
            ${total}
          </span>
        </div>
      </div>

      <div className="summary-date-wrapper">
        <label>Fecha</label>
        <input
          type="date"
          className="barbero-summary-date"
          value={fecha}
          onChange={(e) => onChangeFecha(e.target.value)}
        />
      </div>
    </div>
  );
};

export default BarberoDaySummary;
