const BarberoAgendaItem = ({ turno, onClick }) => {
  return (
    <div
      className={`barbero-agenda-item estado-${turno.estado}`}
      onClick={onClick}
    >
      <div className="hora">{turno.hora}</div>

      <div className="info">
        <strong>{turno.cliente}</strong>
        <span>{turno.servicio}</span>
      </div>

      <div className="estado">
        {turno.estado.replaceAll("_", " ")}
      </div>
    </div>
  );
};

export default BarberoAgendaItem;
