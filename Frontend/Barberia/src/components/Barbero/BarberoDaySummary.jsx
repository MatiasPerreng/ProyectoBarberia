import './BarberoDaySummary.css'

const BarberoDaySummary = ({ turnos, fecha, onChangeFecha }) => {
  const confirmados = turnos.filter(
    (t) => t.estado === "CONFIRMADO"
  );

  const total = confirmados.reduce(
    (acc, t) => acc + (t.precio || 0),
    0
  );

  return (
    <div className="barbero-summary">
      <div className="barbero-summary-info">
        <div>
          <strong>Turnos hoy:</strong> {confirmados.length}
        </div>
        <div>
          <strong>Total estimado:</strong> ${total}
        </div>
      </div>

      {/* 🔥 FILTRO POR DÍA */}
      <input
        type="date"
        className="barbero-summary-date"
        value={fecha}
        onChange={(e) => onChangeFecha(e.target.value)}
      />
    </div>
  );
};

export default BarberoDaySummary;