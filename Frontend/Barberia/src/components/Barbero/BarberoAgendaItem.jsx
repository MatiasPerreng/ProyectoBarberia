const BarberoAgendaItem = ({ turno, onClick }) => {
  const nombreCompleto = [
    turno.cliente_nombre,
    turno.cliente_apellido,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div
      className={`barbero-agenda-item estado-${turno.estado}`}
      onClick={onClick}
    >
      <div className="hora">{turno.hora}</div>

      <div className="info">
        <strong className="cliente-nombre">
          {nombreCompleto || "Cliente"}
        </strong>
        <span className="servicio">
          {turno.servicio}
        </span>
      </div>

      <div className="estado">
        {turno.estado.replaceAll("_", " ")}
      </div>
    </div>
  );
};

export default BarberoAgendaItem;
