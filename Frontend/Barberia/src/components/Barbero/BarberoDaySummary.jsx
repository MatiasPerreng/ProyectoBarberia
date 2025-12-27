const BarberoDaySummary = ({ turnos }) => {
  const confirmados = turnos.filter(
    (t) => t.estado === "CONFIRMADO"
  );
  const total = confirmados.reduce(
    (acc, t) => acc + (t.precio || 0),
    0
  );

  return (
    <div className="barbero-summary">
      <div>
        <strong>Turnos hoy:</strong> {confirmados.length}
      </div>
      <div>
        <strong>Total estimado:</strong> ${total}
      </div>
    </div>
  );
};

export default BarberoDaySummary;
