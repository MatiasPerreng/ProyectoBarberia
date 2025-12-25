const dias = [
  "", "Lunes", "Martes", "Miércoles",
  "Jueves", "Viernes", "Sábado", "Domingo"
];

const HorarioList = ({ horarios, onDelete }) => {
  return (
    <div className="admin-table">
      {horarios.map((h) => (
        <div className="admin-row" key={h.id_horario}>
          <div>
            <strong>{dias[h.dia_semana]}</strong>
            <small>
              {h.hora_desde} → {h.hora_hasta}
            </small>
            <small>
              {h.fecha_desde} / {h.fecha_hasta}
            </small>
          </div>

          <button onClick={() => onDelete(h.id_horario)}>
            Eliminar
          </button>
        </div>
      ))}
    </div>
  );
};

export default HorarioList;
