import { useState } from "react";

const diasSemana = [
  { id: 1, label: "Lunes" },
  { id: 2, label: "Martes" },
  { id: 3, label: "Miércoles" },
  { id: 4, label: "Jueves" },
  { id: 5, label: "Viernes" },
  { id: 6, label: "Sábado" },
  { id: 7, label: "Domingo" },
];

const HorarioForm = ({ idBarbero, onSubmit, onClose }) => {
  const [diaSemana, setDiaSemana] = useState(1);
  const [horaDesde, setHoraDesde] = useState("09:00");
  const [horaHasta, setHoraHasta] = useState("18:00");
  const [fechaDesde, setFechaDesde] = useState("");
  const [fechaHasta, setFechaHasta] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    onSubmit({
      id_barbero: idBarbero,
      dia_semana: diaSemana,
      hora_desde: horaDesde,
      hora_hasta: horaHasta,
      fecha_desde: fechaDesde,
      fecha_hasta: fechaHasta,
    });
  };

  return (
    <div className="admin-modal-overlay">
      <div className="admin-modal">
        <h3>Nuevo horario</h3>

        <form onSubmit={handleSubmit}>
          <select
            value={diaSemana}
            onChange={(e) => setDiaSemana(Number(e.target.value))}
          >
            {diasSemana.map((d) => (
              <option key={d.id} value={d.id}>
                {d.label}
              </option>
            ))}
          </select>

          <div className="row">
            <input
              type="time"
              value={horaDesde}
              onChange={(e) => setHoraDesde(e.target.value)}
            />
            <input
              type="time"
              value={horaHasta}
              onChange={(e) => setHoraHasta(e.target.value)}
            />
          </div>

          <div className="row">
            <input
              type="date"
              value={fechaDesde}
              onChange={(e) => setFechaDesde(e.target.value)}
              required
            />
            <input
              type="date"
              value={fechaHasta}
              onChange={(e) => setFechaHasta(e.target.value)}
              required
            />
          </div>

          <div className="modal-actions">
            <button type="submit">Guardar</button>
            <button type="button" onClick={onClose}>
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default HorarioForm;
