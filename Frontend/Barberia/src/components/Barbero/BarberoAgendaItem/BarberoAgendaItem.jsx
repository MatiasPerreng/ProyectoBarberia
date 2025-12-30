
import getDiaTexto from '../../../../utils/date'

const BarberoAgendaItem = ({ turno, onClick }) => {
  const diaTexto = getDiaTexto(turno.fechaHora);

  return (
    <div
      className={`barbero-agenda-item estado-${turno.estado}`}
      onClick={onClick}
    >
      {/* HORA */}
      <div className="hora">{turno.hora}</div>

      {/* INFO */}
      <div className="info">
        <p className="frase">
          <strong>{diaTexto}</strong> tenés{" "}
          <strong>{turno.servicio}</strong>{" "}
          con{" "}
          <strong>
            {turno.cliente_nombre} {turno.cliente_apellido}
          </strong>
        </p>

        <span>
          ⏱ {turno.duracion} min
          {turno.telefono && ` · 📞 ${turno.telefono}`}
        </span>
      </div>

      {/* ESTADO */}
      <span className="estado">{turno.estado}</span>
    </div>
  );
};

export default BarberoAgendaItem;
